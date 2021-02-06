# ---------------------------------------------------------------------------
# Original code from the FortiusANT Repo
# https://github.com/WouterJD/FortiusANT
# ---------------------------------------------------------------------------
#


class antFE(object):
    def __init__(self, ant_dongle):
        self._ant_dongle = ant_dongle
        self.EventCounter = 0
        self.DistanceTravelled = 0
        self.info = []
        self.fedata = []
        self.WaterrowerValueRaw ={}
        self.InstPower = 0
        self.Cadence = 0
        self.AccumlatedStrokecount = 0
        self.Rollovercount = 0
        self.AccumlatedElapsedTime = 0
        self.AccumlatedDistanceTravelled = 0

    def BroadcastTrainerDataMessage(self,WaterrowerValuesRaw):
        self.WaterrowerValueRaw = WaterrowerValuesRaw
        self.ElapsedTime = WaterrowerValuesRaw['elapsedtime'] * 4 # the unit for ant+ is 1 equals to 0.25 sec therfore I need to multipli the elapsedtime by 4.
        self.DistanceTravelled = WaterrowerValuesRaw['total_distance_m']
        self.Speed = (WaterrowerValuesRaw['speed'] * 1000 / 100) #  cm/s to m/s (/100) and multiply by 1000 cause ant+ 0.001 m/s
        self.Heart = 0
        self.StrokeCount = WaterrowerValuesRaw['total_strokes']
        self.Cadence = WaterrowerValuesRaw['stroke_rate']/2
        self.Cadence = min(253, self.Cadence)  # Limit to 253
        self.InstPower = WaterrowerValuesRaw['watts']
        self.InstPower = max(0, self.InstPower)  # Not negative
        self.InstPower = min(65533, self.InstPower)  # Limit to 4093



        if self.EventCounter % 64 in (30, 31):  # After 10 blocks of three messages, then 2 = 32 messages
            self.info = self._ant_dongle.msgPage80_ManufacturerInfo(self._ant_dongle.channel_FE, 0xff, 0xff, self._ant_dongle.HWrevision_FE, self._ant_dongle.Manufacturer_waterrower, self._ant_dongle.ModelNumber_FE)
            self.fedata = self._ant_dongle.ComposeMessage(self._ant_dongle.msgID_BroadcastData, self.info)

        elif self.EventCounter % 64 in (62, 63):  # After 10 blocks of three messages, then 2 = 32 messages
            self.info = self._ant_dongle.msgPage81_ProductInformation(self._ant_dongle.channel_FE, 0xff, self._ant_dongle.SWrevisionSupp_FE, self._ant_dongle.SWrevisionMain_FE, self._ant_dongle.SerialNumber_FE)
            self.fedata = self._ant_dongle.ComposeMessage(self._ant_dongle.msgID_BroadcastData, self.info)

        elif self.EventCounter % 3 == 0 or self.EventCounter % 4 == 0:

            self.AccumlatedStrokecount = self.Rollovercalc(self.StrokeCount,254)
            self.info = self._ant_dongle.msgPage22_RowingData(self._ant_dongle.channel_FE, self.AccumlatedStrokecount, self.Cadence, self.InstPower)
            self.fedata = self._ant_dongle.ComposeMessage(self._ant_dongle.msgID_BroadcastData, self.info)

        else:
            self.AccumlatedElapsedTime = self.Rollovercalc(self.ElapsedTime,256)
            self.AccumlatedDistanceTravelled = self.Rollovercalc(self.DistanceTravelled,256)
            self.info = self._ant_dongle.msgPage16_GeneralFEdata(self._ant_dongle.channel_FE, self.AccumlatedElapsedTime, self.AccumlatedDistanceTravelled, self.Speed, self.Heart)
            self.fedata = self._ant_dongle.ComposeMessage(self._ant_dongle.msgID_BroadcastData, self.info)


    def Rollovercalc(self,rollovervar, limit):
        if rollovervar <= limit:
            Accumulatedvar = rollovervar
        else:
            rollovercount = int(rollovervar/ limit)
            Accumulatedvar = rollovervar - (rollovercount * limit)
        return Accumulatedvar