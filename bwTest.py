#!/usr/bin/env python
# Credit for file_size & convert_bytes goes to Rajiv Sharma (found on StackOverflow)

import datetime
import os
import sys
from timeit import default_timer as timer
import time
import urllib
import urllib2

save_path = "/home/sigma/controller/bin/logfiles/"
download_path = "/home/sigma/controller/bin/download/"

def dir_check(download_path):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

hash = "\043"
urls = ["http://nexus.dtect.net/service/local/artifact/maven/content?r=snapshots&g=sigma&a=messages&v=0.9.5-SNAPSHOT&c=py&e=zip%ssigma" % hash,
	"http://nexus.dtect.net/service/local/artifact/maven/content?r=snapshots&g=sigma&a=sensor&v=LATEST&c=py&e=zip%ssigma" % hash,
	"http://nexus.dtect.net/service/local/artifact/maven/content?r=snapshots&g=sigma&a=data&v=LATEST&c=py&e=zip%ssigma" % hash,
	"http://nexus.dtect.net/service/local/artifact/maven/content?r=snapshots&g=sigma&a=device&v=LATEST&c=py&e=zip%ssigma" % hash]

def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)

def bwTest(deviceID):
    # Save stdout for later...
    stdouttemp = sys.stdout

    capeLogFile = os.path.join(save_path, deviceID + "_test_results.txt")         
    with open(capeLogFile, "a") as results:

        sys.stdout = results 
        print "********************** BEGIN BANDWIDTH DATA COLLECT FOR CAPE " + str(deviceID)
        print "********************** " + datetime.datetime.now().isoformat() + "\n"
        start = timer()

        dir_check(download_path)
        i = 0;
        for url in urls:
            try:
                i += 1
                urllib.urlretrieve(url, os.path.join(download_path, "url%d.zip" % i))
                print "Downloaded url%d.zip" % i
                print "File size: " + file_size(os.path.join(download_path, "url%d.zip" % i)) + "\n"
                success = True
            except Exception as e:
                print "Issues occurred downloading the file(s): " + str(e)
                # Reset stdout
                sys.stdout = stdouttemp
                print "TEST FAILED"
                print str(e)
                sys.exit()

        stop = timer()
        totalT = stop - start 
        print "Total download completed in " + str(totalT) + " seconds"

        if totalT > 60:
            print "Bandwidth speed is abnormally slow - check for issues."

        print "\n********************** END BANDWIDTH DATA COLLECT \n"
        # Reset stdout
        sys.stdout = stdouttemp
        print "TEST PASSED SUCCESSFULLY"


if __name__== '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Specify the cape ID, which should be the GSM IMEI.')
    args = parser.parse_args()

    if args.id is None:
        print("Missing argument(s); cannot proceed.")
    else:
        print("Beginning bandwidth test...")
        deviceID = args.id
        bwTest(deviceID)
