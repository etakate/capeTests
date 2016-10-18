#!/usr/bin/env python

import serial
import select
import time
import datetime
import os
import sys
import shlex
import subprocess


save_path = '/home/sigma/controller/bin/logfiles/'
name_of_file = raw_input("Enter cape ID [Format: CAxxx] : ")

# Create GSM log file
capeGSMLogFile = os.path.join(save_path, name_of_file+"_test_results.txt")
with open(capeGSMLogFile, 'a') as results:
    sys.stdout = results

    print "********************** BEGIN CELL NETWORK DATA COLLECT FOR " + name_of_file + " **********************"
    print "********************** " + datetime.datetime.now().isoformat() + " ***************************\n"

    # Run cell network test
    cmd = shlex.split("ping -c10 dtect.net")
    try:
       output = subprocess.check_output(cmd)
       show = str(output)
       print show
    except subprocess.CalledProcessError:
        print "Cell network test complete - The cell network is DOWN".format(cmd[-1])
    else:
        print "Cell network test complete - The cell network is UP".format(cmd[-1])

    print "\n********************** END CELL NETWORK DATA COLLECT  **********************"
