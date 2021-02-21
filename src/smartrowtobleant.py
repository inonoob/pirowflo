import logging
import struct

import gatt
import threading
from time import sleep
from threading import Timer
import time
from copy import deepcopy

import smartrowreader

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

    def __init__(self, rower_interface):
        self._rower_interface = rower_interface
        self._rower_interface.register_callback(self.on_row_event)

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
        self.starttime = None
        self.fullstop = True
        self.SmartRowHalt = False


    def elapsedtime(self):
        if self.fullstop == False:
            elaspedtimecalc = int(time.time() - self.starttime)
            self.WRValues.update({'elapsedtime':elaspedtimecalc})
        elif self.fullstop == True and self.WRValues.get('total_distance_m') !=0:
            elaspedtimecalc = int(time.time() - self.starttime)
            self.WRValues.update({'elapsedtime':elaspedtimecalc})
        else:
            self.WRValues.update({'elapsedtime': 0})

    def on_row_event(self, event):
        if event[0] == self.ENERGIE_KCAL_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:6]))})
            self.WRValues.update({'total_kcal': int((event[6:10]))})
            self.elapsedtime()

        if event[0] == self.WORK_STROKE_LENGTH_MESSAGE:
            event = event.replace(" ", "0")
            #print(event)
            self.WRValues.update({'total_distance_m': int((event[1:6]))})
            self.WRValues.update({'work': float(event[7:11])/10})
            self.WRValues.update({'stroke_length': int((event[11:14]))})
            self.elapsedtime()

        if event[0] == self.POWER_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:6]))})
            if self.SmartRowHalt == True:
                self.WRValues.update({'watts': 0})
            else:
                self.WRValues.update({'watts': int((event[6:9]))})
            self.WRValues.update({'watts_avg': float((event[9:14]))/10})
            self.elapsedtime()

        if event[0] == self.STROKE_RATE_STROKE_COUNT_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:6]))})
            if self.SmartRowHalt == True:
                self.WRValues.update({'stroke_rate': 0})
            else:
                self.WRValues.update({'stroke_rate': float((event[6:8]))*2})
            self.WRValues.update({'total_strokes':int((event[9:13]))})
            self.elapsedtime()

        if event[0] == self.PACE_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:6]))})
            pace_inst = int(event[6])*60 + int(event[7:9])
            if self.SmartRowHalt == True:
                self.WRValues.update({'instantaneous pace': 0})
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

        if event[0] == self.FORCE_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:6]))})
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

    reset(smartrow)
    sleep(1)

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
