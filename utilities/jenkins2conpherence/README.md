phriction2pdf
-------------
Interrogate jenkins job status and report to phabricator

required make parameters
```
make token='your-conduit-token' jenkins='http://jenkins:port/url' user='jenkins_user' pass='jenkins_pass/token' host='phabricator.host' room=room_id
```

optional parameters are colors (status colors to match) and timeout (for curl)
```
colors=red timeout=60
```
