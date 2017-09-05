data
----
Scripts and utilties for managing data within phabricator

---

### backup
Handles dumping/backing up content from phabricator to the file system.

* Review the backup.sh to make sure it points where the phabricator install was done, going forward from there

#### enable

```
mkdir -p /opt/phab
mkdir -p /opt/phab/backups
ln -s /opt/phabricator-tools/data/backup/backup.sh /opt/phab/
systemctl enable /opt/phabricator-tools/data/backup/phabricator-backup.timer
ln -s /opt/phabricator-tools/data/backup/phabricator-backup.service /etc/systemd/system/
systemctl daemon-reload
systemctl start phabricator-backup.timer
```

---

### tar-repos
Supports a tar/gz of repos and static-file-hosting them. 

* This should be setup after the backup scripts are in place
* Review the tar-gz-repos.sh script to match the corresponding environment

#### enable

```
ln -s /opt/phabricator-tools/data/tar-repos/tar-gz-repos.sh /opt/phab/
systemctl enable /opt/phabricator-tools/data/tar-repos/phabricator-tar-repos.timer
ln -s /opt/phabricator-tools/data/tar-repos/phabricator-tar-repos.service /etc/systemd/system/
systemctl daemon-reload
systemctl start phabricator-tar-repos.timer
```

### repos

handles updating a wikipage with enabled repositories using the ZipController exstension

#### enable

```
systemctl enable /opt/phabricator-tools/data/repos/phabricator-repo-wiki.timer
ln -s /opt/phabricator-tools/data/repos/phabricator-repo-wiki.service /etc/systemd/system/
systemctl daemon-reload
systemctl start phabricator-repo-wiki.timer
```
