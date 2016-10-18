#! /usr/bin/env python
# GPS report adapted from Tim Reilly && Dan Mandle
 
# OUTLINE
# Turn off gps services -- needed to communicate over serial connection with GPS device
# Verify GPS settings have persisted -- log
# Restart gps services -- needed for GPS data collection
# Collect GPS information again -- log
# Compare time -- log

import datetime
from gps import *
import ntplib
import os
import pynmea2
import re
import six
import subprocess
import sys
from time import *
import time
import threading

# Save stdout for later...
stdouttemp = sys.stdout
 
save_path = '/home/sigma/controller/bin/logfiles/'
name_of_file = raw_input("Enter cape ID [Format: CAxxx] : ")

proc1 = 'gpsd.socket'
proc2 = 'gpsd.service'

# Shut down gpsd.socket
print 'Shutting down gpsd.socket...'
try:
    os.system('systemctl stop ' + proc1)
    time.sleep(10)
    tmp = os.popen('ps -Af').read()
    if proc1 not in tmp[:]:
        print 'OK'
    else:
        print 'gpsd.socket still up'
except Exception as e:
    print 'Issue occurred shutting down gpsd.socket: \n' + str(e)

# Shut down gpsd.service
print 'Shutting down gpsd.service...'
try:
    os.system('systemctl stop ' + proc2)
    time.sleep(10)
    tmp = os.popen('ps -Af').read()
    if proc2 not in tmp[:]:
        print 'OK'
    else:
        print 'gpsd.service still up'
except Exception as e:
    print 'Issue occurred shutting down gpsd.service: \n' + str(e)

# Set new baudrate
try:
    os.system('stty speed 115200 </dev/ttyO5')
    time.sleep(1)
except Exception as e:
    print 'Issue occurred setting the baudrate: \n' + str(e)


class GpsPoller(threading.Thread):

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

# Calculate GPS/NTP difference
def calc_delta(td):
    try:
        tdh = td.seconds//3600
        tdm = (td.seconds//60)%60
        tds = float(str(td.seconds) + '.' + str(td.microseconds))
        if tdh != 0 or tdm != 0:
            tdelta = str(tdh) + ':' + str(tdm) + ':' + str(tds)
        else:
            tdelta = tds
    except Exception as e:
        print str(e)
    return tdelta

if __name__ == '__main__':

    print 'Starting GPS Pass 2...'

    # Start GPS Log File
    capeGPSLogFile = os.path.join(save_path, name_of_file+"_test_results.txt")
    with open(capeGPSLogFile, 'a') as results:
        sys.stdout = results

        # Verify GPS Settings
        print '********************** BEGIN GPS SETTINGS VERIFICATION FOR ' + name_of_file + ' --- PASS 2 --- **********************'
        print '********************** ' + datetime.datetime.now().isoformat() + ' *************************** \n'

        talkers = ['$GL', '$GB', '$GA']
#        headerids = ['GGA', 'RMC', 'TXT', 'GBQ', 'GLQ', 'GPQ', 'GNQ']
        try:
            os.system('timeout 30 cat /dev/ttyS5 | tee tmp_gps.txt')
            GPSset = True

            with open('tmp_gps.txt', 'r') as gps_strings:
                for line in [ line for line in gps_strings if line != '']:

                    if line[0:3] in talkers:
                        GPSset = False
                        break
#                   elif line[3:6] not in headerids:
#                       GPSset = False
#                       break
                    else:
                        pass

                if GPSset == False:
                    print 'GPS satellite filtering did not persist on reboot. Check configuration.'
                else:
                    print 'GPS satellite filtering persisted successfully on reboot. Configuration OK.'

        except Exception as e:
            print 'Something is wrong with the serial connection to the GPS module. \n' + str(e)

        print '\n*************************** END GPS SETTINGS VERIFICATION --- PASS 2 --- *************************** \n'

        # Restart gpsd -- must be on for GPS data collect to occur successfully!
        try:
            os.system('/etc/init.d/gpsd start')
            time.sleep(3)
            tmp = os.popen('ps -Af').read()
            if 'gpsd' not in tmp[:]:
                os.system('/etc/init.d/gpsd start')
                time.sleep(3)
                tmp = os.popen('ps -Af').read()
            else:
                pass
        except Exception as e:
            print 'Something happened: \n' + str(e)


        # Collect GPS data
        gpsp = GpsPoller()
        data = False
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
                        # FFR - 'epx' is normally stored in report.keys()[0]
                        if 'lon' not in report.keys():
                            continue

                        else:
                            # Verify coordinate lock 
                            if report['lon'] != '0.0' and report['lat'] != '0.0':

                                # Print report
                                stop = time.time()
                                data = True
                                print "********************** BEGIN GPS DATA COLLECT FOR " + name_of_file + " --- PASS 2 --- **********************"
                                print "********************** " + datetime.datetime.now().isoformat() + " ***************************\n"
                                print 'Latitude: ' , report['lat']
                                print 'Longitude: ' , report['lon']
                                print 'Time UTC: ' , report['time']
                                if 'alt' not in report.keys():
                                    print 'Altitude (m): [not reported]'
                                else:
                                    print 'Altitude (m): ' , report['alt']
                                if 'speed' not in report.keys():
                                    print 'Speed (m/s): [not reported]'
                                else:
                                    print 'Speed (m/s): ' , report['speed']
                                print 'Track: ' , report['track']
                                print 'Mode: ' , report['mode']
                                if 'ept' not in report.keys():
                                    print 'EPT: [not reported]'
                                else:
                                    print 'EPT: ' , report['ept']
# Additional GPS fields available
#                                print 'EPS: ' , report['eps']
#                                print 'EPV: ' , report['epv']
#                                print 'EPX: ' , report['epx']
#                                print 'Climb: ' , report['climb']
                                elapsed = stop - start
                                print "Time to Positioning Lock: ", elapsed , " seconds"

                                # Check current GPS time
                                try:
                                    os.system('ntpdate -u time.nist.gov')
                                    gps = report['time']
                                    cmd = datetime.datetime.now()
                                    gt = re.split("T|Z", str(gps))
                                    gpstime = '%s%s' % (gt[1], '000')
                                    ntptime = re.split("\s", str(cmd))
                                    print '\nChecking GPS time....'
                                    print 'GPS: ' + gpstime
                                    print 'NTP: ' + ntptime[1]

                                    g = datetime.datetime.strptime(gpstime, '%H:%M:%S.%f')
                                    n = datetime.datetime.strptime(ntptime[1], '%H:%M:%S.%f')

                                    td = n - g
                                    tdelta_pass2 = calc_delta(td)

                                    if isinstance(tdelta_pass2, six.string_types):
                                        print 'GPS time differs from NTP time by minutes or hours [' + tdelta_pass2 + ']. Difference is not acceptable, something needs help.'
                                    else:
                                        if -2.0 > tdelta_pass2 or tdelta_pass2 > 2.0:
                                            print 'GPS time differs from NTP time by ' + str(tdelta_pass2) + ' seconds. Difference is not acceptable.'
                                        else:
                                            print 'GPS time differs from NTP time by ' + str(tdelta_pass2) + ' seconds. Difference is within acceptable range.'

                                        # Compare GPS time test pass 1 to pass 2
                                        #with open('tmp_gpstd.txt', 'r') as f:
                                         #   tdelta_pass1 = f.read()
                                        pass1 = [line.rstrip('\n') for line in open('tmp_gpstd.txt')]
                                        tdelta_pass1 = pass1[0]
                                        td_diff = float(tdelta_pass2) - float(tdelta_pass1)
                                        print '\nGPS time offset difference between Pass 1 and Pass 2: ' + str(td_diff)
                                        if -3.0 > td_diff or td_diff > 3.0:
                                            print td_diff
                                            print "GPS time offset differs significantly from pass 1."
                                        else:
                                            print 'GPS time offset OK.'
 
                                        print "\n********************** END GPS DATA COLLECT  --- PASS 2 --- **********************\n"
                                        break

                                except Exception as e:
                                    print 'Something happened during the GPS time verification: ' + str(e)

                            else:
                                if time.time() > timeout:
                                    print 'GPS lock not established within 60 seconds. No data collected.'
                                    break
                                else:
                                    print 'No GPS lock yet...'
                                    continue

                    except(AttributeError, KeyError) as e:
                        print str(e)
                        pass

                else:
                    try:
                        to = time.time() + 30
                        print 'No GPS data coming in, restarting....'
                        while time.time() < to:
                            tmp = os.popen('ps -Af').read()
                            if 'gpsd' not in tmp[:]:
                                os.system('/etc/init.d/gpsd restart')
                                continue
                            else:
                                print 'gpsd restarted'
                                pass
                                #break
                    except Exception as e:
                        print 'ERROR: CHECK GPS!'
                        print str(e)

            if time.time() > timeout and data is not True:
                print 'GPS data not found within 75 seconds. No data collected.'
            else:
                pass
                
        except Exception as e:
            print 'Failed. GPS is down.' + str(e)
        gpsp.running = False 
        gpsp.join()

        results.close()

# Reset stdout
sys.stdout = stdouttemp
