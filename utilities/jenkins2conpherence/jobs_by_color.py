#!/usr/bin/python

"""Retrieve and output jobs by color."""

import jenkins
import argparse
import re
import conduit

ALL_COLORS = 'ALL'


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--jenkins', required=True, type=str)
    parser.add_argument('--user', required=True, type=str)
    parser.add_argument('--pwd', required=True, type=str)
    parser.add_argument('--colors', required=True, type=str)
    parser.add_argument('--ignore', default=None, type=str)
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--room", required=True, type=int)
    args = parser.parse_args()
    server = jenkins.Jenkins(args.jenkins,
                             username=args.user,
                             password=args.pwd)
    colors = args.colors.split(',')
    do_all = args.colors == ALL_COLORS
    color_out = {}
    ignores = None
    if args.ignore is not None:
        ignore_str = args.ignore
        if ignore_str.strip():
            ignores = re.compile(args.ignore)
    for job in server.get_jobs():
        job_color = job['color']
        job_name = job['name']
        if ignores is not None:
            if ignores.search(job_name) is not None:
                continue
        if job_color in colors or do_all:
            if job_color not in color_out:
                color_out[job_color] = []
            color_out[job_color].append(job_name)
    messages = []
    for key in sorted(color_out.keys()):
        messages.append(key)
        messages.append('---')
        for item in sorted(color_out[key]):
            messages.append('{0}'.format(item))
        messages.append('\n')
    c = conduit.Conpherence()
    c.host = args.host
    c.token = args.token
    c.updatethread(args.room, "\n".join(messages))

if __name__ == '__main__':
    main()
