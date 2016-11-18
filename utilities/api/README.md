api
===

Phabricator API interactions via conduit and python

# conduit.py

The API implementation, via libcurl/pycurl

# duedates.py

Using a custom duedates field, will report to a room when open tasks are in the past

```
python duedates.py --host "http://phabricator.url/api/" --token "api-token" --room "1"
```

# unmodified.py

Reports when tasks are not updated in a timely fashion

```
python unmodified.py --host "http://phabricator.url/api/" --token "api-token" --room "1" --report 30 --close 45
```

# common.py

Helpers
