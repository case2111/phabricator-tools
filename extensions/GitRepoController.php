<?php
final class GitRepoController extends PhabricatorController {
    private function endsWith($str, $search)
    {
        $length = strlen($search);
        return $length === 0 || (substr($str, -$length) === $search);
    }

    public function handleRequest(AphrontRequest $request) {
        $querystring = parse_url($request->getRequestURI(), PHP_URL_QUERY);
        if (isset($querystring) && trim($querystring) != '') {
            $querystring = htmlspecialchars(sprintf('?%s', $querystring));
        }
        $path = explode('?', join('/', array_slice(explode('/', $request->getRequestURI()), 1)))[0];
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
        if ($this->endsWith($path, '.css')) {
            $resp->setMimeType('text/css');
        }
        $resp->setCanCDN(false);
        $resp->setContent($ret);
    	return $resp;
    }
}
