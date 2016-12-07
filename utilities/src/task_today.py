#!/usr/bin/python
"""Reports on calendar events 'today'."""

import conduit
import time
import calendar


def process(factory, room):
    """Process event dates."""
    c = factory.create(conduit.CalendarEvent)
    who = factory.create(conduit.User).whoami()["phid"]
    e = c.upcoming_by_subscriber(who)["data"]
    gm = time.gmtime()
    now = calendar.timegm(gm)
    now_end = now + 86400
    conph = factory.create(conduit.Conpherence)
    for item in e:
        fields = item["fields"]
        start = fields["startDateTime"]["epoch"]
        end = fields["endDateTime"]["epoch"]
        start_time = time.gmtime(start)
        is_all = fields['isAllDay'] and \
            start_time.tm_mon == gm.tm_mon and \
            start_time.tm_mday == gm.tm_mday and \
            start_time.tm_year == gm.tm_year
        if (start >= now and end <= now_end) or is_all:
            msg = "E{0} is today (flagged all day? {1})".format(item["id"],
                                                                is_all)
            conph.updatethread(room, msg)
