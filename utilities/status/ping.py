#!/usr/bin/python
"""Report on execution."""

import argparse
import conduit

def _process(host, token, room, flavor):
    """Ping alive."""
    factory = conduit.Factory()
    factory.token = token
    factory.host = host
    msg = "{0} timer executed".format(flavor)
    factory.create(conduit.Conpherence).updatethread(room, msg)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--room", required=True, type=str)
    parser.add_argument("--flavor", required=True, type=str)
    args = parser.parse_args()
    _process(args.host, args.token, args.room, args.flavor)


if __name__ == '__main__':
    main()
