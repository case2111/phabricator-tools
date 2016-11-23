#!/usr/bin/python
"""Reports open issues when subscribed."""

import argparse
import conduit


def _process(host, token, room, project):
    """Process event dates."""
    factory = conduit.Factory()
    factory.token = token
    factory.host = host
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


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--room", required=True, type=str)
    parser.add_argument("--project", required=True, type=str)
    args = parser.parse_args()
    _process(args.host, args.token, args.room, args.project)


if __name__ == '__main__':
    main()
