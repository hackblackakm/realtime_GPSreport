import sys
import time
import argparse
import threading

import serial

from getmac import getmac
from GPS_Threading import gpsRx

port = '/dev/ttyACM1'

class RxThread(threading.Thread):
        
    def __init__(self, sys_state, ser):
        super(RxThread, self).__init__()
        self.sys_state = sys_state
        self.ser = ser
        self.stop = False
    
    def run(self):
        while not self.stop:
            if self.ser.inWaiting():
                temp_str = self.ser.readline().decode('utf8')
                #print(temp_str.encode())
                if temp_str[0] == '1':
                    self.sys_state['received_m'] = temp_str[0]
                    print(self.sys_state['received_m'])
                    self.sys_state['transmit_flag'] = 1

class TxThread(threading.Thread):

    def __init__(self, sys_state, ser):
        super(TxThread, self).__init__()
        self.sys_state = sys_state
        self.ser = ser
        self.stop = False

    def run(self):
        while not self.stop:
            if (not self.ser.inWaiting()) and self.sys_state['transmit_flag']:
                #content = 'hello' + "\n"
                #self.ser.write(self.sys_state['transmit_m'].encode())
                self.sys_state['transmit_flag'] = 0
                #temp_mac = 'mac address : ' + self.sys_state['mac_address'] + '\n'
                temp_mac = self.sys_state['mac_address'] 
                #print(temp_mac)
                #self.ser.write(temp_mac.encode())
                #tem"p_gps = 'gps position : ' + self.sys_state['gps_position'] + '\n'
                temp_gps = self.sys_state['gps_position']
                print(temp_gps)
                temp = temp_mac + '/' + temp_gps
                self.ser.write(temp.encode())
                #self.ser.write('ttyACM0\n'.encode())
                time.sleep(self.sys_state['interval_time'])



def main():
    gps_port = gpsRx()
    gps_port.start()
    gps_port.resume() #gps start
    
    sys_state = {
        'received_m' : ' ',
        'interval_time' : 0.1,
        'transmit_m' : 'hello.',
        'transmit_flag' : 0,
        #'mac_address' : getmac(),
        'mac_address' : '1',
        'gps_position' : gps_port.gps_return()
    }

    ser = serial.Serial(port, 9600, timeout = 0.5)

    rx = RxThread(sys_state, ser)
    tx = TxThread(sys_state, ser)
    rx.start()
    tx.start()

    while True:

        command = 'n'
        if command == 'q':
            rx.stop = True
            tx.stop = True
            gps_port.stop()
            ser.close()
            break
        elif command == 's' :
            tx.sys_state['transmit_flag'] = 1
            command = ''
        else:
            time.sleep(0.1)
            pass
        tx.sys_state['gps_position'] = gps_port.gps_return()

if __name__ == "__main__":
    main()
