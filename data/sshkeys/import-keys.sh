#!/bin/bash
_sync() {
    CONFIG=/etc/epiphyte.d/environment
    if [ ! -e $CONFIG ]; then
        echo "Could not find $CONFIG"
        exit 1
    fi
    dos2unix $CONFIG > /dev/null 2>&1
    source $CONFIG
    if [ -z "$1" ]; then
        echo "a key value is required"
        exit 1
    fi
    KEY=$1
    USER_NAME=$(echo "$KEY" | cut -d "-" -f 1)
    #| tr '[:upper:]' '[:lower:]')
    if [ -z $USER_NAME ]; then
        echo "invalid $KEY"
        exit 1
    fi
    USER_HOME="/home/$USER_NAME/"
    if [ ! -d $USER_HOME ]; then
        echo "$USER_HOME is not configured"
        exit 1
    fi
    SSH_HOME=$USER_HOME".ssh/"
    if [ ! -d $SSH_HOME ]; then
        echo "$SSH_HOME does not exist"
        exit 1
    fi
    if [ -z "$SSH_COMMAND" ]; then
        echo "no ssh command set"
        exit 1
    fi
    ACTUAL_VAL="SSH_"$(echo $KEY | tr '[:lower:]' '[:upper:]' | sed "s/-/_/g")
    USERS=${!ACTUAL_VAL}
    if [ -z "$USERS" ]; then
        echo "$CONFIG does not have a key for $ACTUAL_VAL"
        exit 1
    fi
    _tmp=$(mktemp)
    echo "# "$(date) > $_tmp
    for u in $(echo "$USERS"); do
        echo "# user: $u" >> $_tmp
        $SSH_COMMAND/${u}-keys >> $_tmp
        if [ $? -ne 0 ]; then
            echo "$u (ssh issue?)"
        fi
    done
    c=$(cat $_tmp | sed "/^$/d" | grep -v "^#" | wc -l)
    if [ $c -lt 1 ]; then
        echo "no keys, not updating..."
        exit 1
    fi
    SSH_KEYS=${SSH_HOME}authorized_keys
    mv $_tmp ${SSH_KEYS}
    chown $USER_NAME:$USER_NAME $SSH_KEYS
    chmod 600 $SSH_KEYS
}

_sync "$@" | systemd-cat -p err -t sshkeys
