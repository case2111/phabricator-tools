utilities
---------
Various utilities for interacting with phabricator

# chat_*
provides a websocket connected chatbot for getting messages to a bot outside of phabricator

```
python chat_bot.py --host "https://phab.example.com" --token "api-token" --last 30 --lock /path/to/lock/file
```

# task_*
provides timed (daily, weekly) tasks operations within and around phabricator
