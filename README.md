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

### Feed Tagged Story

* Feed stories that take a 'title' and 'tag' json element
* Produce a delimited `JSON:{'title': '<input_title>', 'tag': '<input_tag>'}` rendering

## logs

---

Handles log rotation as necessary

```
cd logs
ln -s /path/to/logs/phd-rotate /etc/logrotate.d/phd
ln -s /path/to/logs/aphlict-rotate /etc/logrotate.d/aphlict
```
