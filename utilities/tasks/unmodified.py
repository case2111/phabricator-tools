#!/usr/bin/python
"""Handles reporting on open, deprecated due dates."""

import argparse
import conduit
import calendar
import time


def resolve_users(factory, user_set):
    """resolve user phid set to dict of phid & @name."""
    u = factory.create(conduit.User)
    users = u.by_phids(user_set)
    resolved_users = {}
    for user in users:
        resolved_users[user["phid"]] = "@" + user["userName"]
    return resolved_users


def _convert_user_phid(input_set, users):
    """convert user phids to users."""
    result = {}
    for k in input_set:
        user_set = []
        for u in input_set[k]:
            user_set.append(users[u])
        result[k] = sorted(set(user_set))
    return result


def _execute(factory, room, host, values, message, is_closing):
    """execute on a set of task values."""
    c = factory.create(conduit.Conpherence)
    m = factory.create(conduit.Maniphest)
    msgs = []
    for val in values:
        msgs.append("[`{0}`]({3}/{0}) ({1}) {2}"
                    .format(val,
                            " ".join(values[val]),
                            message,
                            host))
        if is_closing:
            m.invalid_by_id(val[1:])
    c.updatethread(room, "\n".join(sorted(msgs)))

def _process(host, token, room, report, close):
    """Process unmodified tasks."""
    factory = conduit.Factory()
    factory.token = token
    factory.host = host
    p = factory.create(conduit.Project)
    m = factory.create(conduit.Maniphest)
    res = p.open()["data"]
    proj_tracked = []
    reporting = {}
    closing = {}
    all_users = []
    now = calendar.timegm(time.localtime())
    for proj in res:
        if proj in proj_tracked:
            continue
        proj_tracked.append(proj)
        tasks = m.open_by_project_phid(proj)
        for item in tasks:
            datum = tasks[item]
            modified = int(datum["dateModified"])
            diff = (now - modified) / 86400
            task = datum["objectName"]
            tell = [datum["authorPHID"]]
            owner = datum["ownerPHID"]
            cc = datum["ccPHIDs"]
            if owner is not None:
                tell.append(owner)
            if cc is not None:
                for user in cc:
                    tell.append(user)
            if diff > close:
                closing[task] = tell
            else:
                if diff > report:
                    reporting[task] = tell
            bad = task in reporting or task in closing
            if bad:
                for telling in tell:
                    if telling not in all_users:
                        all_users.append(telling)
    if len(reporting) == 0 and len(closing) == 0:
        return

    resolved = resolve_users(factory, all_users)
    super_sets = []
    if len(reporting) > 0:
        super_sets.append((reporting, "will be closed if not updated soon", False))
    if len(closing) > 0:
        super_sets.append((closing, "was closed, no recent activity", True))
    for sets in super_sets:
        use_set = _convert_user_phid(sets[0], resolved)
        _execute(factory, room, host, use_set, sets[1], sets[2])


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--room", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--report", required=True, type=int)
    parser.add_argument("--close", required=True, type=int)
    args = parser.parse_args()
    _process(args.host, args.token, args.room, args.report, args.close)


if __name__ == '__main__':
    main()
