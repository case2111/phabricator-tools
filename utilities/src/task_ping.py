#!/usr/bin/python
"""Report on execution."""

import conduit
import os


def process(factory, room, msg):
    """Ping alive."""
    factory.create(conduit.Conpherence).updatethread(room, msg)


def check(factory, room, hosts):
    """Check a host for being up."""
    for host in hosts:
        response = os.system("ping -c 4 " + host + " -4")
        if response != 0:
            process(factory, room, "{0} is down...".format(host))
