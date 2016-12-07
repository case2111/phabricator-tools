#!/usr/bin/python
"""Edits a phriction page from source."""

import argparse
import os
import conduit


def _process(factory, slug, title, content):
    """process the input file."""
    p = factory.create(conduit.Phriction)
    post_content = "> this page is managed externally, do NOT edit it\n\n"
    post_content = post_content + content
    p.edit(slug, title, post_content)


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--slug", required=True, type=str)
    parser.add_argument("--input", required=True, type=str)
    parser.add_argument("--title", required=True, type=str)
    args = parser.parse_args()
    if not os.path.exists(args.input):
        print('input file does not exist.')
        exit(-1)
    factory = conduit.Factory()
    factory.token = args.token
    factory.host = args.host
    with open(args.input, 'r') as f:
        _process(factory, args.slug, args.title, f.read())

if __name__ == '__main__':
    main()
