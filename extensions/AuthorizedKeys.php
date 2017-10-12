<?php

final class PhabricatorAuthorizedKeysConduitAPIMethod
  extends PhabricatorAuthConduitAPIMethod {

  public function getAPIMethodName() {
    return 'auth.authorizedkeys';
  }

  public function getMethodDescription() {
    return pht('retrieve authorized keys.');
  }

  protected function defineParamTypes() {
    return array(
      'phids' => 'required list<phid>'
    );
  }

  protected function defineReturnType() {
    return 'result-set';
  }

  protected function execute(ConduitAPIRequest $request) {
    $viewer = $request->getUser();

    $query = id(new PhabricatorAuthSSHKeyQuery())
      ->setViewer($viewer)
      ->withIsActive(true);

    $object_phids = $request->getValue('phids');
    if ($object_phids !== null) {
      $query->withObjectPHIDs($object_phids);
    }

    $pager = $this->newPager($request);
    $public_keys = $query->executeWithCursorPager($pager);

    $keys = array();
    foreach ($public_keys as $public_key) {
      array_push($keys,
                 "# " . $public_key->getName(),
                 $public_key->getEntireKey());
    }

    $results = array(
      'data' => $keys,
    );

    return $this->addPagerResults($results, $pager);
  }
}

