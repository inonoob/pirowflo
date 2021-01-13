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

every 30th and 31st messages the Manufacturer info 0x50 is send. This also applies for the product information 0x51 each 62th and 63th message 

    elif self.EventCounter % 64 in (62, 63):  # After 10 blocks of three messages, then 2 = 32 messages
        self.info = self._ant_dongle.msgPage81_ProductInformation(self._ant_dongle.channel_FE, 0xff, self._ant_dongle.SWrevisionSupp_FE, self._ant_dongle.SWrevisionMain_FE, self._ant_dongle.SerialNumber_FE)
        self.fedata = self._ant_dongle.ComposeMessage(self._ant_dongle.msgID_BroadcastData, self.info)

every 3rd and 4th event the Rowing message 0x16 is sand. All the given input data 
are according the ANT+ spec for rowing data. (Ant+ documenation Fitness equipement profile)

    elif self.EventCounter % 3 == 0 or self.EventCounter % 4 == 0:


if non of the if and elif are hit by the event division check, the General Fitness page is 
send 0x10. 


All message are build by first invoking the specific page methode from the instance 
antDongle. This encode the value in the proper byte length. e.g. 

    self.info = self._ant_dongle.msgPage16_GeneralFEdata(self._ant_dongle.channel_FE, self.AccumlatedElapsedTime, self.AccumlatedDistanceTravelled, self.Speed, self.Heart)

Then the message compose methode is called which put togther the data to signal a data broadbast will be done 
and add the byte transformed data at the end. 

This is an example of how a finished message looks like : 

broadcast data +    rowing data              | Checksum 
a4 09 4e 00    |     10 00 ff 5a 00 00 1b 01 | 4c

This is the result of the composeMessage methode. The message hasn't be send yet. 

Some of the rowing values a subjected to rollover. That means once the rollover
value is hit, it must be set to 0. The device getting those data must keep
track of this rollover. E.g StrokeCount rolls over after 254 strokes. 

in order to have a simpler code with all those rollover value the following methode
has been defined: 

    def Rollovercalc(self,rollovervar, limit):
        if rollovervar <= limit:
            Accumulatedvar = rollovervar
        else:
            rollovercount = int(rollovervar/ limit)
            Accumulatedvar = rollovervar - (rollovercount * limit)
        return Accumulatedvar

As the Waterrower data coming from the wrtobleant.py don't have a rollover 
the data must be transformed to meet this requirement. It is done by dividing
the number by the limit in order to check how many rollovers must be 
substracted from the input value in order to tranform it to be between 0 and 
the given limit. 

e.g if 300 strokes are received, 

    def Rollovercalc(300, 256):
        if rollovervar <= limit:  300 > 256 
            Accumulatedvar = rollovervar
        else:
            rollovercount = int(300/ 256)  # 1
            Accumulatedvar = 300 - (1 * 256) = 44 # < 256
        return Accumulatedvar

e.g if 1000 strokes are received, 

    def Rollovercalc(1000, 256):
        if rollovervar <= limit:  1000 > 256 
            Accumulatedvar = rollovervar
        else:
            rollovercount = int(1000/ 256)  # 3
            Accumulatedvar = 1000- (3 * 256) = 232 # < 256
        return Accumulatedvar

