#!/usr/bin/python
"""Common helpers."""

import conduit


def resolve_users(factory, user_set):
    """resolve user phid set to dict of phid & @name."""
    u = factory.create(conduit.User)
    users = u.by_phids(user_set)
    resolved_users = {}
    for user in users:
        resolved_users[user["phid"]] = "@" + user["userName"]
    return resolved_users
