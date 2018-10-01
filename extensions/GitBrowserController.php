<?php
final class GitBrowserController extends PhabricatorController {
    private function endsWith($str, $search)
    {
        $length = strlen($search);
        return $length === 0 || (substr($str, -$length) === $search);
    }

    public function handleRequest(AphrontRequest $request) {
        $querystring = parse_url($request->getRequestURI(), PHP_URL_QUERY);
        if (isset($querystring) && trim($querystring) != '') {
            $querystring = sprintf('?%s', $querystring);
	}
	$parts = explode('/', $request->getRequestURI());
        $path = explode('?', join('/', array_slice($parts, 1)))[0];
        $url = sprintf('http://localhost:19999/%s%s', $path, urldecode($querystring));
        $ret = file_get_contents($url, FALSE);
        if( FALSE === $ret ) {
            return new Aphront404Response();
        }
        $resp = new AphrontFileResponse();
        $resp->setMimeType('text/html');
        if ($this->endsWith($path, '.js')) {
            $resp->setMimeType('text/javascript');
        }
        if ($this->endsWith($path, '.tar.gz')) {
            $resp->setMimeType('applization/gzip');
        }
        if ($this->endsWith($path, '.zip')) {
            $resp->setMimeType('application/zip');
        }
        if ($this->endsWith($path, '.png')) {
            $resp->setMimeType('image/png');
        }
        if ($this->endsWith($path, '.jpg')) {
            $resp->setMimeType('image/jpeg');
        }
        if ($this->endsWith($path, '.css')) {
            $resp->setMimeType('text/css');
        }
        if (sizeof($parts) > 4) {
            if (strstr($parts[4], 'plain')) {
                $resp->setMimeType('text/plain');
            }
        }
        $resp->setCanCDN(false);
        $resp->setContent($ret);
    	return $resp;
    }
}
