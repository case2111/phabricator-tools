#!/usr/bin/python
"""Handles reporting on open, deprecated due dates."""

import conduit
import time
import calendar

DUE_KEY = "std:maniphest:custom:duedate"
AUX_KEY = "auxiliary"


def process(factory):
    """Process due dates."""
    m = factory.create(conduit.Maniphest)
    res = m.open()
    now = calendar.timegm(time.localtime())
    for item in res:
        datum = res[item]
        if AUX_KEY in datum:
            aux = datum[AUX_KEY]
            if DUE_KEY in aux:
                due = aux[DUE_KEY]
                if due is not None:
                    if due < now:
                        name = datum["objectName"][1:]
                        m.comment_by_id(name, "this task is overdue")
