import logging
import struct

import gatt
import threading
from time import sleep
from threading import Timer
import time

import smartrowreader


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
filelogHandler = logging.FileHandler("logs.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
filelogHandler.setFormatter(formatter)
logger.addHandler(filelogHandler)
logger.addHandler(logHandler)


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
        self.WRValues = self.WRValues_rst
        self.WRvalue_standstill = self.WRValues_rst
        self.BLEvalues = self.WRValues_rst
        self.ANTvalues = self.WRValues_rst
        self.starttime = 0
        self.fullstop = True

    def elapsedtime(self):
        if self.fullstop == False:
            elaspedtimecalc = int(time.time() - self.starttime)
            self.WRValues.update({'elapsedtime':elaspedtimecalc})
        else:
            self.WRValues.update({'elapsedtime': 0})


    def on_row_event(self, event):
        if event[0] == self.ENERGIE_KCAL_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'total_kcal': int((event[6:10]))})
            self.elapsedtime()

        if event[0] == self.WORK_STROKE_LENGTH_MESSAGE:
            event = event.replace(" ", "0")
            #print(event)
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'work': float(event[7:11])/10})
            self.WRValues.update({'stroke_length': int((event[11:14]))})
            self.elapsedtime()

        if event[0] == self.POWER_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'watts': int((event[6:9]))})
            self.WRValues.update({'watts_avg': float((event[9:14]))/10})
            self.elapsedtime()

        if event[0] == self.STROKE_RATE_STROKE_COUNT_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'stroke_rate': float((event[6:8]))*2})
            self.WRValues.update({'total_strokes':int((event[9:13]))})
            self.elapsedtime()

        if event[0] == self.PACE_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            pace_inst = int(event[6])*60 + int(event[7:9])
            self.WRValues.update({'instantaneous pace': pace_inst})
            pace_avg = int(event[9])*60 + int(event[10:12])
            self.WRValues.update({'pace_avg': pace_avg})
            self.elapsedtime()

        if event[0] == self.FORCE_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'force': int((event[7:11]))})
            if event[12] == "!":
                self.fullstop = True
            else:
                self.fullstop = False
            self.elapsedtime()

        print(self.WRValues)

    # def heartbeat(self):
    #     self.heartbeat = ["24"] # $ ssems to be the heartbeat which is send to the Smartrow every second
    #     self._rower_interface.characteristic_write_value(self.heartbeat)
    #     # TODO: check how to send every second the signal

    #TODO: Elapsed Time must be created
    #TODO: Waterrower is as full stop message f the ! indicates that the system is a stop

def connectSR(manager,smartrow):
    smartrow.connect()
    manager.run()

def reset(smartrow):
    smartrow.characteristic_write_value(struct.pack("<b", 13))
    sleep(0.025)
    smartrow.characteristic_write_value(struct.pack("<b", 86))
    sleep(0.025)
    smartrow.characteristic_write_value(struct.pack("<b", 64))
    sleep(0.025)
    smartrow.characteristic_write_value(struct.pack("<b", 13))

def heartbeat(smartrow):
    smartrow.characteristic_write_value(struct.pack("<b", 36))
    sleep(1)


def main(in_q, ble_out_q,ant_out_q):
    macaddresssmartrower = smartrowreader.connecttosmartrow()

    manager = gatt.DeviceManager(adapter_name='hci1')
    smartrow = smartrowreader.SmartRow(mac_address=macaddresssmartrower, manager=manager)
    SRtoBLEANT = DataLogger(smartrow)

    if smartrow.is_connected == True:
        #try:
        BC = threading.Thread(target=connectSR, args=(manager,smartrow))
        BC.daemon = True
        BC.start()

        HB = threading.Thread(target=heartbeat, args=smartrow)
        HB.daemon = True
        HB.start()

        logger.info("SmartRow Ready and sending data to BLE and ANT Thread")

        while True:
            if not in_q.empty():
                ResetRequest_ble = in_q.get()
                print(ResetRequest_ble)
                reset(smartrow)
            else:
                pass
            ble_out_q.append(SRtoBLEANT.WRValues)
            ant_out_q.append(SRtoBLEANT.WRValues)
            # smartrow.characteristic_write_value(struct.pack("<b", 36)) # heart beat
            # sleep(1)
    else:
        logger.warning("not connect to SmartRow!")


        # except KeyboardInterrupt:
        #     smartrow.disconnect()
        #     manager.stop()



if __name__ == '__main__':
    main()