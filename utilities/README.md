utilities
===

general implementation of phabricator enhancements/utilities

## setup

```
cd /opt/phabricator-tools/utilities
make install
```

---

### src
python implementation(s)

---

### system
system install and execution scripts

#### scripts

* Timers that run daily/weekly
* Chat wrapper

#### git

* hooks to implement repo-based workflows

navigate to git repository `.git/hooks/` and link the corresponding hooks by name

#### systemd-units

* units to enable timers, chat, etc.

```
systemctl enable /opt/phabricator-tools/utilities/system/systemd-units/{name}.timer
ln -s /opt/phabricator-tools/utilities/system/systemd-units/{name}.service
systemctl daemon-reload
systemctl start {name}.timer
```
