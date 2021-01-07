
from time import sleep

import antdongle as ant
import antfe as fe

from collections import deque

def main(ant_in_q):
    EventCounter = 0
    messages = []       # messages to be sent to
    Antdongle = ant.clsAntDongle()
    Antdongle.Calibrate()
    sleep(0.25)
    Antdongle.Trainer_ChannelConfig()
    sleep(0.25)
    Waterrower = fe.antFE(Antdongle)

    while True:
        if len(ant_in_q) != 0:
            WaterrowerValuesRaw = ant_in_q.pop()
            #print(WaterrowerValuesRaw)
            #WaterrowerValuesRaw = WRValues_test
            if EventCounter < 255:
                Waterrower.EventCounter = EventCounter
                #print(Waterrower.EventCounter)
                Waterrower.BroadcastTrainerDataMessage(WaterrowerValuesRaw)
                messages.append(Waterrower.fedata)# Add data to teh message array
                #print("message to be send is:{0}".format(Waterrower.fedata))
                if len(messages) > 0:
                    Antdongle.Write(messages, True, False) # check if length of array is greater than 0 if yes then send data over Ant+
                EventCounter += 1
                #print(EventCounter)
                messages = []
            else:
                 EventCounter = 0
                 messages = []
        else:
            pass

        # WRValues_test = FakeRower(WRValues_test)
        sleep(0.25)


def FakeRower(WRValues_test):
    WRValues_test_updated = {}
    WRValues_test_updated.update({'stroke_rate': 23})
    WRValues_test_updated.update({'total_strokes': WRValues_test['total_strokes'] + 1})
    WRValues_test_updated.update({'total_distance_m': WRValues_test['total_distance_m'] + 1})
    WRValues_test_updated.update({'speed': 500000 })
    WRValues_test_updated.update({'watts': 150})
    WRValues_test_updated.update({'total_kcal': WRValues_test['total_kcal'] + 1})
    WRValues_test_updated.update({'elapsedtime': WRValues_test['elapsedtime'] +1})
    return WRValues_test_updated

if __name__ == '__main__':

    # WRValues_test = {
    #             'stroke_rate': 23,
    #             'total_strokes': 10,
    #             'total_distance_m': 10,
    #             'instantaneous pace': 0,
    #             'speed': 10,
    #             'watts': 50,
    #             'total_kcal': 0,
    #             'total_kcal_hour': 0,
    #             'total_kcal_min': 0,
    #             'heart_rate': 120,
    #             'elapsedtime': 25,
    #         }
    main()