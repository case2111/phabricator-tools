<?php

final class PhareHostApplication extends PhabricatorApplication {

    public function getName() {
        return pht('Phare');
    }

    public function getShortDescription() {
        return pht('Phabricator sharing things fairly with users');
    }

    public function getBaseURI() {
        return '/phare/';
    }

    public function getRoutes() {
        return array(
          '/phare/([a-z]+)' => 'PhareController'
        );
    }

    public function isUnlisted() {
        return true;
    }

    public function isLaunchabled() {
        return false;
    }
}
