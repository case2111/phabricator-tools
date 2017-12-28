<?php

final class StaticFileHostApplication extends PhabricatorApplication {

    public function getName() {
        return pht('Static File Hosting');
    }

    public function getShortDescription() {
        return pht('Supports static file hosting within phabricator');
    }

    public function getBaseURI() {
        return '/sfh/';
    }

    public function getRoutes() {
        return array(
          '/sfh/(\d+)\.([a-z]+)' => 'StaticFileController'
        );
    }

    public function isUnlisted() {
        return true;
    }

    public function isLaunchabled() {
        return false;
    }
}
