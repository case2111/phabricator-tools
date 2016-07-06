phriction2pdf
-------------
Interrogate jenkins job status and report to phabricator

required make parameters
```
make token='your-conduit-token' jenkins='http://jenkins:port/url' user='jenkins_user' pass='jenkins_pass/token' host='http://phabricator.host' room=room_id
```
* The token and host variables support environment variables of PHAB_API_TOKEN and PHAB_HOST

optional parameters are colors (status colors to match) and timeout (for curl)
```
colors=red timeout=60
```
