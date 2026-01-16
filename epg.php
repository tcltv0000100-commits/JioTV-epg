<?php
date_default_timezone_set("UTC");

$sourceUrl = "https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz";
$outFile   = "epg.xml.gz";

function downloadFile($url, $dest)
{
    $fp = fopen($dest, "w");
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_FILE => $fp,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 300,
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

$tmpGz  = "source.xml.gz";
$tmpXml = "source.xml";

@unlink($tmpGz);
@unlink($tmpXml);
@unlink($outFile);

echo "Downloading...\n";
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

/**
 * STEP 1: Build map oldId => display-name
 */
echo "Building channel-id map...\n";
$map = [];

$r = new XMLReader();
$r->open($tmpXml);

while ($r->read()) {
    if ($r->nodeType === XMLReader::ELEMENT && $r->name === "channel") {
        $oldId = $r->getAttribute("id");
        $display = "";

        // read inside <channel> ... </channel>
        while ($r->read()) {
            // <display-name>
            if ($r->nodeType === XMLReader::ELEMENT && $r->name === "display-name") {
                $display = trim($r->readString());
                break;
            }
            // end channel
            if ($r->nodeType === XMLReader::END_ELEMENT && $r->name === "channel") {
                break;
            }
        }

        if ($oldId && $display) {
            $map[$oldId] = $display;
        }
    }
}
$r->close();

echo "Mapped channels: " . count($map) . "\n";
if (count($map) == 0) {
    die("ERROR: channel map empty (source xml issue?)\n");
}

/**
 * STEP 2: Rewrite source xml -> output gzip
 * - <channel id="OLD"> becomes <channel id="DISPLAY">
 * - <programme channel="OLD"> becomes <programme channel="DISPLAY">
 */
echo "Rewriting output gzip...\n";
$in = fopen($tmpXml, "rb");
$gz = gzopen($outFile, "wb9");

while (!feof($in)) {
    $chunk = fread($in, 1024 * 1024);

    // replace channel id
    $chunk = preg_replace_callback('/<channel id="([^"]+)">/', function ($m) use ($map) {
        $old = $m[1];
        $new = $map[$old] ?? $old;
        return '<channel id="' . xmlEscape($new) . '">';
    }, $chunk);

    // replace programme channel
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

echo "DONE ✅ Output: $outFile (" . round(filesize($outFile)/1024/1024, 2) . " MB)\n";
