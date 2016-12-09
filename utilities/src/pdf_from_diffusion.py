#!/usr/bin/python
"""Convert a diffusion markdown path to pdf."""
import phriction_conversion
import base64
import argparse
import conduit


def _get(factory, path, callsign, branch, output):
    """get the artifact."""
    if not path.endswith(".md"):
        raise Exception("only md files are supported for conversion")
    d = factory.create(conduit.Diffusion).filecontent_by_path_branch(path,
                                                                     callsign,
                                                                     branch)
    f = factory.create(conduit.File).download(d["filePHID"])
    b = base64.b64decode(f).decode("ascii")
    phriction_conversion._process(b, output)


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--output", required=True, type=str)
    parser.add_argument("--path", type=str, required=True)
    parser.add_argument("--callsign", type=str, required=True)
    parser.add_argument("--branch", type=str, required=True)
    args = parser.parse_args()
    factory = conduit.Factory()
    factory.token = args.token
    factory.host = args.host
    _get(factory, args.path, args.callsign, args.branch, args.output)

if __name__ == '__main__':
    main()
