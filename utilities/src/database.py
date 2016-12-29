#!/usr/bin/python
"""Database query execution."""

import mysql.connector as mariadb
import conduit


def user_check(user, password, factory, room):
    """Check user conpherence activity."""
    users = []
    u_factory = factory.create(conduit.User)
    for u in _get_scaler(user,
                         password,
                         "phabricator_conpherence",
                         """
                         select distinct participantPHID
                         from conpherence_participant
                         where participationStatus = 1 and
                            participantPHID not in (
                                SELECT participantPHID
                                from conpherence_participant
                                where participationStatus = 0
                            );"""):
        user_obj = u_factory.by_phids([u])[0]
        if "agent" in user_obj["roles"]:
            continue
        named = "@" + user_obj["userName"]
        users.append(named)
    if len(users) > 0:
        c = factory.create(conduit.Conpherence)
        c.updatethread(room,
                       "ignoring chat: {0}".format(",".join(sorted(users))))


def _get_scaler(user, password, db, query):
    """Get a scaler result set."""
    conn = mariadb.connect(user=user,
                           password=password,
                           database=db)
    curs = conn.cursor()
    curs.execute(query)
    for row in curs:
        yield row[0].decode("ascii")
