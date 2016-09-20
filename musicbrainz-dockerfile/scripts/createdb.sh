#!/bin/bash

FTP_HOST=ftp://ftp.musicbrainz.org
FETCH_DUMPS=$1

if [[ $2 != "" ]]; then
    FTP_HOST=$2
fi

if [[ $FETCH_DUMPS == "-fetch" ]]; then
  echo "fetching data dumps"
  python /download-data.py $FTP_HOST /media/dbdump
  /musicbrainz-server/admin/InitDb.pl --createdb --import /media/dbdump/mbdump*.tar.bz2 --echo
else
  echo "no dumps found or dumps are incomplete"
  /musicbrainz-server/admin/InitDb.pl --createdb --echo
fi
