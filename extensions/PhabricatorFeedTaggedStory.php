<?php
final class PhabricatorFeedTaggedStory extends PhabricatorFeedStory {
  public function getPrimaryObjectPHID() {
    return $this->getAuthorPHID();
  }
  public function renderView() {
    $data = $this->getStoryData();
    $author_phid = $data->getAuthorPHID();
    $view = $this->newStoryView();
    $view->setTitle($data->getValue('title'));
    $view->setImage($this->getHandle($author_phid)->getImageURI());
    return $view;
  }
  public function renderText() {
    $data = $this->getStoryData();
    $fields = explode(',', $data->getValue('fields', ''));
    array_push($fields, 'tag', 'title');
    $obj = array();
    foreach ($fields as &$fld) {
        if($fld != '') {
            $obj[$fld] = $data->getValue($fld, '');
        }
    }
    return json_encode($obj);
  }
}
