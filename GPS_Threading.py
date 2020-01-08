import serial
import threading
import pynmea2
import sys
import time
import numpy as np
#GT = np.load('Ground_Truth.npy')
chose = 19
lat_factor = 1.1119
lon_factor = 1.00772
class gpsRx(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.ser = serial.Serial('/dev/ttyS0', 9600, timeout=1) # open your serial port
        self.ser.close() # First, we need to close serial port, in case data flow chaos
        self._running = False # flag: gps threading running 
        self._stop = False # flag: main threading running
        self.gps_pos = 'init/0'
        self.last_gpstime = time.time()
     
    # maintread     
    def run(self):
        while not self._stop:
            # get time for differnet file name
            timerunning = time.time()
            if((timerunning - self.last_gpstime) > 4):
                self.restart()
            timeNow = time.gmtime() 
            timeStamp = time.strftime('%Y%m%d_%H%M%S', timeNow) 
            #FileName = 'GPS_%s.txt' % (timeStamp)
            #sys.stdout.flush()
            #sys.stdout.write('\r' + FileName)
            while (self._running and self.ser.isOpen()):
                try:
                    if (self.ser.inWaiting() > 0):
                        gps_sig = self.ser.readline().decode('utf8')[:-2] # gps serial port read line
                        #print(gps_sig)
                        self.parseGPS(gps_sig) # parsing function
                        #print(gps_sig)
                        #try:
                        #    with open(FileName, 'at') as fout:
                        #        fout.write(gps_sig+'\n')
                        #except FileExistsError:
                        #    with open(FileName, 'xt') as fout:
                        #        fout.write(gps_sig + '\n')                        

                except:
                    break
                    
    # method: gps parsing
    def parseGPS(self,gps_sig):
        if gps_sig.find('GGA') > 0: # GGS is fix GPS, it include longitude, latitude and height 
            msg = pynmea2.parse(gps_sig)
            if (msg != ''): self.last_gpstime = time.time()
            #y = ((msg.latitude - GT[chose][0]-25))*lat_factor*10**5 # lat
            #x = ((msg.longitude - GT[chose][1]-121))*lon_factor*10**5
            #print('\rLat:%f -- Lon:%f -- sats: %s --fix Q %s' % (msg.latitude, msg.longitude, msg.num_sats, msg.gps_qual))
 
            print('\rLat:%f -- Lon:%f -- sats: %s -- Alt: %f --fix Q %s' % (msg.latitude, msg.longitude, msg.num_sats, msg.altitude, msg.gps_qual))
            #self.gps_pos = '%f | %f | %s | %f | %s' % (msg.latitude, msg.longitude, msg.num_sats, msg.altitude, msg.gps_qual)
            self.gps_pos = '%f|%f|%f/%s' % (msg.latitude, msg.longitude, msg.altitude, msg.num_sats)
            #print('\rGT lat:%f -- GT lon:%f -- GT alt:%f --' %(GT[chose][0],GT[chose][1],GT[chose][2]))
            #print('\rHorizon Err:%f -- Alt Err:%f --'%((x**2+y**2)**0.5,abs(msg.altitude - GT[chose][2])))
            #print('--------------------------------------------------')
        # if you need any other information, like velocity, you can read VTG        

    def gps_return(self):
        return self.gps_pos
    # method: resume main thread
    def resume(self):
        self._running = True
        self.ser.open()
    # method: suspend main thread
    def suspend(self):
        self._running = False
        self.ser.close()

    # method: stop main thread    
    def stop(self):
        self._stop = True
        self.ser.close()

    # auto restart for gps not respond for a period
    def restart(self):
        self.suspend()
        time.sleep(0.7)
        self.last_gpstime = time.time()
        self.resume()
