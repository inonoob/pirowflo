import logging
import struct

import gatt
import threading
from time import sleep
import time
from copy import deepcopy

from . import ftmsrowerreader

logger = logging.getLogger(__name__)


class DataLogger():
    # INDEXES are [index, length]
    # referencing later by [index:index + length] notation
    # All little endian?
    #        +- Strokes per 2 seconds
    #        |  +--+- Total Strokes
    #        |  |  |  +--+--+- Total Distance
    #        |  |  |  |  |  |  +--+- Instantaneous Pace
    #        |  |  |  |  |  |  |  |  +--+- Instantaneous Power (watts)
    #        |  |  |  |  |  |  |  |  |  |  +--+- Total Energy
    #        |  |  |  |  |  |  |  |  |  |  |  |  +--+- Energy_per_hour
    #        |  |  |  |  |  |  |  |  |  |  |  |  |  |  +- Energy Per Minute
    #        |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  +--+- Elapsed time
    #        |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
    #  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 Index
    # 2c-09-32-03-00-2b-00-00-95-00-83-00-09-00-f1-02-00-12-00
    INDEXES = {
    "stroke_rate": [2, 1], # /2 for StrokesPerSecond
    "total_strokes": [3, 2], # Total, 02 00 = 00 02 = 2
    "total_distance_m": [5, 3], # Total, Meters 1a 00 00 = 00 00 1a = 26
    "instantaneous pace": [8, 2], # Gauge, c4 00 = 00 c4 = 196 seconds per 500 meters
    "watts": [10, 2], # Gauge, 50 00 = 00 50 = 80 watts (instantaneous_power)
    "total_kcal": [12, 2], # Total, kCal 07 00 = 00 07 = 7 kCal
    "total_kcal_hour": [14, 2], # Gauge? Total? Total if we continue for 1 hr? 
    "total_kcal_minute": [16, 1], # Gauge/Avg, once at least a minute is done
    #"elapsed_time": [17, 3], # Total reported, but apparently we calculate it?
    }
    FTMS_EVENT = 44
    
    def __init__(self, rower_interface):
        self._rower_interface = rower_interface
        self._rower_interface.register_callback(self.on_row_event)
        
        self.WRValues_rst = None
        self.WRValues = None
        self.WRValues_standstill = None
        self.starttime = None
        self.fullstop = None
        self.ftmsHalt = None
        
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
        self.ftmsHalt = False
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

    def on_row_event(self, event):
        if int(event[0]) == self.FTMS_EVENT:
            oldWRValues = deepcopy(self.WRValues)
            for message_type, indexes in self.INDEXES.items():
                i, l = indexes
                # Get the data at the index(es), reverse the byte order
                # Convert the bytestring to a hex string, then to a decimal integer
                integer_value = int(event[i:i+l][::-1].hex(),16)
                #if message_type = "stroke_rate":
                #    integer_value = int(integer_value / 2) # Handled in antfe.py
                self.WRValues.update({message_type: integer_value})
                if message_type == "instantaneous pace" and integer_value > 0:
                    # pace is seconds per 500m
                    # We want cm/s? I guess? So 500 (meters) * 100 gives us CM
                    # Then divide by pace for cm/s
                    speed = 500 * 100 / integer_value
                    self.WRValues.update({'speed': speed})
            new_strokes = self.WRValues['total_strokes'] - oldWRValues['total_strokes']
            new_distance = self.WRValues['total_distance_m'] - oldWRValues['total_distance_m']
            if new_strokes > 0:
                self.WRValues.update({'stroke_length':  new_distance / new_strokes})
            self.elapsedtime()

            print(self.WRValues)
            #print("| H|R| TS|   TD| IP| Wa| TE| TH|M|time")
            #print(event.hex())


def connectFTMS(manager,ftms):
    ftms.connect()
    manager.run()

def reset(ftms):
    pass
    ftms.characteristic_write_value(struct.pack("<b", 13))
    sleep(0.002)
    ftms.characteristic_write_value(struct.pack("<b", 86))
    sleep(0.002)
    ftms.characteristic_write_value(struct.pack("<b", 64))
    sleep(0.002)
    ftms.characteristic_write_value(struct.pack("<b", 13))

def heartbeat(sr):
    pass
    while True:
        sr.characteristic_write_value(struct.pack("<b", 36))
        sleep(1)


def main(in_q, ble_out_q,ant_out_q):
    # this starts discovery, calls manager.run() and returns manager.ftmsmac
    # 
    macaddressftms = ftmsrowerreader.connecttoftmsrow()
    manager = gatt.DeviceManager(adapter_name='hci0')
    ftms = ftmsrowerreader.FTMS_Rower(mac_address=macaddressftms, manager=manager)
    FTMStoBLEANT = DataLogger(ftms)
    
    BC = threading.Thread(target=connectFTMS, args=(manager,ftms))
    BC.daemon = True
    BC.start()

    logger.info("FTMSRower Ready and sending data to BLE and ANT Thread")
    while not ftms.ready() :
        sleep(0.2)

    print("starting heart beat")
    HB = threading.Thread(target=heartbeat, args=([ftms]))
    HB.daemon = True
    HB.start()
    sleep(3) # this sleep is needed in order give the user time to putt back the handle after pulling it to activate it.
    # The ftms device is very sensitive to touches which then triggers 1 m very easy after a reset which then already starts after a restart.
    reset(ftms)
    sleep(1)
    FTMStoBLEANT.Initial_reset = True # this should help to check if the first reset has been performed

    while True:
        if not in_q.empty():
            ResetRequest_ble = in_q.get()
            print(ResetRequest_ble)
            reset(ftms)
        else:
            pass
        ble_out_q.append(FTMStoBLEANT.WRValues)
        ant_out_q.append(FTMStoBLEANT.WRValues)
        sleep(0.1)

if __name__ == '__main__':
    main()
