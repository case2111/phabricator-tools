#!/usr/bin/python
"""Reports on calendar events 'today'."""

import argparse
import conduit
import time
import calendar

def _process(host, token, room):
    """Process event dates."""
    factory = conduit.Factory()
    factory.token = token
    factory.host = host
    c = factory.create(conduit.CalendarEvent)
    who = factory.create(conduit.User).whoami()["phid"]
    e = c.upcoming_by_subscriber(who)["data"]
    now = calendar.timegm(time.localtime())
    now_end = now + 86400
    conph = factory.create(conduit.Conpherence)
    for item in e:
        start = item["fields"]["startDateTime"]["epoch"]
        end = item["fields"]["endDateTime"]["epoch"]
        if start >= now:
            if end <= now_end:
                msg = "E{0} is today".format(item["id"])
                conph.updatethread(room, msg)



def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--room", required=True, type=str)
    args = parser.parse_args()
    _process(args.host, args.token, args.room) 


if __name__ == '__main__':
    main()
