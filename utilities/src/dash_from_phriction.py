#!/usr/bin/python
"""Convert a phriction page to dashboard object."""
import argparse
import conduit
import re
from datetime import datetime


def update(factory, slug, obj):
    """Update an object (dashboard) from wiki."""
    p = factory.create(conduit.Phriction)
    d = factory.create(conduit.Dashboard)
    wiki = p.info(slug)
    lines = []
    regex = re.compile(r'\d{4}[-/]\d{2}[-/]\d{2}')
    today = datetime.now()
    today = datetime(today.year, today.month, today.day)
    for line in wiki["content"].split("\n"):
        matches = regex.findall(line)
        for match in matches:
            line_date = datetime.strptime(match, '%Y-%m-%d')
            if line_date < today:
                skip = True
                break
        skip = False
        if skip:
            continue
        lines.append(line)

    content = "\n".join(lines)
    d.edit_text(obj, content)


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--slug", type=str, required=True)
    parser.add_argument("--object", type=str, required=True)
    args = parser.parse_args()
    factory = conduit.Factory()
    factory.token = args.token
    factory.host = args.host
    update(factory, args.slug, args.object)

if __name__ == '__main__':
    main()
