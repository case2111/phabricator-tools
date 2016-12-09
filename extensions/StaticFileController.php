<?php
final class StaticFileController extends PhabricatorController {
  public function handleRequest(AphrontRequest $request) {
    $file = split('/', $request->getRequestURI())[2];
    $env = getenv('PHAB_MON_PATH');
    if (!$env) {
      $env = '/tmp/'
    }
    $full = $env . $file;
    if (!file_exists($full)) {
        return new Aphront404Response();
    }
    $ext = pathinfo($full)['extension'];
    $response = new AphrontFileResponse();
    $mime = 'n/a';
    switch ($ext) {
        case "pdf":
            $mime = 'application/pdf';
            break;
        default:
            return new Aphront404Response();
    }
    $response->setMimeType($mime);
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
