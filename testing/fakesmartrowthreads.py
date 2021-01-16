"""
Python script to broadcast FakeSmartRow data over BLE and ANT

      FakeSmartRow Ant and BLE Raspberry Pi Module
                                                                 +-+
                                               XX+-----------------+
                  +-------+                 XXXX    |----|       | |
                   +-----+                XXX +----------------+ | |
                   |     |             XXX    |XXXXXXXXXXXXXXXX| | |
    +--------------X-----X----------+XXX+------------------------+-+
    |                                                              |
    +--------------------------------------------------------------+

To begin choose an interface from where the data will be taken from either the S4 Monitor connected via USB or
the Smartrow pulley via bluetooth low energy

Then select which broadcast methode will be used. Bluetooth low energy or Ant+ or both.

e.g. use the S4 connected via USB and broadcast data over bluetooth and Ant+

python3 fakesmartrowthreads.py -i s4 -b -a
"""

import logging
import threading
import argparse
from queue import Queue
from collections import deque

import fakesmartrowble
import fakerower



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

    def FakeSmartRowBLE(out_q, ble_in_q):
        logger.info("Start BLE Advertise and BLE GATT Server")
        FakeSmartRowBLE = fakesmartrowble.main(out_q, ble_in_q)
        FakeSmartRowBLE()

    def FakeSmartRow(in_q, ble_out_q):
        logger.info("FakeSmartRow Interface started")
        FakeSmartRowserial = fakerower.main(in_q, ble_out_q)
        FakeSmartRowserial()


    # TODO: Switch from queue to deque
    q = Queue()
    ble_q = deque(maxlen=1)
    if args.interface == "s4":
        logger.info("inferface S4 monitor will be used for data input")
        t1 = threading.Thread(target=FakeSmartRow, args=(q, ble_q))
        t1.daemon = True
        t1.start()
    else:
        logger.info("no interface selected")

    if args.blue == True:
        t2 = threading.Thread(target=FakeSmartRowBLE, args=(q, ble_q))
        t2.daemon = True
        t2.start()
    else:
        logger.info("Bluetooth service not used")
    while True:
        pass

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter, )
        parser.add_argument("-i", "--interface", choices=["s4","sr"], default="s4", help="choose  FakeSmartRow interface S4 monitor: s4 or Smartrow: sr")
        parser.add_argument("-b", "--blue", action='store_true', default=False,help="Broadcast FakeSmartRow data over bluetooth low energy")
        args = parser.parse_args()
        logger.info(args)
        main(args)
    except KeyboardInterrupt:
        print("code has been shutdown")

