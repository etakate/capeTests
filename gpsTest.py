#!/usr/bin/env python
# GPS report adapted from Tim Reilly && Dan Mandle

from gps import *
from gpsOnOff import *
from gpsSettings import *

import datetime
import ntplib
import os
import pynmea2
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

    # Pass 2 Init sequence
    if str(iteration) == '2':
        gpsShutdown()
        bbr = 'cold'
        gpsReset(bbr)
        gpsStartup()

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
            success = False
            start = time.time()
            timeout = time.time() + 200 
            gpsp.start()
            os.system('clear')
            while time.time() < timeout:
                # Get incoming gps stream
                report = gpsp.get_current_value()

                if report != '':               
                    try: 
                        # Search for correct GPS info 'bucket'
                        if 'lon' not in report.keys():
                            continue
                        else:
                            # Verify coordinate lock 
                            if report['lon'] != '0.0' and report['lat'] != '0.0':
                                # Verify UTC time is established
                                if report['time']:
                                    success = True
                                    break
                                else:
                                    continue
                            else:
                                continue

                    except Exception as e:
                        # Reset stdout
                        sys.stdout = stdouttemp
                        print "FAIL - No GPS lock established; no GPS data collected."
                        sys.exit()
                        #print "Issues occurred during GPS testing: \n" + str(e)
                        #break

                else:
                    # Reset stdout
                    sys.stdout = stdouttemp
                    print "FAIL - No valid incoming GPS data - check antenna/UFL connection"
                    break

            try:
                # If GPS lock is successfully achieved, print report
                if success == True:
                    print "********************** BEGIN GPS DATA COLLECT FOR CAPE " + str(deviceID) + " --- PASS " + str(iteration)
                    print "********************** " + datetime.datetime.now().isoformat() + "\n"

                    gpsData(start, report)
                    gpsTime(report, iteration)

                    # if str(iteration) == '1':
                    #     gpsTimeInit(tdelta)
                    # else:
                    #     gpsTimeVerify(tdelta)
                    print "********************** END GPS DATA COLLECT --- PASS " + str(iteration) + "\n"

            except Exception as e:
                    print "FAIL - issues occurred with GPS data collection: \n" + str(e)

        except Exception as e:
            print "MAJOR FAIL - GPS is down. Time for troubleshooting: \n" + str(e)

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
 #   parser.add_argument('--bbr', choices=['hot', 'warm', 'cold'], default='cold', help='Specify the BBR sections to clear. Options: hot - warm - cold')
    args = parser.parse_args()

    if args.id is None:
        print("Missing arguments; cannot proceed.")
    else:
        print("Beginning GPS test...")
        iteration = args.iteration
        deviceID = args.id
        #if args.bbr is not None:
        #    bbr = args.bbr
        gpsTest(iteration, deviceID)
    