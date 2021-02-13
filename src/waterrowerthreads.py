"""
Python script to broadcast waterrower data over BLE and ANT

      PiRowFlo for Waterrower
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

python3 waterrowerthreads.py -i s4 -b -a
"""

import logging
import logging.config
import threading
import argparse
from queue import Queue
from collections import deque

import waterrowerble
import wrtobleant
import waterrowerant
import smartrowtobleant

logger = logging.getLogger(__name__)

def main(args=None):
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

    def BleService(out_q, ble_in_q):
        logger.info("Start BLE Advertise and BLE GATT Server")
        bleService = waterrowerble.main(out_q, ble_in_q)
        bleService()


    def Waterrower(in_q, ble_out_q, ant_out_q):
        logger.info("Waterrower Interface started")
        Waterrowerserial = wrtobleant.main(in_q, ble_out_q, ant_out_q)
        Waterrowerserial()

    def Smartrow(in_q, ble_out_q, ant_out_q):
        logger.info("Waterrower Interface started")
        Smartrowconnection = smartrowtobleant.main(in_q, ble_out_q, ant_out_q)
        Smartrowconnection()

    def ANTService(ant_in_q):
        logger.info("Start Ant and start broadcast data")
        antService = waterrowerant.main(ant_in_q)
        antService()


    # TODO: Switch from queue to deque
    q = Queue()
    ble_q = deque(maxlen=1)
    ant_q = deque(maxlen=1)
    if args.interface == "s4":
        logger.info("inferface S4 monitor will be used for data input")
        t1 = threading.Thread(target=Waterrower, args=(q, ble_q, ant_q))
        t1.daemon = True
        t1.start()
    else:
        logger.info("S4 not selected")

    if args.interface == "sr":
        logger.info("inferface smartrow will be used for data input")
        t1 = threading.Thread(target=Smartrow, args=(q, ble_q, ant_q))
        t1.daemon = True
        t1.start()
    else:
        logger.info("no interface selected")

    if args.blue == True:
        t2 = threading.Thread(target=BleService, args=(q, ble_q))
        t2.daemon = True
        t2.start()
    else:
        logger.info("Bluetooth service not used")
    if args.antfe == True:
        t3 = threading.Thread(target=ANTService, args=(
        [ant_q]))  # [] are needed to tell threading that the list "deque" is one args and not a list of arguement !
        t3.daemon = True
        t3.start()
    else:
        logger.info("Ant service not used")

    while True:
        pass

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter, )
        parser.add_argument("-i", "--interface", choices=["s4","sr"], default="s4", help="choose  Waterrower interface S4 monitor: s4 or Smartrow: sr")
        parser.add_argument("-b", "--blue", action='store_true', default=False,help="Broadcast Waterrower data over bluetooth low energy")
        parser.add_argument("-a", "--antfe", action='store_true', default=False,help="Broadcast Waterrower data over Ant+")
        args = parser.parse_args()
        logger.info(args)
        main(args)
    except KeyboardInterrupt:
        print("code has been shutdown")

