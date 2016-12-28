#!/usr/bin/python
"""Convert a phriction page to dashboard object."""
import argparse
import conduit

def update(factory, slug, obj):
    """Update an object (dashboard) from wiki."""
    p = factory.create(conduit.Phriction)
    d = factory.create(conduit.Dashboard)
    wiki = p.info(slug)
    d.edit_text(obj, wiki["content"])

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
