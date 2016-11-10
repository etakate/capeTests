#!/usr/bin/env python

import serial
import select
import time
import datetime
import os
import sys
import shlex
import subprocess

# Save stdout for later...
stdouttemp = sys.stdout
save_path = "/home/sigma/controller/bin/logfiles/"


def cellTest(deviceID):
    capeLogFile = os.path.join(save_path, deviceID + "_test_results.txt")
    with open(capeLogFile, 'a') as results:
        sys.stdout = results
        success = False

        print "********************** BEGIN CELL NETWORK DATA COLLECT FOR CAPE " + str(deviceID)
        print "********************** " + datetime.datetime.now().isoformat()

        # Run cell network test
        cmd = shlex.split("ping -c10 google.com")
        try:
           output = subprocess.check_output(cmd)
           show = str(output)
           print show
        except subprocess.CalledProcessError as e:
            print "Cell network test complete - The cell network is DOWN".format(cmd[-1])
            print str(e)
        else:
            print "Cell network test complete - The cell network is UP".format(cmd[-1])
            success = True

        print "\n********************** END CELL NETWORK DATA COLLECT \n"

        # Reset stdout
        sys.stdout = stdouttemp
        if success == True:
            print "TEST PASSED SUCCESSFULLY"
        else:
            print "TEST FAILED - check logfile"


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Specify the cape ID, which should be the GSM IMEI.')
    args = parser.parse_args()

    if args.id is None:
        print("Missing argument(s); cannot proceed.")
    else:
        print("Beginning cell network test...")
        deviceID = args.id
        cellTest(deviceID)