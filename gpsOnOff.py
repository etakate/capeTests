#!/usr/bin/env python

import os
import time

proc1 = "gpsd.socket"
proc2 = "gpsd.service"
proc3 = "/usr/sbin/gpsd -N /dev/ttyO5"


def gpsShutdown():
    # Shut down gpsd.socket
    print "Shutting down gpsd.socket..."
    try:
        os.system("systemctl stop " + proc1)
        time.sleep(5)
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
        time.sleep(5)
        tmp = os.popen("ps -Af").read()
        if proc2 not in tmp[:]:
            print "OK - gpsd.service down"
        else:
            print "FAIL - gpsd.service still up"
    except Exception as e:
        print "Issues occurred during gpsd.service shutdown: \n" + str(e)

def gpsStartup():
    # Startup gpsd
    print "Starting up gpsd..."
    try:
        os.system("/etc/init.d/gpsd start")
        timeout = time.time() + 45
        while time.time() < timeout:
            time.sleep(5)
            tmp = os.popen("ps -Af").read()
            if proc3 not in tmp[:]:
                print "FAIL - gpsd still down"
            else:
                print "OK - gpsd back up"
                break
    except Exception as e:
        print "Issues occurred during gpsd startup: \n" + str(e)
