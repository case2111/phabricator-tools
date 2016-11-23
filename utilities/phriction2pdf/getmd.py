#!/usr/bin/python
"""Handles consuming wiki and producing output md."""

import argparse
import os
import conduit


def asterisk_lists(content):
    """Convert asterisk pairs to tab asterisk."""
    working = content
    while "**" in working:
        working = working.replace("**", "\t*")
    return working

converters = []
converters.append(asterisk_lists)
result_key = 'result'
content_key = 'content'


def _process(host, token, slug, output):
    """process the input file."""
    factory = conduit.Factory()
    factory.token = token
    factory.host = host
    p = factory.create(conduit.Phriction)
    obj_result = p.info(slug)
    if content_key in obj_result:
        result = obj_result[content_key]
        for converter in converters:
            result = converter(result)
    if result is None:
        print('invalid result, file contents...')
        print(file_content)
        exit(-1)
    with open(output, 'w') as f:
        f.write(result)


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--slug", required=True, type=str)
    parser.add_argument("--output", required=True, type=str)
    args = parser.parse_args()
    _process(args.host, args.token, args.slug, args.output)

if __name__ == '__main__':
    main()
