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


### Environment Variables

Environment variables used by the various utility functions
```
vim /etc/environment
---
# host name
PHAB_HOST="https://phabricator.yourdomain"

# general purpose/common room for phabricator tenants to see messages
PHAB_COMMON_ROOM="1"

# task manager token
PHAB_TASK_TOKEN="api-token"

# instance monitor token
PHAB_MON_TOKEN="api-token"

# status watch token
PHAB_STATUS_TOKEN="api-token"

# token for bot on the phabricator box
PHAB_PBOT_TOKEN="api-token"

# room bots can chat in safely
PHAB_BOT_ROOM="2"

# location of install dir (git clone)
PHAB_TOOLS="/opt/phabricator-tools"

# an administrative/meta project
PHAB_ADMIN_PROJ="admin-proj"

# domain name
PHAB_CHECK_DOMAIN="yourdomain"

# hosts to ping/check
PHAB_CHECK_HOSTS="host1 host2 host3"

# pre-receive hook message
PHAB_PRE_RECEIVE_MSG="!monitor|genpage|slug/path|\"page title\"|rREPO|artifact/path.csv"

# execute scheduled tasks
PHAB_TIMED_MSG="!schedule do"

# sleep this long when doing pre-receive hook (to support repo updating)
PHAB_MON_SLEEP="5"

# location of static file (must match sfh extension)
PHAB_MON_PATH="/opt/phab/static/"

# dashboard panel for updating
PHAB_DASH_OBJECT="1"

# slug to use to update the panel
PHAB_DASH_WIKI="slug/path/dash"

# threshold a task must not be modified for before being marked for auto-close
PHAB_AUTOCLOSE_THRESH="60"

# project that will autoclose when scheduling runs
PHAB_AUTOCLOSE_PROJ="PHID-PROJ-id"
```
