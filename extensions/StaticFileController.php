<?php
final class StaticFileController extends PhabricatorController {
  public function handleRequest(AphrontRequest $request) {
    $file = split('/', $request->getRequestURI())[2];
    $full = '/opt/phab/static/' . $file;
    if (!file_exists($full)) {
        return new Aphront404Response();
    }
    $response = new AphrontFileResponse();
    $response->setCanCDN(false);
    $response->setMimeType('application/pdf');
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
