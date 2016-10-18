#!/usr/bin/env python

# OUTLINE
# Turn off essential services -- make sure sigma-controller.py is shut down (script restarts ppp)
# Shut down pppd
# Verify GSM settings are correct -- log
# Collect GSM information -- log
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

# Activate GPIO22
def activateGPIO22(cmd):
    open('/sys/class/gpio/gpio22/value', 'wb').write('1')
    time.sleep(45)
    gpio = subprocess.check_output(cmd, shell=True)
    return gpio

# Create GSM log file
print 'Collecting GSM info....'

capeGSMLogFile = os.path.join(save_path, name_of_file+'_test_results.txt')         
with open(capeGSMLogFile, 'a') as results:
    sys.stdout = results

    print '********************** BEGIN GSM SETTINGS VERIFICATION FOR ' + name_of_file + ' --- PASS 1 --- ********************** \n'
    print '********************** ' + datetime.datetime.now().isoformat() + ' *************************** \n'

    # Check GPIO22 is active
    print 'Verifying gpio22 set...'
    cmd = 'cat /sys/class/gpio/gpio22/value'

    try:        
        gpio22 = subprocess.check_output(cmd, shell=True)
        j = 0;
        if '1' not in gpio22:
            while '1' not in gpio22 and j < 5:
                gpio = activateGPIO22(cmd)
                gpio22 = gpio
                j += 1
            if '1' not in gpio:
                print 'Could not continue script; something is wrong with GPIO22.'
                quit()         
            else:
                print "GPIO22 was turned off; turned on GPIO22."
        else:
            print 'GPIO22 - OK'
    except Exception as e:
        print 'Could not continue script; something is wrong with GPIO22.'
        print e
        quit()

    # Check baud rate
    print "Verifying 'at+ipr' set..."
    if '921600' not in send('at+ipr?')[1]:
        try:
            send('at+ipr=921600')
            print "IPR was not set correctly; it's fixed now. Current value = 921600 \n"
        except Exception as e:
            print 'Attempted to set IPR - something happened: \n' + str(e)
    elif '921600' in send('at+ipr?')[1]:
        print 'IPR - OK'
    else:
        # FAIL LOUDLY
        print send('at+ipr?')[1]
        print 'Something is VERY WRONG - make sure upgrade-serial.py completed successfully.'
        quit()

    # Check CTS/RTS handshaking (prevents lost characters)
    print "Verifying 'at&k3' set..."
    if '&K3' not in send('at&v?')[2]:
        try:
            send('at&k3')
            print "CTS/RTS handshaking was not set correctly; it's fixed now. \nCurrent value = &K3 \n"
        except Exception as e:
            print "Attempted to set CTS/RTS handshaking ('at&k3') - something happened: \n" + str(e)
            print e
    else:
        print 'CTS/RTS handshaking - OK'

    # Check Stored Profile 1
    #    Compare Active Profile to Stored Profile 1 values
    print "Verifying 'at&y1', 'at&w1' set..."
    if send('at&v')[3] != send('at&v')[11]:
        try:
            send('at&w1')
            print 'Stored Profile 1 settings were incorrect. Current settings saved to Stored Profile 1.'
        except Exception as e:
            print 'Attempted to set Stored Profile 1 - something happened: \n' + str(e)
    else:
        print 'Stored Profile 1 - OK'

    if send('at&v')[3] == send('at&v')[11]:
        with open('tmp_gsm.txt', 'w') as f:
            gsm_pass1 = 'Profile Saved'
            f.write('{0}\n'.format(gsm_pass1))
            f.close()
    else:
        print "GSM profile settings were not saved; it's probably a good idea to investigate."

    print '*************************** END GSM SETTINGS VERIFICATION --- PASS 1 --- *************************** \n'

    # Collect GSM information

    # For reference:
    #     at+cgsn = IMEI of GSM module
    #     ati = Model of GSM module
    #     at+cnum  = Phone number of current SIM card
    #     at+csq = Cell signal quality of GSM module
    #     at+ccid = CCID of GSM module
    #     at+ipr = Baudrate of DCE

    print '********************** BEGIN GSM DATA COLLECT FOR ' + name_of_file + ' --- PASS 1 --- **********************'
    print 'IMEI: ' + send('at+cgsn')[1]
    print 'Model: ' + send('ati')[1]
    print 'Phone number: ' + send('at+cnum')[1]
    print send('at+csq')[1]
    print send('at+ccid?')[1]
    print 'Current configuration settings: ' 
    print send('at&v')
    print '*************************** END GSM DATA COLLECT --- PASS 1 --- *************************** \n'

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

