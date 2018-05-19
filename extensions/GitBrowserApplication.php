<?php

final class GitBrowserApplication extends PhabricatorApplication {
    public function getName() {
        return pht('Git Repository Browser');
    }

    public function getShortDescription() {
        return pht('Reverse proxy to support browsing phabricator repos without diffusion');
    }

    public function getBaseURI() {
        return '/cgit/';
    }

    public function getRoutes() {
        return array(
          '/cgit/(.*)' => 'GitBrowserController'
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

