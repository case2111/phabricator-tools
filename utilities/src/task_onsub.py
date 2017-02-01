#!/usr/bin/python
"""Reports open issues when subscribed."""

import conduit


def process(factory, room, project):
    """Process event dates."""
    who = factory.create(conduit.User).whoami()["phid"]
    project_phid = None
    p_factory = factory.create(conduit.Project)
    for item in p_factory.by_name(project)[conduit.DATA_FIELD]:
        project_phid = item["phid"]
        break
    m = factory.create(conduit.Maniphest)
    sub = m.open_and_subscribed(who)
    conph = factory.create(conduit.Conpherence)
    msgs = []
    for subbed in sub:
        datum = sub[subbed]
        if datum["status"] != "actionneeded":
            continue
        if project_phid not in datum["projectPHIDs"]:
            continue
        msg = "{0} needs action from an admin".format(datum["objectName"])
        msgs.append(msg)
    if len(msgs) > 0:
        conph.updatethread(room, "\n".join(msgs))
