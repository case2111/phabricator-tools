#!/usr/bin/python
"""Supports indexing checks/validations."""

import conduit


def _get_by_user(maniphest, user, tasks):
    """get all tasks by users with an index."""
    results = []
    results.append(maniphest.get_by_owner(user))
    results.append(maniphest.get_by_cc(user))
    results.append(maniphest.get_by_author(user))
    for res in results:
        for item in res:
            datum = res[item]
            if conduit.AUX_KEY in datum:
                aux = datum[conduit.AUX_KEY]
                if conduit.IDX_KEY in aux:
                    idx = aux[conduit.IDX_KEY]
                    if idx is not None and len(idx) > 0:
                        tasks[datum["objectName"]] = idx


def _process(factory, user_names, index_vals, room, silent):
    """process the index values for users and check validity."""
    c = factory.create(conduit.Conpherence)
    if not silent:
        c.updatethread(room, "checking index/tag values...")
    users = user_names.split(" ")
    tags = index_vals.split(" ")
    m = factory.create(conduit.Maniphest)
    all_tasks = {}
    msgs = []
    for u in users:
        _get_by_user(m, u, all_tasks)
    for task in all_tasks:
        idx = all_tasks[task].lower().split(" ")
        text = []
        for tag in idx:
            if tag in tags:
                if len(idx) > 1:
                    text.append("multi-part indexing")
            else:
                text.append("unknown tag")
        if len(text) > 0:
            msgs.append("{0} -> {1} ({2})".format(task,
                                                  ", ".join(set(text)),
                                                  idx))
    if len(msgs) == 0 and not silent:
        msgs.append("index/tag values all set")
    if len(msgs) > 0:
        msg = "\n".join(msgs)
        c.updatethread(room, msg)
