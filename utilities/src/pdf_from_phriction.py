#!/usr/bin/python
"""Convert a phriction doc to pdf."""
import argparse
import conduit
import phriction_conversion


def _get(factory, slug, output):
    """Get phriction content."""
    p = factory.create(conduit.Phriction)
    result = p.info(slug)['content']
    phriction_conversion._process(result, output)


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--slug", type=str)
    parser.add_argument("--output", required=True, type=str)
    args = parser.parse_args()
    factory = conduit.Factory()
    factory.token = args.token
    factory.host = args.host
    _get(factory, args.slug, args.output)

if __name__ == '__main__':
    main()
