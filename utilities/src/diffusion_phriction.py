#!/usr/bin/python
"""Edits a phriction page from source."""

import argparse
import conduit
import base64


def _process(factory, slug, title, path, callsign, branch):
    """process the input file."""
    if not path.endswith(".md"):
        raise Exception("only markdown files are allowed")
    d = factory.create(conduit.Diffusion).filecontent_by_path_branch(path,
                                                                     callsign,
                                                                     branch)
    f = factory.create(conduit.File).download(d["filePHID"])
    b = base64.b64decode(f).decode("ascii")
    p = factory.create(conduit.Phriction)
    post_content = """
> this page is managed externally, do NOT edit it here.
> to change, use the r{1} repository and edit the {0} file in the {2} branch

---

{3}
""".format(path, callsign, branch, b)
    p.edit(slug, title, post_content)


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, type=str)
    parser.add_argument("--token", required=True, type=str)
    parser.add_argument("--slug", required=True, type=str)
    parser.add_argument("--title", required=True, type=str)
    parser.add_argument("--path", required=True, type=str)
    parser.add_argument("--callsign", required=True, type=str)
    parser.add_argument("--branch", required=True, type=str)
    args = parser.parse_args()
    factory = conduit.Factory()
    factory.token = args.token
    factory.host = args.host
    _process(factory,
             args.slug,
             args.title,
             args.path,
             args.callsign,
             args.branch)

if __name__ == '__main__':
    main()
