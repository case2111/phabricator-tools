#!/usr/bin/python
"""Reports open issues when subscribed."""

import conduit


def process(factory, room, project):
    """Process event dates."""
    who = factory.create(conduit.User).whoami()["phid"]
    project_phid = None
    for item in factory.create(conduit.Project).by_name(project)["data"]:
        project_phid = item
        break
    m = factory.create(conduit.Maniphest)
    sub = m.open_and_subscribed(who)
    conph = factory.create(conduit.Conpherence)
    for subbed in sub:
        datum = sub[subbed]
        if datum["status"] != "actionneeded":
            continue
        if project_phid not in datum["projectPHIDs"]:
            continue
        msg = "{0} needs action from an admin".format(datum["objectName"])
        conph.updatethread(room, msg)
