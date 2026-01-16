<?php
date_default_timezone_set("UTC");

/* ---------------- CONFIG ---------------- */
$sourceUrl = "https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz";
$outFile = "epg.xml.gz";

/* ---------------- HELPERS ---------------- */

function downloadFile($url, $dest)
{
    $fp = fopen($dest, "w");
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_FILE => $fp,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 180,
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_USERAGENT => "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    ]);
    $ok = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    if ($ok === false) echo "cURL error: " . curl_error($ch) . "\n";
    curl_close($ch);
    fclose($fp);

    echo "Download status: $code\n";
    return $code === 200;
}

function xmlEscape($str)
{
    return htmlspecialchars((string)$str, ENT_QUOTES | ENT_XML1, "UTF-8");
}

/* ---------------- MAIN ---------------- */

$tmpGz = "source.xml.gz";
$tmpXml = "source.xml";

@unlink($tmpGz);
@unlink($tmpXml);
@unlink($outFile);

echo "Downloading source...\n";
if (!downloadFile($sourceUrl, $tmpGz)) {
    die("Download failed\n");
}

echo "Extracting...\n";
$in = gzopen($tmpGz, "rb");
$out = fopen($tmpXml, "wb");
while (!gzeof($in)) {
    fwrite($out, gzread($in, 1024 * 1024));
}
gzclose($in);
fclose($out);

echo "Parsing channels (building map)...\n";

/**
 * STEP 1: Read channels and build mapping:
 * oldId => displayName
 */
$map = [];

$reader = new XMLReader();
$reader->open($tmpXml);

while ($reader->read()) {
    if ($reader->nodeType === XMLReader::ELEMENT && $reader->name === "channel") {
        $oldId = $reader->getAttribute("id");

        $channelNode = $reader->expand();
        $sx = simplexml_import_dom($channelNode);

        // Take first display-name (en preferred)
        $display = "";
        foreach ($sx->{'display-name'} as $dn) {
            $display = trim((string)$dn);
            if ($display !== "") break;
        }

        if ($oldId && $display) {
            $map[$oldId] = $display;
        }
    }
}
$reader->close();

echo "Mapped channels: " . count($map) . "\n";

echo "Rewriting XML -> output gzip...\n";

/**
 * STEP 2: Stream rewrite into gz:
 * - rewrite <channel id="old"> -> id="display"
 * - rewrite <programme channel="old"> -> channel="display"
 * - display-name stays same
 */
$in = fopen($tmpXml, "rb");
$gz = gzopen($outFile, "wb9");

while (!feof($in)) {
    $chunk = fread($in, 1024 * 1024);

    // Replace channel id="OLD"
    $chunk = preg_replace_callback('/<channel id="([^"]+)">/', function ($m) use ($map) {
        $old = $m[1];
        $new = $map[$old] ?? $old;
        return '<channel id="' . xmlEscape($new) . '">';
    }, $chunk);

    // Replace programme channel="OLD"
    $chunk = preg_replace_callback('/<programme([^>]+)channel="([^"]+)"([^>]*)>/', function ($m) use ($map) {
        $before = $m[1];
        $old = $m[2];
        $after = $m[3];
        $new = $map[$old] ?? $old;
        return '<programme' . $before . 'channel="' . xmlEscape($new) . '"' . $after . '>';
    }, $chunk);

    gzwrite($gz, $chunk);
}

fclose($in);
gzclose($gz);

echo "DONE ✅ Output: $outFile (" . round(filesize($outFile) / 1024 / 1024, 2) . " MB)\n";
