<?php
final class ZipController extends PhabricatorController {
  public function handleRequest(AphrontRequest $request) {
    $file = explode('/', $request->getRequestURI())[1];
    $full = '/var/opt/phabricator/git/' . $file;
    if (!file_exists($full)) {
        return new Aphront404Response();
    }
    $tmp = tempnam("/tmp", "repo-");
    $zip = new ZipArchive();
    $zip->open($tmp, ZipArchive::CREATE | ZipArchive::OVERWRITE);
    $files = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($full),
        RecursiveIteratorIterator::LEAVES_ONLY
    );

    foreach ($files as $name => $file)
    {
        if (!$file->isDir())
        {
            $filePath = $file->getRealPath();
            $relativePath = substr($filePath, strlen($full) + 1);
            $zip->addFile($filePath, $relativePath);
        }
    }

    $zip->close();

    $response = new AphrontFileResponse();
    $response->setMimeType('application/zip');
    $response->setCanCDN(false);
    $response->setDownload($file);
    $handle = fopen($tmp, "rb");
    if (!$handle) {
        return new Aphront404Response();
    }
    $contents = fread($handle, filesize($full));
    fclose($handle);
    $response->setContent($contents);
    return $response;
  }
}
