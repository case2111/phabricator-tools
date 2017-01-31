#!/usr/bin/python
"""Handles reporting on open, deprecated due dates."""

import conduit
import time
import calendar


def process(factory):
    """Process due dates."""
    m = factory.create(conduit.Maniphest)
    res = m.open()
    now = calendar.timegm(time.localtime())
    for item in res:
        datum = res[item]
        if conduit.AUX_KEY in datum:
            aux = datum[conduit.AUX_KEY]
            if conduit.DUE_KEY in aux:
                due = aux[conduit.DUE_KEY]
                if due is not None:
                    if due < now:
                        name = datum["objectName"][1:]
                        m.comment_by_id(name, "this task is overdue")
