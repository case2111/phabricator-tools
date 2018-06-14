#!/bin/bash
STATIC=/opt/phab/static/
ACTIVE=/opt/phacility/git/
ARCHIVED=/opt/phab/archived/git/dir/

rm -f ${STATIC}/*.gz
rm -f ${STATIC}/*.html
TODAY=$(date +%Y%m%d)

function tar-dir-files()
{
    cd $1
    for f in $(ls); do
        file_name=$f$TODAY.gz
        cd $1/$f && tar -zcf $STATIC/$file_name *
    done
}

tar-dir-files $ACTIVE
tar-dir-files $ARCHIVED
