tar-repos
---
provides nightly tar/gz of files. This should be setup after the backup scripts are in place

# install

```
ln -s /opt/phabricator-tools/data/tar-repos/tar-gz-repos.sh /opt/phab/
systemctl enable /opt/phabricator-tools/data/tar-repos/phabricator-tar-repos.timer
ln -s /opt/phabricator-tools/data/tar-repos/phabricator-tar-repos.service /etc/systemd/system/
systemctl daemon-reload
systemctl start phabricator-tar-repos.timer
```
