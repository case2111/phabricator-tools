#!/usr/bin/python
"""Handles reporting on open, deprecated due dates."""

import argparse
import conduit
import time
import calendar

DUE_KEY = "std:maniphest:custom:duedate"
AUX_KEY = "auxiliary"


def _process(host, token, room):
    """Process due dates."""
    factory = conduit.Factory()
    factory.token = token
    factory.host = host
    m = factory.create(conduit.Maniphest)
    res = m.open()
    now = calendar.timegm(time.localtime())
    outdated = {}
    for item in res:
        datum = res[item]
        if AUX_KEY in datum:
            aux = datum[AUX_KEY]
            if DUE_KEY in aux:
                due = aux[DUE_KEY]
                if due is not None:
                    if due < now:
                        name = datum["objectName"]
                        users = datum["authorPHID"]
                        owner = datum["ownerPHID"]
                        if owner is not None:
                            users = owner
                        outdated[name] = [users]
                        #outdated.append(res[item]["objectName"])
    if len(outdated) > 0:
        user_phids = []
        for task in outdated:
            for user in outdated[task]:
                if user not in user_phids:
                    user_phids.append(user)
        u = factory.create(conduit.User)
        users = u.by_phids(user_phids)
        resolved_users = {}
        for user in users:
            resolved_users[user["phid"]] = "@" + user["userName"]
        outputs = []
        for old in outdated:
            user_set = []
            for user in outdated[old]:
                user_set.append(resolved_users[user])
            msg = "{0} ({1})".format(old, ",".join(set(user_set)))
            outputs.append(msg)
        msg = "the following tasks have due dates in the past: {0}".format(
                " ".join(outputs))
        c = factory.create(conduit.Conpherence)
        c.updatethread(room, msg)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--room", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    args = parser.parse_args()
    _process(args.host, args.token, args.room)


if __name__ == '__main__':
    main()
