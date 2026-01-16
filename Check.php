<?php
date_default_timezone_set("UTC");

/* ---------------- CONFIG ---------------- */
$prevEpgDayCount = 7;
$nextEpgDayCount = 2;
$langId = 6;
$parallelRequests = 12; // increase for more speed (10–15 safe)

/* ---------------- CURL HELPERS ---------------- */

function curlHandle($url)
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_HTTPHEADER => [
            "User-Agent: okhttp/4.9.0",
            "Accept: application/json"
        ]
    ]);
    return $ch;
}

function xmlEscape($str)
{
    return htmlspecialchars((string)$str, ENT_QUOTES | ENT_XML1, 'UTF-8');
}

function formatEpoch($epochMs)
{
    return gmdate("YmdHis", intval($epochMs / 1000)) . " +0000";
}

/* ---------------- CHANNELS ---------------- */

function getChannels()
{
    $url = "https://jiotv.data.cdn.jio.com/apis/v1.4/getMobileChannelList/get/?os=android&devicetype=phone";
    $ch = curlHandle($url);
    $res = curl_exec($ch);
    curl_close($ch);

    if (!$res) return [];
    $json = json_decode($res, true);
    return $json["result"] ?? [];
}

function writeEpgChannel($ch, $fp)
{
    fwrite($fp,
        "\t<channel id=\"{$ch['channel_id']}\">\n" .
        "\t\t<display-name>" . xmlEscape($ch['channel_name']) . "</display-name>\n" .
        "\t\t<icon src=\"https://jiotv.catchup.cdn.jio.com/dare_images/images/{$ch['logoUrl']}\" />\n" .
        "\t</channel>\n"
    );
}

/* ---------------- PROGRAM WRITE ---------------- */

function writeEpgProgram($cid, $epg, $fp)
{
    $start = formatEpoch($epg["startEpoch"] ?? 0);
    $end   = formatEpoch($epg["endEpoch"] ?? 0);

    fwrite($fp, "\t<programme start=\"$start\" stop=\"$end\" channel=\"$cid\">\n");
    fwrite($fp, "\t\t<title lang=\"en\">" . xmlEscape($epg["showname"] ?? "") . "</title>\n");
    fwrite($fp, "\t\t<desc lang=\"en\">" . xmlEscape($epg["episode_desc"] ?? $epg["description"] ?? "") . "</desc>\n");

    if (!empty($epg["showCategory"])) {
        fwrite($fp, "\t\t<category lang=\"en\">" . xmlEscape($epg["showCategory"]) . "</category>\n");
    }

    if (!empty($epg["episode_num"])) {
        fwrite($fp, "\t\t<episode-num system=\"onscreen\">" . xmlEscape($epg["episode_num"]) . "</episode-num>\n");
    }

    if (!empty($epg["episodePoster"])) {
        fwrite($fp, "\t\t<icon src=\"https://jiotv.catchup.cdn.jio.com/dare_images/shows/{$epg['episodePoster']}\" />\n");
    }

    fwrite($fp, "\t</programme>\n");
}

/* ---------------- PARALLEL EPG FETCH ---------------- */

function fetchEpgParallel($requests)
{
    $mh = curl_multi_init();
    $handles = [];

    foreach ($requests as $key => $url) {
        $ch = curlHandle($url);
        curl_multi_add_handle($mh, $ch);
        $handles[$key] = $ch;
    }

    do {
        curl_multi_exec($mh, $running);
        curl_multi_select($mh);
    } while ($running);

    $results = [];
    foreach ($handles as $key => $ch) {
        $results[$key] = curl_multi_getcontent($ch);
        curl_multi_remove_handle($mh, $ch);
        curl_close($ch);
    }

    curl_multi_close($mh);
    return $results;
}

/* ---------------- MAIN ---------------- */

@unlink("epg.xml");
@unlink("jio.gz");

echo "Fetching channels...\n";
$channels = getChannels();
if (!$channels) die("No channels found\n");

$fp = fopen("epg.xml", "w");

fwrite($fp, "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n");
fwrite($fp, "<!DOCTYPE tv SYSTEM \"xmltv.dtd\">\n");
fwrite($fp, "<tv generator-info-name=\"Arnab Ghosh\">\n");

/* channels */
foreach ($channels as $ch) {
    writeEpgChannel($ch, $fp);
}

/* programs */
for ($day = -$prevEpgDayCount; $day < $nextEpgDayCount; $day++) {
    echo "Day $day\n";

    $queue = [];
    foreach ($channels as $ch) {
        $queue[] = [
            "cid" => $ch["channel_id"],
            "url" => "https://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get?channel_id={$ch['channel_id']}&offset=$day&langId=$langId"
        ];
    }

    $chunks = array_chunk($queue, $parallelRequests);
    foreach ($chunks as $batch) {
        $req = [];
        foreach ($batch as $i => $b) $req[$i] = $b["url"];

        $responses = fetchEpgParallel($req);

        foreach ($responses as $i => $res) {
            $json = json_decode($res, true);
            if (empty($json["epg"])) continue;

            foreach ($json["epg"] as $epg) {
                writeEpgProgram($batch[$i]["cid"], $epg, $fp);
            }
        }
    }
}

fwrite($fp, "</tv>\n");
fclose($fp);

/* gzip */
file_put_contents("jio.gz", gzencode(file_get_contents("epg.xml"), 9));

echo "DONE ✅ Output: jio.gz\n";
