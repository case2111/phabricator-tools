#!/bin/bash
STATIC=/opt/phab/static/
ACTIVE=/opt/phacility/git/
ARCHIVED=/opt/phab/archived/git/dir/

rm -f ${STATIC}/*.gz

function tar-dir-files()
{
    cd $1
    for f in $(ls); do
        cd $1/$f && tar -zcf $STATIC/$f.gz *
    done
}

tar-dir-files $ACTIVE
tar-dir-files $ARCHIVED
