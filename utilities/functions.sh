#!/bin/bash
INFO_MODE="[INFO]"
CACHE="/var/cache/phabricator-tools/"

function phabricator_encode() {
    _py="
import sys
import urllib.parse

print(urllib.parse.quote(sys.stdin.read()))"
    echo "$@" | python -c "$_py"
}

function info_mode() {
    echo "$INFO_MODE $@"
}