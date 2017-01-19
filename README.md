phabricator-tools
===
A toolbox of utilities for interacting with phabricator.

## data
Tools for dealing with data in phabricator on the host

### highlights

* nightly backup scripts
* production of nightly repository bundles/snapshots

---

## extensions
Phabricator extensions

### Static File Host (sfh)

* Provides an endpoint "/sfh/" within phabricator to place and download/view files
* Requires naming of format [0-9]+.[extension]
* Currently supports pdf, html, and gzip downloads

### highlights

* static file hosting (behind phabricator)
* ability to host various file types matching names and by file extension

---

## utility
Various utility scripts for interacting with parts of phabricator

### highlights

* chat bot(s)
* weekly/daily scheduled tasks (via systemd + chat bots)
* requiring tasks to remain updated within a time window
* detecting users who are not using conpherence/phab enough :)
* generate dashboard panels from wiki pages
* generate docs (pdf) from wiki pages/repos
* generate wiki docs from repos
* Using a custom date (due date) to manage tasks falling in/out of schedule
