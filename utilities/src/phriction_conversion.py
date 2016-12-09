#!/usr/bin/python
"""Handles consuming markdown and producing output pdf."""

import subprocess

converters = []


def asterisk_lists(content):
    """Convert asterisk pairs to tab asterisk."""
    working = content
    while "**" in working:
        working = working.replace("**", "\t*")
    return working

converters.append(asterisk_lists)


def _process(content, output):
    """process the input file."""
    result = content
    for converter in converters:
        result = converter(result)
    markdown = output + ".md"
    with open(markdown, 'w') as f:
        f.write(result)
    proc = subprocess.Popen(["pandoc",
                             markdown,
                             "--output",
                             output + ".pdf",
                             "--smart",
                             "-V",
                             "geometry:margin=0.7in"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    print(out)
    print(err)
    if proc.returncode != 0:
        raise Exception("{0} \n {1}".format(out.decode("ascii"),
                                            err.decode("ascii")))
