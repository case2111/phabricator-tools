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

### backup

nightly backup/snapshot of phabricator content for restoration/migration/backup purposes

### repos

manage the links to active repos served by a proxied app (cgit)

### sshkeys

* extract (for remote usage) user ssh keys for other location deployments
* retrieve ssh keys from a remote location

### reports

load reports (using a common header) into phabricator from an inbox

### cleansing

cleansing/maintenance scripts to monitor state of tasks/projects/wiki

## extensions

### Logout (conduit)

* Logout users by passing a list of PHIDs
* Adminstrator only

### Task Redirection

* Supports utilizing a diffusion repo (local) clone to perform repo-configured redirects

### Git

Provides a reverse proxy to a locally running version of cgit

## logs

Handles log rotation as necessary for phd and aphlict

## Authorized Keys (conduit)

* Take a set of phids (users) and produce a data array output for use in authorized keys

e.g.
```
curl https://<phabricator>/api/auth.authorizedkeys  -d phids[0]=PHID-USER-xyz -d api.token=api-token | python -c "import sys, json; print('\n'.join(json.loads(sys.stdin.read())['result']['data']))"
```

## utilities

maintenance/utility scripts to maintain/cleanse phabricator data
