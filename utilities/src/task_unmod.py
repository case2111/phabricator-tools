#!/usr/bin/python
"""Handles reporting on open, deprecated due dates."""

import conduit
import calendar
import time
import task_duedates


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
            if "PHID-USER" in u:
                user_set.append(users[u])
        result[k] = sorted(set(user_set))
    return result


def _execute(factory, room, values, proj):
    """execute on a set of task values."""
    c = factory.create(conduit.Conpherence)
    m = factory.create(conduit.Maniphest)
    msgs = []
    tasks = {}
    task_data = m.get_by_ids([x[1:] for x in values.keys()])
    for t in task_data:
        tasks[task_data[t]["id"]] = task_data[t]["projectPHIDs"]
    for val in values:
        msgs.append("{0} will be auto-closed, please update it ({1})"
                    .format(val,
                            " ".join(values[val])))
        task_id = val[1:]
        cur = tasks[task_id]
        cur.append(proj)
        m.update_projects(task_id, cur)
    c.updatethread(room, "\n".join(sorted(msgs)))


def process(factory, room, report, project_close):
    """Process unmodified tasks."""
    p = factory.create(conduit.Project)
    m = factory.create(conduit.Maniphest)
    closing = m.open_by_project_phid(project_close)
    for task in closing:
        close_id = closing[task]["id"]
        m.resolve_by_id(close_id)
    res = p.open()["data"]
    proj_tracked = []
    reporting = {}
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
            if task_duedates.AUX_KEY in datum:
                aux = datum[task_duedates.AUX_KEY]
                if task_duedates.DUE_KEY in aux:
                    due = aux[task_duedates.DUE_KEY]
                    valid = False
                    if due is not None:
                        try:
                            int(due)
                            valid = True
                        except ValueError:
                            valid = False
                    if valid:
                        diff = 0
            if owner is not None:
                tell.append(owner)
            if cc is not None:
                for user in cc:
                    tell.append(user)
            if diff > report:
                reporting[task] = tell
            bad = task in reporting
            if bad:
                for telling in tell:
                    if telling not in all_users:
                        all_users.append(telling)
    if len(reporting) == 0:
        return

    resolved = resolve_users(factory, all_users)
    super_sets = []
    if len(reporting) > 0:
        super_sets.append(reporting)
    for sets in super_sets:
        use_set = _convert_user_phid(sets, resolved)
        _execute(factory, room, use_set, project_close)
