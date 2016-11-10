#!/usr/bin/env python

import datetime
import os
import time


def gpsBaud:
    # Set new baudrate
    try:
        os.system('stty speed 115200 </dev/ttyO5')
        time.sleep(1)
    except Exception as e:
        print 'Issue occurred setting the baudrate: \n' + str(e)


def gpsSettings:
    # Talker IDs
    talkers = ['$GL', '$GB', '$GA']
    # Header IDs
    headerids = ['GGA', 'RMC', 'TXT', 'GBQ', 'GLQ', 'GPQ', 'GNQ']
    try:
        os.system('timeout 30 cat /dev/ttyS5 | tee tmp_gps.txt')
        GPSset = True

        with open('tmp_gps.txt', 'r') as gps_strings:
            for line in [ line for line in gps_strings if line != '']:

                if line[0:3] in talkers:
                    GPSset = False
                    break
                    pass
                elif line[3:6] not in headerids:
                    GPSset = False
                    break
                else:
                    pass

            if GPSset == False:
                print 'GPS satellite filtering was not saved. Check configuration.'
            else:
                print 'GPS satellite filtering saved successfully. Configuration OK.'

    except Exception as e:
        print 'Something is wrong with the serial connection to the GPS module. \n' + str(e)


def gpsData(report):
    # Print report
    stop = time.time()
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

    elapsed = stop - start
    print "Time to Positioning Lock: ", elapsed , " seconds"

    # Additional GPS fields available:
    # print 'EPS: ' , report['eps']
    # print 'EPV: ' , report['epv']
    # print 'EPX: ' , report['epx']
    # print 'Climb: ' , report['climb']


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


def gpsTime(report):
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

        # td = timedelta object
        td = n - g
        tdelta_pass1 = calc_delta(td)

        if isinstance(tdelta_pass1, six.string_types):
            print 'GPS time differs from NTP time by minutes or hours [' + tdelta_pass1 + ']. Difference is not acceptable, something needs help.'
        else:
            if -5 > tdelta_pass1 or tdelta_pass1 > 5:
                print 'GPS time differs from NTP time by ' + str(tdelta_pass1) + ' seconds. Difference is not acceptable.'
            else:
                print 'GPS time differs from NTP time by ' + str(tdelta_pass1) + ' seconds. Difference is within acceptable range.'

            # Write GPS time test pass 1 results for later comparison
            with open('tmp_gpstd.txt', 'w') as f:
                f.write('{0}\n'.format(tdelta_pass1))
                f.close()    

            break

    except Exception as e:
        print 'Something happened during the GPS time check: ' + str(e)






