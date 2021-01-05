"""
Python script to broadcast waterrower data over BLE and ANT
"""

import logging
import threading
import argparse
from queue import Queue
from collections import deque

import WaterrowerBle
import WRtoBLEANT
import WaterrowerAnt


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
filelogHandler = logging.FileHandler("logs.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
filelogHandler.setFormatter(formatter)
logger.addHandler(filelogHandler)
logger.addHandler(logHandler)


def main(args=None):

    def BleService(out_q, ble_in_q):
        logger.info("Start BLE Advertise and BLE GATT Server")
        bleService = WaterrowerBle.main(out_q, ble_in_q)
        bleService()

    def Waterrower(in_q, ble_out_q, ant_out_q):
        logger.info("Waterrower to BLE and ANT")
        Waterrowerserial = WRtoBLEANT.main(in_q, ble_out_q, ant_out_q)
        Waterrowerserial()

    def ANTService(ant_in_q):
        logger.info("Start Ant and start broadcast data")
        antService = WaterrowerAnt.main(ant_in_q)
        antService()


    # TODO: Switch from queue to deque
    q = Queue()
    ble_q = deque(maxlen=1)
    ant_q = deque(maxlen=1)
    t1 = threading.Thread(target=BleService, args=(q, ble_q))
    t1.daemon = True
    t2 = threading.Thread(target=Waterrower, args=(q, ble_q, ant_q))
    t2.daemon = True
    t3 = threading.Thread(target=ANTService, args=([ant_q])) # [] are needed to tell threading that the list "deque" is one args and not a list of arguement !
    t3.daemon = True
    t1.start()
    if args.blue == True:
        t2.start()
    if args.antfe == True:
        t3.start()

    while True:
        pass

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter, )
        parser.add_argument("-b", "--blue", action='store_true', default=False,help="Broadcast Waterrower data over bluetooth low energy")
        parser.add_argument("-a", "--antfe", action='store_true', default=False,help="Broadcast Waterrower data over Ant+")
        args = parser.parse_args()
        main(args)
    except KeyboardInterrupt:
        print("code has been shutdown")

# https://github.com/anjiuidev/argparser-python/blob/master/sample.py
# https://github.com/thorsummoner/python-argp
#https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
