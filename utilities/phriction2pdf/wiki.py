#!/usr/bin/python

"""Handles consuming wiki md and producing output."""

import argparse
import os
import json


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


def process(in_name, out_name):
    """process the input file."""
    if os.path.exists(in_name):
        result = None
        with open(in_name, 'r') as f:
            file_content = f.read()
            obj = json.loads(file_content)
            if result_key in obj:
                obj_result = obj[result_key]
                if obj_result is not None and content_key in obj_result:
                    result = obj_result[content_key]
                    for converter in converters:
                        result = converter(result)
            if result is None:
                print('invalid result, file contents...')
                print(file_content)
                exit(-1)
            with open(out_name, 'w') as f:
                f.write(result)
    else:
        print('no file found: ' + file_name)
        exit(-1)


def main():
    """Main entry."""
    parser = argparse.ArgumentParser(description='wiki "processing"')
    parser.add_argument('--input', help='input file', required=True)
    parser.add_argument('--output', help='output file', required=True)
    args = parser.parse_args()
    try:
        process(args.input, args.output)
    except Exception as error:
        print(error)
        exit(-1)


if __name__ == '__main__':
    main()
