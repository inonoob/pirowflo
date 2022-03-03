import logging
import struct

import gatt
import threading
from time import sleep
import time
from copy import deepcopy

from . import smartrowreader

logger = logging.getLogger(__name__)


class DataLogger():

    ENERGIE_KCAL_MESSAGE = "a"
    WORK_STROKE_LENGTH_MESSAGE = "b"
    POWER_MESSAGE = "c"
    STROKE_RATE_STROKE_COUNT_MESSAGE = "d"
    PACE_MESSAGE = "e"
    FORCE_MESSAGE = "f"
    FIRST_PART_FORCE_CURVE_MESSAGE = "x"
    SECOND_PART_FORCE_CURVE_MESSAGE = "y"
    THIRD_PARD_FORCE_CURVE_MESSAGE = "z"

    SmartRowV3 = False

    def __init__(self, rower_interface):
        self._rower_interface = rower_interface
        self._rower_interface.register_callback(self.on_row_event)

        self.WRValues_rst = None
        self.WRValues = None
        self.WRValues_standstill = None
        self.starttime = None
        self.fullstop = None
        self.SmartRowHalt = None

        self._reset_state()

    def _reset_state(self):
        self.WRValues_rst = {
            'stroke_rate': 0,
            'total_strokes': 0,
            'total_distance_m': 0,
            'instantaneous pace': 0,
            'speed': 0,
            'watts': 0,
            'total_kcal': 0,
            'total_kcal_hour': 0,
            'total_kcal_min': 0,
            'heart_rate': 0,
            'elapsedtime': 0.0,
            'work': 0,
            'stroke_length': 0,
            'force': 0,
            'watts_avg':0,
            'pace_avg':0
        }
        self.WRValues = deepcopy(self.WRValues_rst)
        self.WRValues_standstill = deepcopy(self.WRValues_rst)
        self.starttime = None # time.time() # was None
        self.fullstop = True
        self.SmartRowHalt = False
        self.Initial_reset = False


    def elapsedtime(self):
        print(self.fullstop)
        if self.fullstop == False:
            elaspedtimecalc = int(time.time() - self.starttime)
            self.WRValues.update({'elapsedtime':elaspedtimecalc})
        elif self.fullstop == True and self.WRValues.get('total_distance_m') !=0 and self.Initial_reset == True:
            if not self.starttime:
                   self.starttime = time.time()
            elaspedtimecalc = int(time.time() - self.starttime)
            self.WRValues.update({'elapsedtime':elaspedtimecalc})
        else:
            self.WRValues.update({'elapsedtime': 0})

    # Response for SmartRow V3
    def calculate_challenge_response(self, keylock):
        try:
            key=keylock[1:15]
            checksum=keylock[15:17]
            cksum=f'{(sum(ord(ch) for ch in key)):0>4X}'

            if cksum[-2:] == checksum:
                print("Checksum GOOD")
                a=(int(keylock[11:15],16) * 17923) // 256
                result=f'{a:0>6x}'[2:]
                
                response=[0x0d]
                for c in result:
                    response.append(ord(c))
                response.append(0x0d)
                
                print(response)
                return response
            else:
                print("Checksum BAD")

        except Exception as e:
            print(e)

        # return 0x23 on failure
        return [0x23]

    def send_challenge_response(self, key):
        print("--> Sending challenge response")

        for b in key:
            self._rower_interface.characteristic_write_value(struct.pack("<b",b))
            sleep(0.1)

    # SmartRow V3 obfuscates the first 6 characters
    def parse_v3_decrypt(self, event):
        try:
            s = ''
            for c in event[1:6]:
                s += chr(int(ord(c) & 15 | 0x30))

            r = event[0] + s + event[6:]
            return r

        except Exception as e:
            print(e)
            print(event)
            return event

    def on_row_event(self, event):
        if 'V3.00' in event:
            self.SmartRowV3 = True
            self._rower_interface.characteristic_write_value(struct.pack("<b", 0x23))

        elif 'KEYLOCK' in event:
            try:
                self.SmartRowV3 = True
                key = self.calculate_challenge_response(event)
                self.send_challenge_response(key)
            except Exception as e:
                print("Exception in KEYLOCK event!")
                print(str(e))

        # Un-obfuscate SmartRow V3 distance data
        if self.SmartRowV3 is True:
            event = self.parse_v3_decrypt(event)

        try:
            if event[0] == self.ENERGIE_KCAL_MESSAGE:
                event = event.replace(" ", "0")
                self.WRValues.update({'total_distance_m': int((event[1:6]))})
                self.WRValues.update({'total_kcal': int((event[6:10]))})
                self.elapsedtime()

            elif event[0] == self.WORK_STROKE_LENGTH_MESSAGE:
                event = event.replace(" ", "0")
                #print(event)
                self.WRValues.update({'total_distance_m': int((event[1:6]))})
                self.WRValues.update({'work': float(event[7:11])/10})
                self.WRValues.update({'stroke_length': int((event[11:14]))})
                self.elapsedtime()

            elif event[0] == self.POWER_MESSAGE:
                event = event.replace(" ", "0")
                self.WRValues.update({'total_distance_m': int((event[1:6]))})
                if self.SmartRowHalt == True:
                    self.WRValues.update({'watts': 0})
                else:
                    self.WRValues.update({'watts': int((event[6:9]))})
                self.WRValues.update({'watts_avg': float((event[9:14]))/10})
                self.elapsedtime()

            elif event[0] == self.STROKE_RATE_STROKE_COUNT_MESSAGE:
                event = event.replace(" ", "0")
                self.WRValues.update({'total_distance_m': int((event[1:6]))})
                if self.SmartRowHalt == True:
                    self.WRValues.update({'stroke_rate': 0})
                else:
                    self.WRValues.update({'stroke_rate': float((event[6:8]))*2})
                self.WRValues.update({'total_strokes':int((event[9:13]))})
                self.elapsedtime()

            elif event[0] == self.PACE_MESSAGE:
                event = event.replace(" ", "0")
                self.WRValues.update({'total_distance_m': int((event[1:6]))})
                pace_inst = int(event[6])*60 + int(event[7:9])
                if self.SmartRowHalt == True:
                    self.WRValues.update({'instantaneous pace': 0})
                    self.WRValues.update({'speed': 0})
                else:
                    self.WRValues.update({'instantaneous pace': pace_inst})
                if pace_inst != 0:
                    speed = int(500 * 100 / pace_inst) # speed in cm/s
                    self.WRValues.update({'speed': speed})
                else:
                    self.WRValues.update({'speed': 0})
                pace_avg = int(event[9])*60 + int(event[10:12])
                self.WRValues.update({'pace_avg': pace_avg})
                self.elapsedtime()

            elif event[0] == self.FORCE_MESSAGE:
                event = event.replace(" ", "0")
                self.WRValues.update({'total_distance_m': int((event[1:6]))})
                
                # It doesn't look like V3 has data in this field
                if not self.SmartRowV3:
                    self.WRValues.update({'force': int((event[7:11]))})

                if event[11] == "!":
                    self.SmartRowHalt = True
                    self.fullstop = True
                elif self.starttime == None:
                    self.starttime = time.time()
                    self.SmartRowHalt = False
                    self.fullstop = False
                else:
                    self.SmartRowHalt = False
                    self.fullstop = False
                self.elapsedtime()

            else:
                self._rower_interface.characteristic_write_value(struct.pack("<b", 0x23))

        except Exception as e:
            print(e)
            print(event)

        print(self.WRValues)


def connectSR(manager,smartrow):
    smartrow.connect()
    manager.run()

def reset(smartrow):
    smartrow.characteristic_write_value(struct.pack("<b", 13))
    sleep(0.002)
    smartrow.characteristic_write_value(struct.pack("<b", 86))
    sleep(0.002)
    smartrow.characteristic_write_value(struct.pack("<b", 64))
    sleep(0.002)
    smartrow.characteristic_write_value(struct.pack("<b", 13))

def heartbeat(sr):
    while True:
        sr.characteristic_write_value(struct.pack("<b", 36))
        sleep(1)


def main(in_q, ble_out_q,ant_out_q):
    # this starts discovery, calls manager.run() and returns manager.smartrowmac
    # 
    macaddresssmartrower = smartrowreader.connecttosmartrow()
    manager = gatt.DeviceManager(adapter_name='hci0')
    smartrow = smartrowreader.SmartRow(mac_address=macaddresssmartrower, manager=manager)
    SRtoBLEANT = DataLogger(smartrow)

    BC = threading.Thread(target=connectSR, args=(manager,smartrow))
    BC.daemon = True
    BC.start()

    logger.info("SmartRow Ready and sending data to BLE and ANT Thread")
    while not smartrow.ready() :
      sleep(0.2)

    print("starting heart beat")
    HB = threading.Thread(target=heartbeat, args=([smartrow]))
    HB.daemon = True
    HB.start()
    sleep(3) # this sleep is needed in order give the user time to putt back the handle after pulling it to activate it.
    # The SmartRow device is very sensitive to touches which then triggers 1 m very easy after a reset which then already starts after a restart.
    reset(smartrow)
    sleep(1)
    SRtoBLEANT.Initial_reset = True # this should help to check if the first reset has been performed

    while True:
        if not in_q.empty():
            ResetRequest_ble = in_q.get()
            print(ResetRequest_ble)
            reset(smartrow)
        else:
            pass
        ble_out_q.append(SRtoBLEANT.WRValues)
        ant_out_q.append(SRtoBLEANT.WRValues)
        sleep(0.1)

if __name__ == '__main__':
    main()
