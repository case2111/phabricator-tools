#!/usr/bin/python
"""Check the git version of an item."""

import subprocess


def _version(path):
    """process the input file."""
    proc = subprocess.Popen(["git",
                             "--git-dir",
                             path + "/.git",
                             "log",
                             "-n",
                             "1"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    print(out)
    print(err)
    if proc.returncode == 0:
        return '```\n' + out.decode("ascii") + "\n```"
    else:
        raise Exception("{0} \n {1}".format(out.decode("ascii"),
                                            err.decode("ascii")))
