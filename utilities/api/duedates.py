#!/usr/bin/python
"""Handles reporting on open, deprecated due dates."""

import argparse
import common
import conduit
import time
import calendar

DUE_KEY = "std:maniphest:custom:duedate"
AUX_KEY = "auxiliary"


def _process(host, token):
    """Process due dates."""
    factory = conduit.Factory()
    factory.token = token
    factory.host = host
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
                        name = datum["objectName"]
                        m.comment_by_id(name[1:], "this task is overdue")

def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    args = parser.parse_args()
    _process(args.host, args.token)


if __name__ == '__main__':
    main()
