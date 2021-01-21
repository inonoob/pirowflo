import logging
import struct

import gatt
import threading
from time import sleep

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

    def on_row_event(self, event):
        #print("hello world2 {0}".format(event))
        #print(event[0])
        if event[0] == self.ENERGIE_KCAL_MESSAGE:
            #print("kCal are {0}".format(event))
            event = event.replace(" ", "0")
            #print(event)
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'total_kcal': int((event[6:10]))})
        if event[0] == self.WORK_STROKE_LENGTH_MESSAGE:
            #print("Work and Stroke lengh {0}".format(event))
            event = event.replace(" ", "0")
            #print(event)
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'work': float(event[7:11])/10})
            self.WRValues.update({'stroke_length': int((event[11:14]))})


        if event[0] == self.POWER_MESSAGE:
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'watts': int((event[6:9]))})
            self.WRValues.update({'watts_avg': float((event[9:14]))/10})


        if event[0] == self.STROKE_RATE_STROKE_COUNT_MESSAGE:
            #print("Stroke rate and stroke count{0}".format(event))
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'stroke_rate': float((event[6:8]))*2})
            self.WRValues.update({'total_strokes':int((event[9:13]))})
            #print("total strokes{0}".format(self.WRValues.get('total_strokes')))
            #print("stroke rate{0}".format(self.WRValues.get('stroke_rate')))
        if event[0] == self.PACE_MESSAGE:
            #print("Pace is {0}".format(event))
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            pace_inst = int(event[6])*60 + int(event[7:9])
            self.WRValues.update({'instantaneous pace': pace_inst})
            pace_avg = int(event[9])*60 + int(event[10:12])
            self.WRValues.update({'pace_avg': pace_avg})

        if event[0] == self.FORCE_MESSAGE:
            #print("Force{0}".format(event))
            event = event.replace(" ", "0")
            self.WRValues.update({'total_distance_m': int((event[1:5]))})
            self.WRValues.update({'force': int((event[7:11]))})

            
        print(self.WRValues)

    # def reset(self):
    #     self.restemsg = ["0D","56","40","0D"] # enter V @ enter is SmartRow reset command.
    #     for msg in self.restemsg:
    #         self._rower_interface.characteristic_write_value(msg)
    #         sleep(0.05)

    def heartbeat(self):
        self.heartbeat = ["24"] # $ ssems to be the heartbeat which is send to the Smartrow every second
        self._rower_interface.characteristic_write_value(self.heartbeat)
        # TODO: check how to send every second the signal

    #TODO: Elapsed Time must be created
    #TODO: Waterrower is as full stop message f the ! indicates that the system is a stop

def test(manager,smartrow):
    smartrow.connect()
    manager.run()

def reset(smartrow):
    smartrow.characteristic_write_value(struct.pack("<b", 13))
    smartrow.characteristic_write_value(struct.pack("<b", 86))
    smartrow.characteristic_write_value(struct.pack("<b", 54))
    smartrow.characteristic_write_value(struct.pack("<b", 13))

def main(in_q, ble_out_q,ant_out_q):
    macaddresssmartrower = smartrowreader.connecttosmartrow()

    manager = gatt.DeviceManager(adapter_name='hci0')
    smartrow = smartrowreader.SmartRow(mac_address=macaddresssmartrower, manager=manager)
    SRtoBLEANT = DataLogger(smartrow)

    try:
        # smartrow.connect()
        # manager.run()
        BC = threading.Thread(target=test, args=(manager,smartrow))
        BC.daemon = True
        BC.start()
        sleep(10)
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
            #print("hello after the thread")
            #smartrow.characteristic_write_value(struct.pack("<b", 36))

    except KeyboardInterrupt:
        smartrow.disconnect()
        manager.stop()



if __name__ == '__main__':
    main()