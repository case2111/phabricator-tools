#!/usr/bin/python
"""Check the git version of an item."""

import subprocess
import os


def _version(in_path):
    """process the input file."""
    version = "unknown"
    if os.path.exists(full):
        with open(full, 'r') as f:
            version = f.read()
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
        return "{0}\n\n```\n{1}\n```".format(version, out.decode("ascii"))
    else:
        raise Exception("{0} \n {1}".format(out.decode("ascii"),
                                            err.decode("ascii")))
