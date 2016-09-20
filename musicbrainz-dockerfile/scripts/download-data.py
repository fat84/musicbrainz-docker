#!/usr/bin/env python

import os
import sys
from ftplib import FTP
from subprocess import check_output

FILE_LIST = [
    "mbdump.tar.bz2",
    "mbdump-cdstubs.tar.bz2",
    "mbdump-cover-art-archive.tar.bz2",
    "mbdump-derived.tar.bz2",
    "mbdump-documentation.tar.bz2",
    "mbdump-editor.tar.bz2",
    "mbdump-stats.tar.bz2",
    "mbdump-wikidocs.tar.bz2",
]
LATEST_PATH = "/pub/musicbrainz/data/fullexport"
LATEST_FILE = "LATEST"
MD5SUMS_FILE = "MD5SUMS"

bin_data = ""
def handle_binary(data):
    global bin_data
    bin_data += data

if len(sys.argv) < 3:
    print "Usage: %s <FTP host> <dest dir>" % (sys.argv[0], sys.argv[1])
    sys.exit(-1)

host = sys.argv[1]
dest = sys.argv[2]

ftp = FTP(host)
ftp.login()
ftp.cwd(LATEST_PATH)
ftp.retrbinary('RETR %s' % LATEST_FILE, callback=handle_binary)

latest = bin_data.strip()
print "Latest data dump is:", latest
ftp.cwd(latest.strip())

bin_data = ""
ftp.retrbinary('RETR %s' % MD5SUMS_FILE, callback=handle_binary)
sums = bin_data.split("\n")

for line in sums:
    if not line:
        continue

    md5, file_name = line.split(" ", 1)
    file_name = file_name[1:]

    if not file_name in FILE_LIST:
        continue

    print "%s:" % file_name
    dest_file = os.path.join(dest, file_name)
    if os.path.exists(dest_file):
        print "   exists, checking MD5:",
        sys.stdout.flush()

        sum_file = check_output(["md5sum", dest_file])
        file_sum, dummy, file = sum_file.split(" ")
        if file_sum != md5:
            print "\n   local copy does not match remote copy. Nuking local file."
            os.unlink(dest_file)
        else:
            print "ok"

    if not os.path.exists(dest_file):
        while True:
            print "   downloading: ",
            sys.stdout.flush()
            ftp.retrbinary('RETR %s' % file_name, open(dest_file, 'wb').write)
            sum_file = check_output(["md5sum", dest_file])
            file_sum, dummy, file = sum_file.split(" ")
            if file_sum != md5:
                print "\n   Downloaded copy does not match remote copy. Ugh. Re-downloading."
                os.unlink(dest_file)
            else:
                print "\n   done, verified."
                break


ftp.quit()
