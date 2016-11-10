#!/usr/bin/env python

import os
import time

proc1 = "gpsd.socket"
proc2 = "gpsd.service"


def gpsShutdown:
    # Shut down gpsd.socket
    print "Shutting down gpsd.socket..."
    try:
        os.system("systemctl stop " + proc1)
        time.sleep(10)
        tmp = os.popen("ps -Af").read()
        if proc1 not in tmp[:]:
            print "OK - gpsd.socket down"
         else:
            print "FAIL - gpsd.socket still up"
    except Exception as e:
        print "Issues occurred during gpsd.socket shutdown: \n" + str(e)

    # Shut down gpsd.service
    print "Shutting down gpsd.service..."
    try:
        os.system("systemctl stop " + proc2)
        time.sleep(10)
        tmp = os.popen("ps -Af").read()
        if proc2 not in tmp[:]:
            print "OK - gpsd.service down"
        else:
            print "FAIL - gpsd.service still up"
    except Exception as e:
        print "Issues occurred during gpsd.service shutdown: \n" + str(e)

def gpsStartup:
    # Startup gpsd.socket
    print "Starting up gpsd.socket..."
    try:
        os.system("/etc/init.d/gpsd start")
        time.sleep(10)
        tmp = os.popen("ps -Af").read()
        if proc1 not in tmp[:]:
            print "FAIL - gpsd.socket still down"
         else:
            print "OK - gpsd.socket back up"
    except Exception as e:
        print "Issues occurred during gpsd.socket shutdown: \n" + str(e)
