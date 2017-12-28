<?php
final class TaskRedirController extends PhabricatorController {
    public function handleRequest(AphrontRequest $request) {
        $tasks = '/opt/taskredir/';
        exec('git -C ' . $tasks . ' pull 2>&1');
        $path = $tasks . 'forms/';
        $maniphest = $path . 'forms.csv';
        $name = explode('/', $request->getRequestURI())[2];
        if (file_exists($maniphest) ) {
            $csv = array_map('str_getcsv', file($maniphest));
            $header = array_shift($csv);
            foreach ($csv as $value) {
                if ($name == $value[0]) {
                    $use_file = $path . $value[0] . ".md";
                    if (file_exists($use_file)) {
                        $raw_text = file_get_contents($use_file);
                        $quoted = urlencode($raw_text);
                        $and = $value[1];
                        $response = new AphrontRedirectResponse();
                        $response->setURI("/maniphest/task/edit/form/default/?description=" . $quoted . $and);
                        return $response;
                    }
                }
            }
        }
        return new Aphront404Response();
    }
}
