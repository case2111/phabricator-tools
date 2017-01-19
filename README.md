phabricator-tools
===
A toolbox of utilities for interacting with phabricator. These tools are meant to extend and expand the abilities presented by phabricator. Though they are custom to our organizations requirements, they should offer some insights and starting points for other implementations


## general setup

clone the repository
```
cd /opt
git clone https://github.com/epiphyte/phabricator-tools
cd phabricator-tools
git checkout stable
```

from here navigate to subfolders where applicable for further instruction

## data
Tools for dealing with data in phabricator on the host. These include general data management from phabricator within the phabricator machine instance. Including the ability to produce nightly backups (following the data to backup from the phabricator guide) and nightly snapshot bundles of repositories

---

## extensions

### Static File Host (sfh)

* Provides an endpoint "/sfh/" within phabricator to place and download/view files
* Requires naming of format [0-9]+.[extension]
* Currently supports pdf, html, and gzip downloads
* Copy the php files into the phabricator extensions folder

---

## utility
Various utility scripts for interacting with parts of phabricator, like:

* chat bot(s)
* weekly/daily scheduled tasks (via systemd + chat bots)
* requiring tasks to remain updated within a time window
* detecting users who are not using conpherence/phab enough :)
* generate dashboard panels from wiki pages
* generate docs (pdf) from wiki pages/repos
* generate wiki docs from repos
* Using a custom date (due date) to manage tasks falling in/out of schedule
