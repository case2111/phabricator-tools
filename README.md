phabricator-tools
===
A toolbox of utilities for interacting with phabricator. These tools are meant to extend and expand the abilities presented by phabricator. Though they are custom to our organizations requirements, they should offer some insights and starting points for other implementations

# install

configure and setup the epiphyte [repository](https://github.com/epiphyte/repository)

install
```
pacman -S phabricator-tools
```

## data
Tools for dealing with data in phabricator on the host. These include general data management from phabricator within the phabricator machine instance. Including the ability to produce nightly backups (following the data to backup from the phabricator guide) and nightly snapshot bundles of repositories

### tar/nightly repo

tar/bundle repositories into gunzip files
```
systemctl enable phabricator-tar-repos.timer
```

### backup

nightly backup/snapshot of phabricator content for restoration/migration/backup purposes

```
systemctl enable phabricator-backup.timer
```

### repos

update a wiki/phriction page with current repository (diffusion) download links

```
systemctl enable phabricator-repo-wiki.timer
```

## extensions

### Static File Host (sfh)

* Provides an endpoint "/sfh/" within phabricator to place and download/view files
* Requires naming of format [0-9]+.[extension]
* Currently supports pdf, html, and gzip downloads
* Copy the php files into the phabricator extensions folder

### Feed Tagged Story

* Feed stories that take a 'title' and 'tag' json element
* Produce a delimited `JSON:{'title': '<input_title>', 'tag': '<input_tag>'}` rendering

### Zip (diffusion)

* Current/live zips of diffusion repositories
* Supports "package" download with requiring `git`

## logs

Handles log rotation as necessary for phd and aphlict
