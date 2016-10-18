#!/usr/bin/env python

# OUTLINE
# Turn off essential services -- make sure sigma-controller.py is shut down (script restarts ppp)
# Shut down pppd
# Verify GSM settings have persisted post-reboot -- log
# Restart essential services

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

save_path = '/home/sigma/controller/bin/logfiles/'
name_of_file = raw_input('Enter cape ID [Format: CAxxx] : ')

proc1 = 'sigma-controller.py' 
proc2 = 'sigma-messenger.py'
proc3 = 'pppd'

# Shut down sigma-controller.py
print 'Shutting down sigma-controller...'
try:
    os.system(proc1 + ' stop')
    time.sleep(3)
    tmp = os.popen('ps -Af').read() 
    if proc1 not in tmp[:]: 
        print 'OK'
    else:
        print 'sigma-controller.py still up'
except Exception as e:
    print 'Something happened: \n' + str(e) 

# Shut down sigma-messenger.py
print 'Shutting down sigma-messenger...'
try:
    os.system(proc2 + ' stop')
    time.sleep(3)
    tmp = os.popen('ps -Af').read() 
    if proc2 not in tmp[:]: 
        print 'OK'
    else:
        print 'sigma-messenger.py still up'
except Exception as e:
    print 'Something happened: \n' + str(e) 

# Shut down pppd
print 'Shutting off pppd...'
try:
    os.system("kill $(pidof pppd)")
    time.sleep(3)
    tmp = os.popen("ps -Af").read() 
    if proc3 not in tmp[:]: 
        print 'OK'
    else:
        print 'pppd still up'
except Exception as e:
    print 'Something happened: \n' + str(e) 

# Open serial connection to GSM module
com = serial.Serial('/dev/ttyO4', 921600)
fd = com.fileno()

# Send to GSM module
def send(data):
    com.write(data + '\r')
    resp = []
    while select.select([fd], [], [], 1.0)[0]:
        resp.append(os.read(fd, 512))
    resp = ''.join(resp).split('\r\n')
    return [r for r in resp if r]

# Create GSM log file
print 'Collecting GSM info....'

capeGSMLogFile = os.path.join(save_path, name_of_file+'_test_results.txt')         
with open(capeGSMLogFile, 'a') as results:
    sys.stdout = results

    print '********************** BEGIN GSM SETTINGS VERIFICATION FOR ' + name_of_file + ' --- PASS 2 --- **********************'
    print '********************** ' + datetime.datetime.now().isoformat() + ' *************************** \n'

    # Check stored settings persisted post-reboot
    print "Verifying settings..."

    if '921600' in send('at+ipr?')[1] and send('at&v')[3] == send('at&v')[11]:
        gsm_pass2 = 'Profile Saved'        
    else:
        gsm_pass2 = 'Profile NOT Saved'

    pass1 = [line.rstrip('\n') for line in open('tmp_gsm.txt')]
    gsm_pass1 = pass1[0]

    if gsm_pass2 == gsm_pass1:
        print "GSM verification checks PASSED -- settings are persistent."
    else:
        print "GSM verification checks FAILED -- settings did not persist."

    print '*************************** END GSM SETTINGS VERIFICATION --- PASS 2 --- *************************** \n'

    # Collect GSM information

    # For reference:
    #     at+cgsn = IMEI of GSM module
    #     ati = Model of GSM module
    #     at+cnum  = Phone number of current SIM card
    #     at+csq = Cell signal quality of GSM module
    #     at+ccid = CCID of GSM module
    #     at+ipr = Baudrate of DCE

    print '********************** BEGIN GSM DATA COLLECT FOR ' + name_of_file + ' --- PASS 2 --- **********************'
    print 'IMEI: ' + send('at+cgsn')[1]
    print 'Model: ' + send('ati')[1]
    print 'Phone number: ' + send('at+cnum')[1]
    print send('at+csq')[1]
    print send('at+ccid?')[1]
    print 'Current configuration settings: ' 
    print send('at&v')
    print '*************************** END GSM DATA COLLECT --- PASS 2 --- *************************** \n'

# Close serial connection to GSM module
com.close()

# Reset stdout
sys.stdout = stdouttemp

# Restart sigma-controller.py
print 'Turning on sigma-controller...'
try:
    os.system(proc1 + ' start')
    tmp = os.popen('ps -Af').read() 
    if proc1 not in tmp[:]: 
        newprocess = "nohup python %s &" % (proc1)
        os.system(proc1 + ' start')  
        time.sleep(3)
    else:
        print 'sigma-controller.py is back up'
except Exception as e:
    print 'Something happened: \n' + str(e) 

# Restart sigma-messenger.py
print 'Turning on sigma-messenger...'
try:
    os.system(proc2 + ' start')
    tmp = os.popen('ps -Af').read() 
    if proc2 not in tmp[:]: 
        newprocess = "nohup python %s &" % (proc2)
        os.system(proc2 + ' start')
    else:
        print 'sigma-messenger.py is back up'
except Exception as e:
    print 'Something happened: \n' + str(e) 

# Restart pppd
print 'Turning on pppd...'
try:
    os.system('pon att')
    tmp = os.popen('ps -Af').read() 
    if proc3 not in tmp[:]: 
        while True:
            newprocess = "nohup python %s &" % (proc3)
            os.system(proc3 + '-dns start')
    else:
        print 'pppd is back up'
except Exception as e:
    print 'Something happened: \n' + str(e) 

time.sleep(3)
