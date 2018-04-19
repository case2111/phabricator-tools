#!/bin/bash
STATIC=/opt/phab/static/
ACTIVE=/opt/phacility/git/
ARCHIVED=/opt/phab/archived/git/dir/
HTML='
<!DOCTYPE HTML>
<html lang="en-US">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" contents="5;url=FILENAME" />
        <title>nightly build of FILENAME</title>
    </head>
    <body>
    you should be automatically redirected shortly...(or click <a href="FILENAME">here</a>)
	</body>
</html>
'

rm -f ${STATIC}/*.gz
rm -f ${STATIC}/*.html
TODAY=$(date +%Y%m%d)

function tar-dir-files()
{
    cd $1
    for f in $(ls); do
        file_name=$f$TODAY.gz
        cd $1/$f && tar -zcf $STATIC/$file_name *
        echo $HTML | sed "s/FILENAME/$file_name/g" > $STATIC/$f.html
    done
}

tar-dir-files $ACTIVE
tar-dir-files $ARCHIVED
