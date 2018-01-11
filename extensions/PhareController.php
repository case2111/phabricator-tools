<?php
final class PhareController extends PhabricatorController {
    public function handleRequest(AphrontRequest $request) {
        $pharing = '/opt/phare/';
        $user = strtolower($request->getUser()->getUserName());
        $user = preg_replace("/[^:alnum:]]/u", "", $user);
        $name = strtolower(explode('/', $request->getRequestURI())[2]);
        $file_name = $pharing . $user . "." . $name . "*";
        foreach (glob($file_name) as $f_name) {
            $response = new AphrontFileResponse();
            $response->setMimeType("application/octet-stream");
            $response->setCanCDN(false);
            $full_name = $f_name;
            $handle = fopen($full_name, 'rb');
            if (!$handle) {
                continue;
            }
            $base = basename($full_name);
            $response->setDownload($base);
            $contents = fread($handle, filesize($full_name));
            fclose($handle);
            $response->setContent($contents);
            return $response;
        }
        return new Aphront404Response();
    }
}
