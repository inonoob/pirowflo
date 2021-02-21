# ---------------------------------------------------------------------------
# Original code from the bfritscher Repo waterrower
# https://github.com/bfritscher/waterrower
# ---------------------------------------------------------------------------

import threading
import time
import datetime
import logging
import numpy
from copy import deepcopy

import waterrowerinterface

logger = logging.getLogger(__name__)
'''
We register 3 callback function to the WaterrowerInterface with the event as input. Those function get exectuted 
as soon as an event is register from "capturing". 
We create 3 differnt dict with 3 different value sets. 
- first case: rowing has been reseted so only 0 value should be send even if in the WR memory old values persists 
- second case: we do HIIT training and the rower is at standstill. The value are not set to 0 in the WR memory. therfore set all instantaneous value to 0 e.g power, pace, stroke rate 
- last case: Normal rowing get data from WR memory without touching it 

Depeding on thoses cases send to the bluetooth module only the value dict with the correct numbers. 
'''

IGNORE_LIST = ['graph', 'tank_volume', 'display_sec_dec']


class DataLogger(object):
    def __init__(self, rower_interface):
        self._rower_interface = rower_interface
        self._rower_interface.register_callback(self.reset_requested)
        self._rower_interface.register_callback(self.pulse)
        self._rower_interface.register_callback(self.on_rower_event)
        self._stop_event = threading.Event()

        self._reset_state()

    def _reset_state(self):
        self._InstaPowerStroke = []
        self.maxpowerStroke = 0
        self._StrokeStart = False
        self.Watts = 0
        self._maxpowerfivestrokes = []
        self.AvgInstaPower = 0
        self.Lastcheckforpulse = 0
        self.PulseEventTime = 0
        self.InstantaneousPace = 0
        self.DeltaPulse = 0
        self.PaddleTurning = False
        self.rowerreset = True
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
            }
        self.WRValues = deepcopy(self.WRValues_rst)
        self.WRValues_standstill = deepcopy(self.WRValues_rst)
        self.BLEvalues = deepcopy(self.WRValues_rst)
        self.ANTvalues = deepcopy(self.WRValues_rst)
        self.secondsWR = 0
        self.minutesWR = 0
        self.hoursWR = 0
        self.elapsetime = 0
        self.elapsetimeprevious = 0

    def on_rower_event(self, event):
        if event['type'] in IGNORE_LIST:
            return
        if event['type'] == 'stroke_start':
            self._StrokeStart = True
        if event['type'] == 'stroke_end':
            self._StrokeStart = False
        if event['type'] == 'stroke_rate':
            self.WRValues.update({'stroke_rate': (event['value']*2)})
        if event['type'] == 'total_strokes':
            self.WRValues.update({'total_strokes': event['value']})
        if event['type'] == 'total_distance_m':
            self.WRValues.update({'total_distance_m': (event['value'])})
        if event['type'] == 'avg_distance_cmps':
            if event['value'] == 0:
                self.WRValues.update({'instantaneous pace': 0})
                self.WRValues.update({'speed':0})
            else:
                self.InstantaneousPace = (500 * 100) / event['value']
                #print(self.InstantaneousPace)
                self.WRValues.update({'instantaneous pace': self.InstantaneousPace})
                self.WRValues.update({'speed':event['value']})
        if event['type'] == 'watts':
            self.Watts = event['value']
            self.avgInstaPowercalc(self.Watts)
        if event['type'] == 'total_kcal':
            self.WRValues.update({'total_kcal': (event['value']/1000)})  # in cal now in kcal
        if event['type'] == 'total_kcal_h':  # must calclatre it first
            self.WRValues.update({'total_kcal': 0})
        if event['type'] == 'total_kcal_min':  # must calclatre it first
            self.WRValues.update({'total_kcal': 0})
        if event['type'] == 'heart_rate':
            self.WRValues.update({'heart_rate': (event['value'])})  # in cal
        if event['type'] == 'display_sec':
            self.secondsWR = event['value']
        if event['type'] == 'display_min':
            self.minutesWR = event['value']
        if event['type'] == 'display_hr':
            self.hoursWR = event['value']
        self.TimeElapsedcreator()


    def pulse(self,event):
        self.Lastcheckforpulse = int(round(time.time() * 1000))
        if event['type'] == 'pulse':
            self.PulseEventTime = event['at']
            self.rowerreset = False
        self.DeltaPulse = self.Lastcheckforpulse - self.PulseEventTime
        if self.DeltaPulse <= 300:
            self.PaddleTurning = True
        else:
            self.PaddleTurning = False
            self._StrokeStart = False
            self.PulseEventTime = 0
            self.WRValuesStandstill()


    def reset_requested(self,event):
        if event['type'] == 'reset':
            self._reset_state()
            logger.info("value reseted")

    def TimeElapsedcreator(self):
        self.elapsetime = datetime.timedelta(seconds=self.secondsWR, minutes=self.minutesWR, hours=self.hoursWR)
        self.elapsetime = int(self.elapsetime.total_seconds())
        if  self.elapsetime >= self.elapsetimeprevious:
        # print('sec:{0};min:{1};hr:{2}'.format(self.secondsWR,self.minutesWR,self.hoursWR))
            self.WRValues.update({'elapsedtime': self.elapsetime})
            self.elapsetimeprevious = self.elapsetime

    def WRValuesStandstill(self):
        self.WRValues_standstill = deepcopy(self.WRValues)
        self.WRValues_standstill.update({'stroke_rate': 0})
        self.WRValues_standstill.update({'instantaneous pace': 0})
        self.WRValues_standstill.update({'speed': 0})
        self.WRValues_standstill.update({'watts': 0})

    def avgInstaPowercalc(self,watts):
        if watts != 0:
            if self._StrokeStart == True:
                self._InstaPowerStroke.append(watts)
            elif self._StrokeStart == False:
                if len(self._InstaPowerStroke) != 0:
                    self.maxpowerStroke = numpy.max(self._InstaPowerStroke)
                    if len(self._maxpowerfivestrokes) > 4:
                        del self._maxpowerfivestrokes[0]
                    self._maxpowerfivestrokes.append(self.maxpowerStroke)
                    self.AvgInstaPower = int(numpy.average(self._maxpowerfivestrokes))
                    self.WRValues.update({'watts': self.AvgInstaPower})
                    self._InstaPowerStroke = []
                else:
                    pass


    def get_WRValues(self):
        if self.rowerreset:
            return deepcopy(self.WRValues_rst)
        elif not self.rowerreset and not self.PaddleTurning:
            return deepcopy(self.WRValues_standstill)
        elif not self.rowerreset and self.PaddleTurning:
            return deepcopy(self.WRValues)

    def SendToBLE(self):
        self.BLEvalues = self.get_WRValues()

    def SendToANT(self):
        self.ANTvalues = self.get_WRValues()

def main(in_q, ble_out_q,ant_out_q):
    S4 = waterrowerinterface.Rower()
    S4.open()
    S4.reset_request()
    WRtoBLEANT = DataLogger(S4)
    logger.info("Waterrower Ready and sending data to BLE and ANT Thread")
    while True:
        if not in_q.empty():
            ResetRequest_ble = in_q.get()
            print(ResetRequest_ble)
            S4.reset_request()
        else:
            pass
        WRtoBLEANT.SendToBLE()
        WRtoBLEANT.SendToANT()
        ble_out_q.append(WRtoBLEANT.BLEvalues)
        ant_out_q.append(WRtoBLEANT.ANTvalues) # here it is a class deque
        #print(type(ant_out_q))
        #print(ant_out_q)
        #logger.info(WRtoBLEANT.BLEvalues)
        #ant_out_q.append(WRtoBLEANT.ANTvalues)
        time.sleep(0.1)


# def maintest():
#     S4 = WaterrowerInterface.Rower()
#     S4.open()
#     S4.reset_request()
#     WRtoBLEANT = DataLogger(S4)
#
#     def MainthreadWaterrower():
#         while True:
#         #print(WRtoBLEANT.BLEvalues)
#             #ant_out_q.append(WRtoBLEANT.ANTvalues)
#             #print("Rowering_value  {0}".format(WRtoBLEANT.WRValues))
#             #print("Rowering_value_rst  {0}".format(WRtoBLEANT.WRValues_rst))
#             #print("Rowering_value_standstill  {0}".format(WRtoBLEANT.WRValues_standstill))
#             print("Reset  {0}".format(WRtoBLEANT.rowerreset))
#             #print("Paddleturning  {0}".format(WRtoBLEANT.PaddleTurning))
#             #print("Lastcheck {0}".format(WRtoBLEANT.Lastcheckforpulse))
#             #print("last pulse {0}".format(WRtoBLEANT.PulseEventTime))
#             #print("is connected {}".format(S4.is_connected()))
#             time.sleep(0.1)
#
#
#     t1 = threading.Thread(target=MainthreadWaterrower)
#     t1.start()
#
#
# if __name__ == '__main__':
#     maintest()
