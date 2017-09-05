<?php

final class ZipHostApplication extends PhabricatorApplication {

  public function getName() {
    return pht('Repository bundled zips');
  }

  public function getShortDescription() {
    return pht('Supports downloading repositories as zips');
  }

  public function getBaseURI() {
    return '/zip/';
  }

  public function getRoutes() {
    return array(
      '/zip/(\d+)' => 'ZipController'
    );
  }

  public function isUnlisted() {
    return true;
  }

  public function isLaunchabled() {
    return false;
  }
}
