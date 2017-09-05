<?php
final class ZipController extends PhabricatorController {
  public function handleRequest(AphrontRequest $request) {
    $file = explode('/', $request->getRequestURI())[1];
    $full = '/var/opt/phabricator/git/' . $file;
    if (!file_exists($full)) {
        return new Aphront404Response();
    }
    $response = new AphrontFileResponse();
    $response->setMimeType('application/zip');
    $response->setCanCDN(false);
    $response->setDownload($file);
    $handle = fopen($full, "rb");
    if (!$handle) {
        return new Aphront404Response();
    }
    $contents = fread($handle, filesize($full));
    fclose($handle);
    $response->setContent($contents);
    return $response;
  }
}
