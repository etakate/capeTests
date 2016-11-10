#!/usr/bin/env python
# GPS report adapted from Tim Reilly && Dan Mandle

from gps import *
from gpsOnOff import *
from gpsSettings import *

import datetime
import ntplib
import os
import pynmea2
import re
import six
import subprocess
import sys
import time
import threading

# Save stdout for later...
stdouttemp = sys.stdout
 
save_path = "/home/sigma/controller/bin/logfiles/"

class gpsPoller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.session = gps(mode=WATCH_ENABLE)
        self.current_value = None 
        self.running = True 

    def get_current_value(self):
        return self.current_value

    def run(self):
        try:
            while self.running:
                self.current_value = self.session.next() 
        except StopIteration:
            pass

def gpsTest(iteration, deviceID):

    # Create GPS log file
    print "Collecting GPS info...."

    capeLogFile = os.path.join(save_path, deviceID + "_test_results.txt")
    with open(capeLogFile, 'a') as results:
        sys.stdout = results

        # gpsShutdown()
        # print "********************** BEGIN GPS SETTINGS VERIFICATION FOR CAPE " + str(deviceID) + " --- PASS " + str(iteration)
        # print "********************** " + datetime.datetime.now().isoformat() + "\n"
        # gpsSettings()
        # print "********************** END GPS SETTINGS VERIFICATION "
        # gpsStartup()

        # Collect GPS data
        gpsp = gpsPoller()
        try: 
            start = time.time()
            timeout = time.time() + 75 
            gpsp.start()
            while time.time() < timeout:
                os.system('clear')
                report = gpsp.get_current_value()

                if report != '':               
                    try: 
                        # Search for correct GPS info 'bucket'
                        # FFR - 'epx' and 'track' are normally stored in report.keys()[0]
                        if 'lon' not in report.keys():
                            continue
                        else:
                        	print "********************** BEGIN GPS DATA COLLECT FOR CAPE " + str(deviceID) + " --- PASS " + str(iteration)
                            print "********************** " + datetime.datetime.now().isoformat() + "\n"
                            # Verify coordinate lock 
                            if report['lon'] != '0.0' and report['lat'] != '0.0':
                                # Print report
                                gpsData(report)
                                gpsTime(report)
                                print "PASS - GPS lock established"
                            else:
                            	print "FAIL - No GPS lock established; no GPS data collected."
                            	break
                            print "********************** END GPS DATA COLLECT --- PASS " + str(iteration)

                    except Exception as e:
                        print "FAIL - issues occurred with reading GPS data: \n" + str(e)

                else:
                	print "FAIL - No valid incoming GPS data - check antenna/UFL connection"
                	sys.exit()

        except Exception as e:
        	print "FAIL - GPS is down. Time for troubleshooting: \n" + str(e)


        gpsp.running = False 
        gpsp.join()

        results.close()

    # Reset stdout
    sys.stdout = stdouttemp


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', '-it', choices=['1', '2'], help='Specify which iteration of the test you will be running (enter 1 or 2).')
    parser.add_argument('--id', help='Specify the cape ID, which should be the GSM IMEI.')
    args = parser.parse_args()

    if args.id is None:
        print("Missing arguments; cannot proceed.")
    else:
        print("Beginning GPS test...")
        iteration = args.iteration
        deviceID = args.id
        gpsTest(iteration, deviceID)