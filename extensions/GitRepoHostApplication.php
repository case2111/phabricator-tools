<?php

final class GitRepoHostApplication extends PhabricatorApplication {
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
          '/gitweb/(.*)' => 'GitRepoController'
        );
    }

    public function isUnlisted() {
        return false;
    }

    public function isLaunchabled() {
        return false;
    }
}

