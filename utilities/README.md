utilities
---------
Various utilities for interacting with phabricator

# phriction2pdf
Tooling to consuming a phriction page, convert markdown for consumption by pandoc, and output a pdf

# jenkins2conpherence
Tooling to check jenkins status values for jobs and send a message to a phabricator conpherence room


# chatbot
provides a websocket connected chatbot for getting messages to a bot outside of phabricator

```
python chatty.py --host "https://phab.example.com" --token "api-token" --last 30 --lock /path/to/lock/file
```
