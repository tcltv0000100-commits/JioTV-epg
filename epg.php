<?php
date_default_timezone_set("UTC");

/**
 * CONFIG
 */
$prevEpgDayCount = 7;
$nextEpgDayCount = 2;
$langId = 6;

// Output name required by you
$outputGz = "jio.gz";

/**
 * HTTP GET using cURL
 */
function httpGet($url)
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_HTTPHEADER => [
            // realistic browser UA improves success
            "User-Agent: Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
            "Accept: application/json, text/plain, */*",
            "Accept-Language: en-US,en;q=0.9",
            "Connection: keep-alive",
        ],
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if ($response === false) {
        echo "cURL error: " . curl_error($ch) . "\n";
    }

    curl_close($ch);
    return [$httpCode, $response];
}

/**
 * XML escape
 */
function xmlEscape($str)
{
    if ($str === null) return "";
    return htmlspecialchars((string)$str, ENT_QUOTES | ENT_XML1, "UTF-8");
}

function formatEpoch($epochMs)
{
    $ts = intval($epochMs / 1000);
    return gmdate("YmdHis", $ts) . " +0000";
}

/**
 * Fetch channel list
 */
function getChannels()
{
    $url = "https://jiotv.data.cdn.jio.com/apis/v1.4/getMobileChannelList/get/?os=android&devicetype=phone";
    [$code, $res] = httpGet($url);

    echo "Channel API status: $code\n";
    if (!$res) return [];

    $json = json_decode($res, true);
    if (!is_array($json)) {
        echo "Channel API invalid JSON response (maybe blocked)\n";
        echo "Sample: " . substr($res, 0, 200) . "\n";
        return [];
    }

    return $json["result"] ?? [];
}

/**
 * Fetch EPG
 */
function getEpg($channelId, $offset, $langId)
{
    $url = "https://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get?channel_id=" .
        urlencode($channelId) . "&offset=" . urlencode($offset) . "&langId=" . urlencode($langId);

    [$code, $res] = httpGet($url);

    if ($code != 200 || !$res) return [];

    $json = json_decode($res, true);
    if (!is_array($json)) return [];

    return $json["epg"] ?? [];
}

/**
 * Write channels XML
 */
function writeChannelsXml($channels, $file)
{
    $fp = fopen($file, "w");
    foreach ($channels as $c) {
        $id = $c["channel_id"] ?? null;
        $name = $c["channel_name"] ?? null;
        $logo = $c["logoUrl"] ?? "";

        if ($id === null || $name === null) continue;

        fwrite($fp, "\t<channel id=\"" . $id . "\">\n");
        fwrite($fp, "\t\t<display-name>" . xmlEscape($name) . "</display-name>\n");
        fwrite($fp, "\t\t<icon src=\"https://jiotv.catchup.cdn.jio.com/dare_images/images/" . xmlEscape($logo) . "\"></icon>\n");
        fwrite($fp, "\t</channel>\n");
    }
    fclose($fp);
}

/**
 * Write programmes into programX.xml
 */
function writeProgramXmlForDay($day, $channels, $langId)
{
    echo "Generating program$day.xml\n";
    $fp = fopen("program$day.xml", "w");

    $i = 0;
    $total = count($channels);

    foreach ($channels as $c) {
        $cid = $c["channel_id"] ?? null;
        if (!$cid) continue;

        $epgData = getEpg($cid, $day, $langId);

        foreach ($epgData as $epg) {
            $progStart = formatEpoch($epg["startEpoch"] ?? 0);
            $progEnd = formatEpoch($epg["endEpoch"] ?? 0);
            $title = xmlEscape($epg["showname"] ?? "");

            $desc = $epg["episode_desc"] ?? ($epg["description"] ?? "");
            $desc = xmlEscape($desc);

            $category = xmlEscape($epg["showCategory"] ?? "");
            $episodeNum = $epg["episode_num"] ?? "";
            $poster = $epg["episodePoster"] ?? "";

            fwrite($fp, "\t<programme start=\"$progStart\" stop=\"$progEnd\" channel=\"$cid\">\n");
            fwrite($fp, "\t\t<title lang=\"en\">$title</title>\n");
            fwrite($fp, "\t\t<desc lang=\"en\">$desc</desc>\n");

            if (!empty($category)) {
                fwrite($fp, "\t\t<category lang=\"en\">$category</category>\n");
            }
            if (!empty($episodeNum)) {
                fwrite($fp, "\t\t<episode-num system=\"onscreen\">" . xmlEscape((string)$episodeNum) . "</episode-num>\n");
            }
            if (!empty($poster)) {
                fwrite($fp, "\t\t<icon src=\"https://jiotv.catchup.cdn.jio.com/dare_images/shows/" . xmlEscape($poster) . "\"></icon>\n");
            }

            fwrite($fp, "\t</programme>\n");
        }

        $i++;
        if ($i % 50 == 0) echo "Progress: $i/$total\n";
    }

    fclose($fp);
}

/**
 * Merge XML into gzip directly (no RAM blow)
 */
function buildGzEpg($outputGz, $channelsFile, $prevEpgDayCount, $nextEpgDayCount)
{
    // header/footer temp files
    $header = "tv_header.xml";
    $footer = "tv_footer.xml";

    file_put_contents($header,
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" .
        "<!DOCTYPE tv SYSTEM \"xmltv.dtd\">\n" .
        "<tv generator-info-name=\"JioTV-EPG\" generator-info-url=\"https://github.com/\">\n"
    );
    file_put_contents($footer, "</tv>\n");

    // write gz
    $gz = gzopen($outputGz, "w9");
    if (!$gz) {
        echo "ERROR: can't create $outputGz\n";
        return false;
    }

    foreach ([$header, $channelsFile] as $f) {
        $fp = fopen($f, "r");
        while (!feof($fp)) {
            $chunk = fread($fp, 1024 * 1024);
            if ($chunk !== false && $chunk !== "") gzwrite($gz, $chunk);
        }
        fclose($fp);
    }

    for ($day = ($prevEpgDayCount * -1); $day < $nextEpgDayCount; $day++) {
        $file = "program$day.xml";
        if (!file_exists($file)) continue;

        $fp = fopen($file, "r");
        while (!feof($fp)) {
            $chunk = fread($fp, 1024 * 1024);
            if ($chunk !== false && $chunk !== "") gzwrite($gz, $chunk);
        }
        fclose($fp);
    }

    // footer
    $fp = fopen($footer, "r");
    while (!feof($fp)) {
        $chunk = fread($fp, 1024 * 1024);
        if ($chunk !== false && $chunk !== "") gzwrite($gz, $chunk);
    }
    fclose($fp);

    gzclose($gz);

    @unlink($header);
    @unlink($footer);

    echo "Created: $outputGz (" . round(filesize($outputGz) / 1024 / 1024, 2) . " MB)\n";
    return true;
}

/**
 * MAIN
 */
echo "Fetching channels...\n";
$channels = getChannels();

if (count($channels) == 0) {
    echo "No channels found. (Jio API blocked on this IP?)\n";
    exit(1);
}

echo "Channels: " . count($channels) . "\n";

// clean old
@unlink("channels.xml");
@unlink($outputGz);

// write channel xml
writeChannelsXml($channels, "channels.xml");

// generate days
for ($day = ($prevEpgDayCount * -1); $day < $nextEpgDayCount; $day++) {
    writeProgramXmlForDay($day, $channels, $langId);
}

// build gz final
buildGzEpg($outputGz, "channels.xml", $prevEpgDayCount, $nextEpgDayCount);

echo "DONE\n";
