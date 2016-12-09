#!/usr/bin/python
"""Edits a phriction page from source."""

import argparse
import conduit
import base64
import csv
import io

CSV_CONVERT = "csv"


def _process(factory, slug, title, path, callsign, branch, convert):
    """process the input file."""
    converter = raw
    if convert is not None:
        if convert == CSV_CONVERT:
            converter = from_csv
    d = factory.create(conduit.Diffusion).filecontent_by_path_branch(path,
                                                                     callsign,
                                                                     branch)
    f = factory.create(conduit.File).download(d["filePHID"])
    b = base64.b64decode(f).decode("ascii")
    b = converter(b)
    p = factory.create(conduit.Phriction)
    post_content = """
> this page is managed externally, do NOT edit it here.
> to change, use the r{1} repository and edit the {0} file in the {2} branch

{3}
""".format(path, callsign, branch, b)
    p.edit(slug, title, post_content)


def raw(content):
    """raw content."""
    return content


def from_csv(content):
    """csv conversion."""
    buf = io.StringIO(content)
    reader = csv.reader(buf, delimiter=",")
    segments = {}
    for row in reader:
        main = row[0]
        secondary = row[1]
        if main not in segments:
            segments[main] = {}
        if secondary not in segments[main]:
            segments[main][secondary] = []
        segments[main][secondary].append(row[2:])
    last_item = None
    last_sub = None
    lines = []
    for item in sorted(segments.keys()):
        if last_item != item:
            lines.append("\n---\n\n# {0}\n\n---\n".format(item))
            last_sub = None
        sub = segments[item]
        for area in sorted(sub.keys()):
            if area != last_sub:
                lines.append("\n## {0}\n".format(area))
            last_sub = area
            note = None
            area_lines = []
            for sect in sub[area]:
                name = sect[0]
                data = sect[1]
                use = data
                is_note = name == "Note"
                if not is_note:
                    use = name + "\n" + use
                sect_line = "```\n{0}\n```".format(use)
                if is_note:
                    note = sect_line
                else:
                    area_lines.append(sect_line)
            if note is not None:
                lines.append(note)
            for out in sorted(area_lines):
                lines.append(out)
        last_item = item
    return "\n".join(lines)


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
    parser.add_argument("--convert", default=None, type=str,
                        choices=[CSV_CONVERT])
    args = parser.parse_args()
    factory = conduit.Factory()
    factory.token = args.token
    factory.host = args.host
    _process(factory,
             args.slug,
             args.title,
             args.path,
             args.callsign,
             args.branch,
             args.convert)

if __name__ == '__main__':
    main()
