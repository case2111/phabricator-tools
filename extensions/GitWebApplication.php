<?php

final class GitWebApplication extends PhabricatorApplication {
    public function getName() {
        return pht('Git Repository Browser');
    }

    public function getShortDescription() {
        return pht('Reverse proxy to support browsing phabricator repos without diffusion');
    }

    public function getBaseURI() {
        return '/gitweb/';
    }

    public function getRoutes() {
        return array(
          '/gitweb/(.*)' => 'GitWebController'
        );
    }
    public function getIcon() {
        return 'fa-code';
    }
    public function isUnlisted() {
        return false;
    }

    public function isLaunchabled() {
        return false;
    }
}

