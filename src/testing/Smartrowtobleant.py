import logging
import gatt

import smartrowreader
import time



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
        self._rower_interface.register_callback(self.helloworld2)

    def helloworld2(self, event):
        #print("hello world2 {0}".format(event))
        #print(event[0])
        if event[0] == self.ENERGIE_KCAL_MESSAGE:
            print("kCal are {0}".format(event))




def main():
    manager = gatt.DeviceManager(adapter_name='hci0')
    smartrow = smartrowreader.SmartRow(mac_address="00:1A:7D:DA:71:04", manager=manager)
    SRtoBLEANT = DataLogger(smartrow)
    smartrow.connect()
    manager.run()


if __name__ == '__main__':
    main()