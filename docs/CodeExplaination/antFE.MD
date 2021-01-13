Version 13.01.2021

# antFE.py 

## Global overview 

the ant+ Fitness equipement defines how messages should be send and in which order. 
When the class is called it is initialised with the needed data. 

The class has the following methode: 

    def BroadcastTrainerDataMessage(self,WaterrowerValuesRaw):
        self.WaterrowerValueRaw = WaterrowerValuesRaw
        self.ElapsedTime = WaterrowerValuesRaw['elapsedtime'] * 4 # the unit for ant+ is 1 equals to 0.25 sec therfore I need to multipli the elapsedtime by 4.
        self.DistanceTravelled = WaterrowerValuesRaw['total_distance_m']
        self.Speed = (WaterrowerValuesRaw['speed'] * 1000 / 100)#  cm/s to m/s
        self.Heart = 0
        self.StrokeCount = WaterrowerValuesRaw['total_strokes']
        #self.StrokeCount = min(255, self.StrokeCount)
        self.Cadence = WaterrowerValuesRaw['stroke_rate']/2
        self.Cadence = min(253, self.Cadence)  # Limit to 253
        self.InstPower = WaterrowerValuesRaw['watts']
        self.InstPower = max(0, self.InstPower)  # Not negative
        self.InstPower = min(65533, self.InstPower)  # Limit to 4093

it takes as an input the value from the waterrower. This will be populated by the deque
data handler send over by the wrtobleant.py  

if then checks what is the value of the EventCounter. Which must be set before calling
the BroadcastTrainerDataMessage methode. This value defines what message the methode
will responce. This is due to the face that the ant+ defines the following message 
sequence: (see for more details Ant+ Fitness equipment device profile page 27 8.3)


|               30 pages                  |      2 page        |          30 pages       |  2 pages

page16   page16   page22   page22 ...... page80   page80   page16   page16   page22   page22 ...... page81   page81

Therefore we check when it time to send the page 80 by dividing the eventCounter which is between 0 and 
255 by &64 

    if self.EventCounter % 64 in (30, 31):  # After 10 blocks of three messages, then 2 = 32 messages
        self.info = self._ant_dongle.msgPage80_ManufacturerInfo(self._ant_dongle.channel_FE, 0xff, 0xff, self._ant_dongle.HWrevision_FE, self._ant_dongle.Manufacturer_waterrower, self._ant_dongle.ModelNumber_FE)
        self.fedata = self._ant_dongle.ComposeMessage(self._ant_dongle.msgID_BroadcastData, self.info)