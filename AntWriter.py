

import antDongle as ant
import antFE as fe
import time
from time import sleep

def main(ant_q):
    EventCounter = 0
    messages = []       # messages to be sent to
    Antdongle = ant.clsAntDongle()
    Antdongle.Calibrate()
    sleep(0.5)
    Antdongle.Trainer_ChannelConfig()
    sleep(0.5)
    Waterrower = fe.antFE(Antdongle)


    while True:

        # #WaterrowerValuesRaw = ant_q.pop()
        # WaterrowerValuesRaw = ant_q
        # if EventCounter < 255:
        #     Waterrower.EventCounter = EventCounter
        #     print(Waterrower.EventCounter)
        #     messages.append(Waterrower.BroadcastTrainerDataMessage(WaterrowerValuesRaw))# Add data to teh message array
        #     print(Waterrower.fedata)
        #     print(messages)
        #     if len(messages) > 0:
        #         Antdongle.Write(messages, True, False) # check if length of array is greater than 0 if yes then send data over Ant+
        #     EventCounter += 1
        #     print(EventCounter)
        #     messages = []
        # else:
        #      EventCounter = 0
        #      messages = []
        # sleep(0.25)
        info = Antdongle.msgPage80_ManufacturerInfo(Antdongle.channel_FE, 0xff, 0xff,
                                                                Antdongle.HWrevision_FE,
                                                                Antdongle.Manufacturer_waterrower,
                                                                Antdongle.ModelNumber_FE)
        fedata = Antdongle.ComposeMessage(Antdongle.msgID_BroadcastData, info)
        messages.append(fedata)
        Antdongle.Write(messages)
        messages = []
        sleep(0.25)

        info = Antdongle.msgPage81_ProductInformation(Antdongle.channel_FE, 0xff,
                                                                  Antdongle.SWrevisionSupp_FE,
                                                                  Antdongle.SWrevisionMain_FE,
                                                                  Antdongle.SerialNumber_FE)
        fedata = Antdongle.ComposeMessage(Antdongle.msgID_BroadcastData, info)
        messages.append(fedata)
        Antdongle.Write(messages)
        messages = []
        sleep(0.25)


if __name__ == '__main__':
    WRValues_test = {
                'stroke_rate': 23,
                'total_strokes': 10,
                'total_distance_m': 10,
                'instantaneous pace': 0,
                'speed': 10,
                'watts': 0,
                'total_kcal': 0,
                'total_kcal_hour': 0,
                'total_kcal_min': 0,
                'heart_rate': 120,
                'elapsedtime': 25,
            }
    main(WRValues_test)