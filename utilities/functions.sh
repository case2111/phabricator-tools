#!/bin/bash
function phabricator_encode() {
    _py="
import sys
import urllib.parse

print(urllib.parse.quote(sys.stdin.read()))"
    echo "$@" | python -c "$_py"
}
