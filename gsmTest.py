#!/usr/bin/env python

# OUTLINE
# Turn off essential services -- make sure sigma-controller.py is shut down (script restarts ppp)
# Shut down pppd
# Verify GSM settings are correct -- log
# Collect GSM information -- log
# Restart essential services

from gsmSettings import *
from gsmOnOff import *

import argparse
import datetime
import gps
import serial
import select
import time
import os
import os.path
import subprocess
import signal
import sys

# Save stdout for later...
stdouttemp = sys.stdout
save_path = "/home/sigma/controller/bin/logfiles/"

def gsmTest(iteration, deviceID):
    gsmShutdown()

    # Open serial connection to GSM module
    com = serial.Serial("/dev/ttyO4", 921600)
    fd = com.fileno()

    # Create GSM log file
    print "Collecting GSM info...."

    capeLogFile = os.path.join(save_path, deviceID + "_test_results.txt")
    with open(capeLogFile, 'a') as results:
        sys.stdout = results

        print "********************** BEGIN GSM SETTINGS VERIFICATION FOR CAPE " + str(deviceID) + " --- PASS " + str(iteration)
        print "********************** " + datetime.datetime.now().isoformat() + "\n"

        if str(iteration) == '1':
            # Run Pass 1
            gsmSettingsInit()
        else:
        	# Run Pass 2
            gsmSettingsVerify()

        print "********************** END GSM SETTINGS VERIFICATION --- PASS " + str(iteration)

        # Collect GSM information
        print "********************** BEGIN GSM DATA COLLECT FOR CAPE " + str(deviceID) + " --- PASS " + str(iteration)
        gsmData()
        print "********************** END GSM DATA COLLECT --- PASS " + str(iteration)

        # Close serial connection to GSM module
        com.close()

        # Reset stdout
        sys.stdout = stdouttemp
        gsmStartup()


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', '-it', choices=['1', '2'], help='Specify which iteration of the test you will be running (enter "1" or "2").')
    parser.add_argument('--id', help='Specify the cape ID, which should be the GSM IMEI.')
    args = parser.parse_args()

    if args.id is None:
        print("Missing arguments; cannot proceed.")
    else:
        print("Beginning GSM test..."")
        iteration = args.iteration
        deviceID = args.id
        gsmTest(iteration, deviceID)

