<?php

final class TaskRedirHostApplication extends PhabricatorApplication {

  public function getName() {
    return pht('Task Redirection Hosting');
  }

  public function getShortDescription() {
    return pht('Supports task redirection hosting within phabricator');
  }

  public function getBaseURI() {
    return '/sfh/';
  }

  public function getRoutes() {
    return array(
      '/taskredir/([a-z]+)' => 'TaskRedirController'
    );
  }

  public function isUnlisted() {
    return true;
  }

  public function isLaunchabled() {
    return false;
  }
}

