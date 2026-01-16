<?php
/**
 * EPG Fetcher + Repacker
 * Source: epgshare01 IN4
 * Output: epg.xml.gz
 */

date_default_timezone_set("UTC");

$sourceUrl = "https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz";
$outGz = "epg.xml.gz";

function downloadFile($url, $dest)
{
    $fp = fopen($dest, "w");
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_FILE => $fp,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 120,
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_SSL_VERIFYPEER => false,
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

function streamGzCopy($srcGz, $dstGz)
{
    // just repack to standard gzip level 9 (also validates)
    $in = gzopen($srcGz, "rb");
    if (!$in) die("Cannot open $srcGz\n");

    $out = gzopen($dstGz, "wb9");
    if (!$out) die("Cannot write $dstGz\n");

    while (!gzeof($in)) {
        $buf = gzread($in, 1024 * 1024);
        if ($buf !== false && $buf !== "") gzwrite($out, $buf);
    }

    gzclose($in);
    gzclose($out);
}

echo "Downloading source EPG...\n";
$tmp = "source.xml.gz";
@unlink($tmp);
@unlink($outGz);

if (!downloadFile($sourceUrl, $tmp)) {
    die("Download failed\n");
}

// If you want to keep EXACT ids/display-names: just re-pack as output
echo "Repacking...\n";
streamGzCopy($tmp, $outGz);

echo "DONE ✅ Output: $outGz (" . round(filesize($outGz) / 1024 / 1024, 2) . " MB)\n";
