backup
------
Content backup

# install

```
cd /opt
git clone https://github.com/epiphyte/phabricator-tools
```

review the backup.sh to make sure it points where the phabricator install was done, going forward from there
```
mkdir -p /opt/phab
mkdir -p /opt/phab/backups
ln -s /opt/phabricator-tools/data/backup/backup.sh /opt/phab/
systemctl enable /opt/phabricator-tools/data/backup/phabricator-backup.timer
ln -s /opt/phabricator-tools/data/backup/phabricator-backup.service /etc/systemd/system/
systemctl start phabricator-backup.timer
```
