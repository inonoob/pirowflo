# ---------------------------------------------------------------------------
# Original code from the FortiusANT Repo
# https://github.com/WouterJD/FortiusANT
# ---------------------------------------------------------------------------
#


import binascii
import os

import struct
import usb.core
import time

import structconstants      as sc


# ---------------------------------------------------------------------------
# Our own choice what channels are used
#
# Note that a running program cannot be slave AND master for same device
# since the channels are statically assigned!
# ---------------------------------------------------------------------------
# M A X #   c h a n n e l s   m a y   b e   8   s o   b e w a r e   h e r e !
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
# 5.2.1 Channel Type
# 5.3   Establishing a channel (defines master/slave)
# 9.3   ANT Message summary
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# c l s A n t D o n g l e
# ---------------------------------------------------------------------------
# function  Encapsulate all operations required on the AntDongle
#
# attributes
#
# functions __init__
#
# ---------------------------------------------------------------------------
class clsAntDongle():
    channel_FE = 0  # ANT+ channel for Fitness Equipment
    channel_FE_s = channel_FE  # slave=Cycle Training Program

    DeviceNumber_FE = 57591  # These are the device-numbers FortiusANT uses and

    ModelNumber_FE = 2875  # short antifier-value=0x8385, Tacx Neo=2875
    SerialNumber_FE = 19590705  # int   1959-7-5
    HWrevision_FE = 1  # char
    SWrevisionMain_FE = 1  # char
    SWrevisionSupp_FE = 1  # char
    ChannelType_BidirectionalReceive = 0x00  # Slave
    ChannelType_BidirectionalTransmit = 0x10  # Master

    ChannelType_UnidirectionalReceiveOnly = 0x40  # Slave
    ChannelType_UnidirectionalTransmitOnly = 0x50  # Master

    ChannelType_SharedBidirectionalReceive = 0x20  # Slave
    ChannelType_SharedBidirectionalTransmit = 0x30  # Master

    msgID_RF_EVENT = 0x01

    msgID_ANTversion = 0x3e
    msgID_BroadcastData = 0x4e
    msgID_AcknowledgedData = 0x4f
    msgID_ChannelResponse = 0x40
    msgID_Capabilities = 0x54

    msgID_UnassignChannel = 0x41
    msgID_AssignChannel = 0x42
    msgID_ChannelPeriod = 0x43
    msgID_ChannelRfFrequency = 0x45
    msgID_SetNetworkKey = 0x46
    msgID_ResetSystem = 0x4a
    msgID_OpenChannel = 0x4b
    msgID_RequestMessage = 0x4d

    msgID_ChannelID = 0x51  # Set, but also receive master channel - but how/when?
    msgID_ChannelTransmitPower = 0x60

    msgID_StartUp = 0x6f

    msgID_BurstData = 0x50

    # profile.xlsx: antplus_device_type
    DeviceTypeID_fitness_equipment = 17

    # Manufacturer ID       see FitSDKRelease_21.20.00 profile.xlsx
    Manufacturer_garmin = 1
    Manufacturer_dynastream = 15
    Manufacturer_dev = 255
    Manufacturer_waterrower = 118

    DeviceTypeID_FE = DeviceTypeID_fitness_equipment

    TransmissionType_IC = 0x01  # 5.2.3.1   Transmission Type
    TransmissionType_IC_GDP = 0x05  # 0x01 = Independant Channel
    #           0x04 = Global datapages used
    TransmitPower_0dBm = 0x03  # 9.4.3     Output Power Level Settings
    RfFrequency_2457Mhz = 57  # 9.5.2.6   Channel RF Frequency
    devAntDongle = None  # There is no dongle connected yet
    OK = False
    DeviceID = None
    Message = ''
    Cycplus = False
    DongleReconnected = True

    # -----------------------------------------------------------------------
    # _ _ i n i t _ _
    # -----------------------------------------------------------------------
    # Function  Create the class and try to find a dongle
    # -----------------------------------------------------------------------
    def __init__(self, DeviceID=None):
        self.DeviceID = DeviceID
        self.OK = True  # Otherwise we're disabled!!
        self.OK = self.__GetDongle()

    # -----------------------------------------------------------------------
    # G e t D o n g l e
    # -----------------------------------------------------------------------
    # input     self.DeviceID               If a specific dongle is selected
    #
    # function  find antDongle (defined types only)
    #
    # output    self.devAntDongle           False if failed
    #           self.Message                Readable end-user message
    #
    # returns   True/False
    # -----------------------------------------------------------------------
    def __GetDongle(self):
        print("start search for dongle")
        self.Message = ''
        self.Cycplus = False
        self.DongleReconnected = False

        if self.DeviceID == None:
            dongles = {(4104, "Suunto"), (4105, "Garmin"), (4100, "Older")}
            #print(dongles)
        else:
            dongles = {(self.DeviceID, "(provided)")}

        # -------------------------------------------------------------------
        # https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
        # -------------------------------------------------------------------
        found_available_ant_stick = False
        # -------------------------------------------------------------------
        # Check the known (and supported) dongle types
        # Removed: if platform.system() in [ 'Windows', 'Darwin', 'Linux' ]:
        # -------------------------------------------------------------------
        for dongle in dongles:
            ant_pid = dongle[0]
            try:
                # -----------------------------------------------------------
                # Find the ANT-dongles of this type
                # Note: filter on idVendor=0x0fcf is removed
                # -----------------------------------------------------------
                self.Message = "No (free) ANT-dongle found"
                devAntDongles = usb.core.find(find_all=True, idProduct=ant_pid)
            except Exception as e:
                if "AttributeError" in str(e):
                    self.Message = "GetDongle - Could not find dongle: " + str(e)
                elif "No backend" in str(e):
                    self.Message = "GetDongle - No backend, check libusb: " + str(e)
                else:
                    self.Message = "GetDongle: " + str(e)
            else:
                # -----------------------------------------------------------
                # Try all dongles of this type (as returned by usb.core.find)
                # -----------------------------------------------------------
                for self.devAntDongle in devAntDongles:

                        # prints "DEVICE ID 0fcf:1009 on Bus 000 Address 001 ================="
                        # But .Bus and .Address not found for logging
                    # -------------------------------------------------------
                    # Initialize the dongle
                    # -------------------------------------------------------
                    try:  # check if in use
                        # -------------------------------------------------------
                        # As suggested by @ElDonad Elie Donadio
                        # -------------------------------------------------------
                        if os.name == 'posix':
                            for config in self.devAntDongle:
                                for i in range(config.bNumInterfaces):
                                    if self.devAntDongle.is_kernel_driver_active(i):
                                        self.devAntDongle.detach_kernel_driver(i)
                        # -------------------------------------------------------
                        self.devAntDongle.set_configuration()

                        for _ in range(2):
                            # ---------------------------------------------------
                            # If not succesfull immediatly, repeat this
                            # As suggested by @martin-vi
                            # ---------------------------------------------------
                            reset_string = self.msg4A_ResetSystem()  # reset string probe
                            # same as ResetDongle()
                            # done here to have explicit error-handling.
                            self.devAntDongle.write(0x01, reset_string)
                            time.sleep(0.500)  # after reset, 500ms before next action

                            reply = self.Read(False)

                            self.Message = "No expected reply from dongle"
                            for s in reply:
                                synch, length, id, _info, _checksum, _rest, _c, _d = self.DecomposeMessage(s)
                                if synch == 0xa4 and length == 0x01 and id == 0x6f:
                                    found_available_ant_stick = True
                                    print("Using %s dongle" % self.devAntDongle.manufacturer)  # dongle[1]
                                    self.Message = self.Message.replace('\0', '')  # .manufacturer is NULL-terminated
                                    if 'CYCPLUS' in self.Message:
                                        self.Cycplus = True

                            # ---------------------------------------------------
                            # If found, then done - else retry to reset
                            # ---------------------------------------------------
                            if found_available_ant_stick: break

                    except usb.core.USBError as e:  # cannot write to ANT dongle
                        self.Message = "GetDongle - ANT dongle in use"

                    except Exception as e:
                        self.Message = "GetDongle: " + str(e)

                    # -------------------------------------------------------
                    # If found, don't try the next ANT-dongle of this type
                    # -------------------------------------------------------
                    if found_available_ant_stick: break

            # ---------------------------------------------------------------
            # If found, don't try the next type
            # ---------------------------------------------------------------
            if found_available_ant_stick: break

        # -------------------------------------------------------------------
        # Done
        # If no success, invalidate devAntDongle
        # -------------------------------------------------------------------
        if not found_available_ant_stick: self.devAntDongle = None
        return found_available_ant_stick

    # -----------------------------------------------------------------------
    # W r i t e
    # -----------------------------------------------------------------------
    # input     messages    an array of data-buffers
    #
    #           receive     after sending the data, receive all responses
    #           drop        the caller does not process the returned data
    #
    # function  write all strings to antDongle
    #           read responses from antDongle
    #
    # returns   rtn         the string-array as received from antDongle
    # -----------------------------------------------------------------------
    def Write(self, messages, receive=True, drop=True):
        rtn = []
        #print(self.OK)
        if self.OK:  # If no dongle ==> no action at all

            for message in messages:
                #print("this is the message: {0}".format(message))
                # -----------------------------------------------------------
                # Logging
                # -----------------------------------------------------------
                # -----------------------------------------------------------
                # Send the message
                # No error recovery here, will be done on the subsequent Read()
                #       that fails, which is done either here or by application.
                # -----------------------------------------------------------
                try:
                    self.devAntDongle.write(0x01, message)  # input:   endpoint address, buffer, timeout
                    # returns:
                except Exception as e:
                    print("error {0}".format(e))

                # -----------------------------------------------------------
                # Read all responses
                # -----------------------------------------------------------
                if receive:
                    data = self.Read(drop)
                    #print("response: {0}".format(data))
                    for d in data: rtn.append(d)

        return rtn

    # ---------------------------------------------------------------------------
    # R e a d
    # ---------------------------------------------------------------------------
    # input     drop           the caller does not process the returned data
    #                          this flag impacts the logfile only!
    #
    # function  read response from antDongle
    #
    # returns   return array of data-buffers
    # ---------------------------------------------------------------------------
    # Dongle disconnect recovery
    # summary           This is introduced for the CYCPLUS dongles that appear
    #                   do disconnect during a session. Reason unknown.
    #                   Thanks to @mattipee and @ElDonad for persistent
    #                   investigations!
    #                   See https://github.com/WouterJD/FortiusANT/issues/65
    #
    # __ReadAndRetry    checks the succesfull read from the dongle.
    #                   If an error occurs, the dongle is reconnected and
    #                   the DongleReconnected flag is raised, signalling the
    #                   caller that the channels must be reinitiated.
    #                   This is usefull, so that the calling process does not
    #                   need to check this after every call, in the outer loop
    #                   is enough.
    #
    # ApplicationRestart must be called to reset the flag, a good place to do
    #                   this is before the channel-initiating routines
    # ---------------------------------------------------------------------------
    def ApplicationRestart(self):
        self.DongleReconnected = False

    def __ReadAndRetry(self):
        failed = False
        try:
            trv = []  # initialize because is processed even after exception
            trv = self.devAntDongle.read(0x81, 1000, 20)  # input:   endpoint address, length, timeout
            # returns: an array of bytes
        # ----------------------------------------------------------------------
        # https://docs.python.org/3/library/exceptions.html
        # ----------------------------------------------------------------------
        # TimeoutError not raised on all systems, inspect text-message as well.
        # "timeout error" on most systems, "timed out" on Macintosh.
        # ----------------------------------------------------------------------
        except TimeoutError:
            pass
        except Exception as e:
            if "timeout error" in str(e) or "timed out" in str(e):
                pass
            else:
                failed = True
        # ----------------------------------------------------------------------
        # Recover from Exception
        # If the dongle does not come back, it's an infinite loop. Bad luck.
        #
        # When an AntDongle is unplugged and put back in again, the reading from
        # the dongle continues. BUT: the channel definition is lost.
        # So we have to signal to the calling application to repair!
        #
        # Still, this recovery is not useless. The dongle is connected again.
        # the caller must redo the channels.
        # ----------------------------------------------------------------------
        while failed:
            time.sleep(1)
            if self.__GetDongle():
                failed = False  # Exception resolved
                self.DongleReconnected = True
        return trv

    def Read(self, drop):
        # -------------------------------------------------------------------
        # Read from antDongle untill no more data (timeout), or error
        # Usually, dongle gives one buffer at the time, starting with 0xa4
        # Sometimes, multiple messages are received together on one .read
        #
        # https://www.thisisant.com/forum/view/viewthread/812
        # -------------------------------------------------------------------
        data = []
        while self.OK:  # If no dongle ==> no action at all
            trv = self.__ReadAndRetry()
            if len(trv) == 0:
                break
            # --------------------------------------------------------------------------
            # Handle content returned by .read()
            # --------------------------------------------------------------------------


            start = 0
            while start < len(trv):
                error = False
                # -------------------------------------------------------
                # Each message starts with a4; skip characters if not
                # -------------------------------------------------------
                skip = start
                while skip < len(trv) and trv[skip] != 0xa4:
                    skip += 1
                if skip != start:
                    start = skip
                # -------------------------------------------------------
                # Second character in the buffer (element in trv) is length of
                # the info; add four for synch, len, id and checksum
                # -------------------------------------------------------
                if start + 1 < len(trv):
                    length = trv[start + 1] + 4
                    if start + length <= len(trv):
                        # -------------------------------------------------------
                        # Check length and checksum
                        # Append to return array when correct
                        # -------------------------------------------------------
                        d = bytes(trv[start: start + length])
                        checksum = d[-1:]
                        expected = self.CalcChecksum(d)

                        if expected != checksum:
                            error = "error: checksum incorrect"
                        else:
                            data.append(d)  # add data to array
                    else:
                        error = "error: message exceeds buffer length"
                        break
                else:
                    break

                # -------------------------------------------------------
                # Next buffer in trv
                # -------------------------------------------------------
                start += length
        return data

    # -----------------------------------------------------------------------
    # Standard dongle commands
    # Observation: all commands have two bytes 00 00 for which purpose is unclear
    # ------------------------------------------------------------------------------
    # Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
    #   ANT:     D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
    #   trainer: D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
    #   hrm:     D00000693_-_ANT+_Device_Profile_-_Heart_Rate_Rev_2.1.pdf
    # ---------------------------------------------------------------------------
    def Calibrate(self):

        self.ResetDongle()
        print("calibration")

        messages = [
            self.msg4D_RequestMessage(0, self.msgID_Capabilities),  # request max channels
            self.msg4D_RequestMessage(0, self.msgID_ANTversion),  # request ant version
            self.msg46_SetNetworkKey(),
            #self.msg46_SetNetworkKey(NetworkNumber=0x01, NetworkKey=0x00),
            # network for Tacx i-Vortex
        ]
        self.Write(messages)

    def ResetDongle(self):
        if self.Cycplus:
            # For CYCPLUS dongles this command may be given on initialization only
            # If done lateron, the dongle hangs
            # Note that __GetDongle() does not use this routine!
            pass
        else:
            messages = [
                self.msg4A_ResetSystem(),
            ]
            self.Write(messages, False)
        time.sleep(0.500)  # After Reset, 500ms before next action


    def Trainer_ChannelConfig(self):
        messages = [
            self.msg42_AssignChannel(self.channel_FE, self.ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
            self.msg51_ChannelID(self.channel_FE, self.DeviceNumber_FE, self.DeviceTypeID_FE, self.TransmissionType_IC_GDP),
            self.msg45_ChannelRfFrequency(self.channel_FE, self.RfFrequency_2457Mhz),
            self.msg43_ChannelPeriod(self.channel_FE, ChannelPeriod=8192),  # 4 Hz
            self.msg60_ChannelTransmitPower(self.channel_FE, self.TransmitPower_0dBm),
            self.msg4B_OpenChannel(self.channel_FE)
        ]
        print("create Channel")
        self.Write(messages)

    # -------------------------------------------------------------------------------
    # E n u m e r a t e A l l
    # -------------------------------------------------------------------------------
    # input     none
    #
    # function  list all usb-devices
    #
    # returns   none
    # -------------------------------------------------------------------------------
    def EnumerateAll(self):
        devices = usb.core.find(find_all=True)
        for device in devices:
            #       print (device)
            s = "manufacturer=%7s, product=%15s, vendor=%6s, product=%6s(%s)" % \
                (device.manufacturer, device.product, \
                 hex(device.idVendor), hex(device.idProduct), device.idProduct)


            i = 0
            for cfg in device:  # Do not understand this construction; see pyusb tutorial
                i += 1
                for intf in cfg:
                    for _ep in intf:
                        pass



    # -------------------------------------------------------------------------------
    # C a l c C h e c k s u m
    # -------------------------------------------------------------------------------
    # input     ANT message,
    #               e.g. "a40340000103e5" where last byte may be the checksum itself
    #                     s l i .1.2.3    synch=a4, len=03, id=40, info=000103, checksum=e5
    #
    # function  Calculate the checksum over synch + length + id + info (3 + info)
    #
    # returns   checksum, which should match the last two characters
    # -------------------------------------------------------------------------------
    def calc_checksum(self,message):
        return self.CalcChecksum(message)  # alias for compatibility


    def CalcChecksum(self,message):
        xor_value = 0
        length = message[1]  # byte 1; length of info
        length += 3  # Add synch, len, id
        for i in range(0, length):  # Process bytes as defined in length
            xor_value = xor_value ^ message[i]

        #   print('checksum', logfile.HexSpace(message), xor_value, bytes([xor_value]))

        return bytes([xor_value])


    # -------------------------------------------------------------------------------
    # C o m p o s e   A N T   M e s s a g e
    # -------------------------------------------------------------------------------
    def ComposeMessage(self,id, info):
        fSynch = sc.unsigned_char
        fLength = sc.unsigned_char
        fId = sc.unsigned_char
        fInfo = str(len(info)) + sc.char_array  # 9 character string

        format = sc.no_alignment + fSynch + fLength + fId + fInfo
        data = struct.pack(format, 0xa4, len(info), id, info)
        # -----------------------------------------------------------------------
        # Add the checksum
        # (antifier added \00\00 after each message for unknown reason)
        # -----------------------------------------------------------------------
        data += self.calc_checksum(data)

        return data


    def DecomposeMessage(self,d):
        synch = 0
        length = 0
        id = 0
        checksum = 0
        info = binascii.unhexlify('')  # NULL-string bytes
        rest = ""  # No remainder (normal)

        if len(d) > 0:          synch = d[0]  # Carefull approach
        if len(d) > 1:          length = d[1]
        if len(d) > 2:          id = d[2]
        if len(d) > 3 + length:
            if length:          info = d[3:3 + length]  # Info, if length > 0
            checksum = d[3 + length]  # Character after info
        if len(d) > 4 + length: rest = d[4 + length:]  # Remainder (should not occur)

        Channel = -1
        DataPageNumber = -1
        if length >= 1: Channel = d[3]
        if length >= 2: DataPageNumber = d[4]
        #
        # ---------------------------------------------------------------------------
        # Special treatment for Burst data
        # Note that SequenceNumber is not returned and therefore lost, which is to
        #      be implemented as soon as we will use msgID_BurstData
        # ---------------------------------------------------------------------------
        if id == self.msgID_BurstData:
            _SequenceNumber = (Channel & 0b11100000) >> 5  # Upper 3 bits
            Channel = Channel & 0b00011111  # Lower 5 bits

        return synch, length, id, info, checksum, rest, Channel, DataPageNumber

    # ==============================================================================
    # ANT+ message interface
    # ==============================================================================

    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   41   U n a s s i g n C h a n n e l
    # ------------------------------------------------------------------------------
    def msg41_UnassignChannel(self, ChannelNumber):
        format = sc.no_alignment + sc.unsigned_char
        info = struct.pack(format, ChannelNumber)
        msg = self.ComposeMessage(0x41, info)
        return msg


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   42   A s s i g n C h a n n e l
    # ------------------------------------------------------------------------------
    def msg42_AssignChannel(self, ChannelNumber, ChannelType, NetworkNumber):
        format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char + sc.unsigned_char
        info = struct.pack(format, ChannelNumber, ChannelType, NetworkNumber)
        msg = self.ComposeMessage(0x42, info)
        return msg


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   43   C h a n n e l P e r i o d
    # ------------------------------------------------------------------------------
    def msg43_ChannelPeriod(self, ChannelNumber, ChannelPeriod):
        format = sc.no_alignment + sc.unsigned_char + sc.unsigned_short
        info = struct.pack(format, ChannelNumber, ChannelPeriod)
        msg = self.ComposeMessage(0x43, info)
        return msg


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   45   C h a n n e l R f F r e q u e n c y
    # ------------------------------------------------------------------------------
    def msg45_ChannelRfFrequency(self, ChannelNumber, RfFrequency):
        format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char
        info = struct.pack(format, ChannelNumber, RfFrequency)
        msg = self.ComposeMessage(0x45, info)
        return msg


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   46   S e t N e t w o r k K e y
    # ------------------------------------------------------------------------------
    def msg46_SetNetworkKey(self, NetworkNumber=0x00, NetworkKey=0x45c372bdfb21a5b9):
        format = sc.no_alignment + sc.unsigned_char + sc.unsigned_long_long
        info = struct.pack(format, NetworkNumber, NetworkKey)
        print("set Networkkey:{0}".format(info))
        msg = self.ComposeMessage(0x46, info)
        return msg


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   4A   R e s e t   S y s t e m
    # ------------------------------------------------------------------------------
    def msg4A_ResetSystem(self):
        format = sc.no_alignment + sc.unsigned_char
        info = struct.pack(format, 0x00)
        msg = self.ComposeMessage(0x4a, info)
        return msg


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   4B   O p e n C h a n n e l
    # ------------------------------------------------------------------------------
    def msg4B_OpenChannel(self, ChannelNumber):
        format = sc.no_alignment + sc.unsigned_char
        info = struct.pack(format, ChannelNumber)
        msg = self.ComposeMessage(0x4b, info)
        return msg


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   4D   R e q u e s t   M e s s a g e
    # ------------------------------------------------------------------------------
    def msg4D_RequestMessage(self,ChannelNumber, RequestedMessageID):
        format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char
        info = struct.pack(format, ChannelNumber, RequestedMessageID)
        msg = self.ComposeMessage(0x4d, info)
        return msg


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   51   C h a n n e l I D
    # ------------------------------------------------------------------------------
    # D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
    # Page  17.   5.2.3 Channel ID
    # Page  66. 9.5.2.3 Set Channel ID (0x51)
    # Page 121. 9.5.7.2 Channel ID (0x51)
    # ------------------------------------------------------------------------------
    def msg51_ChannelID(self,ChannelNumber, DeviceNumber, DeviceTypeID, TransmissionType):
        format = sc.no_alignment + sc.unsigned_char + sc.unsigned_short + sc.unsigned_char + sc.unsigned_char
        info = struct.pack(format, ChannelNumber, DeviceNumber, DeviceTypeID, TransmissionType)
        msg = self.ComposeMessage(0x51, info)
        return msg


    def unmsg51_ChannelID(self,info):
        #                              0                  1                   2                  3
        format = sc.no_alignment + sc.unsigned_char + sc.unsigned_short + sc.unsigned_char + sc.unsigned_char
        tuple = struct.unpack(format, info)

        return tuple[0], tuple[1], tuple[2], tuple[3]


    # ------------------------------------------------------------------------------
    # A N T   M e s s a g e   60   C h a n n e l T r a n s m i t P o w e r
    # ------------------------------------------------------------------------------
    def msg60_ChannelTransmitPower(self, ChannelNumber, TransmitPower):
        format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char
        info = struct.pack(format, ChannelNumber, TransmitPower)
        msg = self.ComposeMessage(0x60, info)
        return msg


    # ------------------------------------------------------------------------------
    # U n m s g 6 4   C h a n n e l R e s p o n s e
    # ------------------------------------------------------------------------------
    # D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
    # 9.5.6 Channel response / event messages
    # ------------------------------------------------------------------------------
    def unmsg64_ChannelResponse(self, info):
        nChannel = 0
        fChannel = sc.unsigned_char

        nInitiatingMessageID = 1
        fInitiatingMessageID = sc.unsigned_char

        nResponseCode = 2
        fResponseCode = sc.unsigned_char

        format = sc.no_alignment + fChannel + fInitiatingMessageID + fResponseCode
        tuple = struct.unpack(format, info)

        return tuple[nChannel], tuple[nInitiatingMessageID], tuple[nResponseCode]



    # ------------------------------------------------------------------------------
    # P a g e 1 6   G e n e r a l   F E   i n f o
    # ------------------------------------------------------------------------------
    # Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
    #  trainer: D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
    #           Data page 16 (0x10) General FE Data
    # Notes:    Even though HRM is defined, it appears not being picked up by
    #           Trainer Road.
    # ------------------------------------------------------------------------------
    def msgPage16_GeneralFEdata(self, Channel, ElapsedTime, DistanceTravelled, Speed, HeartRate):
        DataPageNumber = 16
        EquipmentType = 0x16  # Rower
        ElapsedTime = int(min(0xff, ElapsedTime))
        DistanceTravelled = int(min(0xff, DistanceTravelled))
        Speed = int(min(0xffff, Speed))
        HeartRate = int(min(0xff, HeartRate))
        #Capabilities = 0x30 | 0x03 | 0x00 | 0x00  # IN_USE | HRM | Distance | Speed
        Capabilities = 0x37   # IN_USE | HRM | Distance | Speed

        # #               bit 7.... ...0
        # HRM =               0b00000011  # 0b____ __xx bits 0-1 0 = hand contact sensor    (2020-12-28 Unclear why option chosen)
        # Distance =          0b00000000  # 0b____ _x__ bit 2    1 = No distance in byte 3  (2020-12-28 Unclear why option chosen)
        # VirtualSpeedFlag =  0b00000000  # 0b____ x___ bit 3    0 = Real speed in byte 4/5 (2020-12-28 Could be virtual speed)
        # FEstate =           0b00110000  # 0b_xxx ____ bits 4-6 3 = IN USE
        # LapToggleBit =      0b00000000  # 0bx___ ____ bit 7    0 = No lap toggle

        fChannel = sc.unsigned_char  # First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
        fEquipmentType = sc.unsigned_char
        fElapsedTime = sc.unsigned_char
        fDistanceTravelled = sc.unsigned_char
        fSpeed = sc.unsigned_short
        fHeartRate = sc.unsigned_char
        fCapabilities = sc.unsigned_char

        format = sc.no_alignment + fChannel + fDataPageNumber + fEquipmentType + fElapsedTime + fDistanceTravelled + fSpeed + fHeartRate + fCapabilities
        info = struct.pack(format, Channel, DataPageNumber, EquipmentType, ElapsedTime, DistanceTravelled, Speed, HeartRate,
                           Capabilities)

        return info


    def msgUnpage16_GeneralFEdata(self,info):
        fChannel = sc.unsigned_char  # 0 First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # 1 First byte of the ANT+ datapage (payload)
        fEquipmentType = sc.unsigned_char  # 2
        fElapsedTime = sc.unsigned_char  # 3
        fDistanceTravelled = sc.unsigned_char  # 4
        fSpeed = sc.unsigned_short  # 5
        fHeartRate = sc.unsigned_char  # 6
        fCapabilities = sc.unsigned_char  # 7

        format = sc.no_alignment + fChannel + fDataPageNumber + fEquipmentType + fElapsedTime + fDistanceTravelled + fSpeed + fHeartRate + fCapabilities
        tuple = struct.unpack(format, info)

        return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6], tuple[7]


    # ------------------------------------------------------------------------------
    # P a g e 2 5   T r a i n e r   i n f o
    # ------------------------------------------------------------------------------
    # Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
    #  trainer: D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
    #           Data page 25 (0x19) Specific Trainer/Stationary Bike Data
    # ------------------------------------------------------------------------------
    def msgPage25_TrainerData(self,Channel, EventCounter, Cadence, AccumulatedPower, CurrentPower):
        DataPageNumber = 25
        EventCounter = int(min(0xff, EventCounter))
        Cadence = int(min(0xff, Cadence))
        AccumulatedPower = int(min(0xffff, AccumulatedPower))
        CurrentPower = int(min(0x0fff, CurrentPower))
        Flags = 0x34

        # #               bit 7.... ...0
        # HRM =               0b00000001  # 0b____ ___x bits 0-1 1 = Accumulated Strokes
        # HRM =               0b00000000  # 0b____ __x_ bits 1   0 = Reserved
        # Distance =          0b00000000  # 0b____ _x__ bit 2    0 = Reserved
        # VirtualSpeedFlag =  0b00000000  # 0b____ X___ bit 3    0 = Reserved
        # FEstate =           0b00110000  # 0b_xxx ____ bits 4-6 3 = IN USE
        # LapToggleBit =      0b00000000  # 0bx___ ____ bit 7    0 = No lap toggle


        fChannel = sc.unsigned_char  # First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
        fEvent = sc.unsigned_char
        fCadence = sc.unsigned_char
        fAccPower = sc.unsigned_short
        fInstPower = sc.unsigned_short  # The first four bits have another meaning!!
        fFlags = sc.unsigned_char

        format = sc.no_alignment + fChannel + fDataPageNumber + fEvent + fCadence + fAccPower + fInstPower + fFlags
        info = struct.pack(format, Channel, DataPageNumber, EventCounter, Cadence, AccumulatedPower, CurrentPower, Flags)

        return info


    def msgUnpage25_TrainerData(self,info):
        fChannel = sc.unsigned_char  # 0 First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # 1 First byte of the ANT+ datapage (payload)
        fEvent = sc.unsigned_char  # 2
        fCadence = sc.unsigned_char  # 3
        fAccPower = sc.unsigned_short  # 4
        fInstPower = sc.unsigned_short  # 5 The first four bits have another meaning!!
        fFlags = sc.unsigned_char  # 6

        format = sc.no_alignment + fChannel + fDataPageNumber + fEvent + fCadence + fAccPower + fInstPower + fFlags
        tuple = struct.unpack(format, info)

        return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6]


    # ------------------------------------------------------------------------------
    # P a g e 2 5   T r a i n e r   i n f o
    # ------------------------------------------------------------------------------
    # Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
    #  trainer: D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
    #           Data page 22 (0x16) Specific Rower Data
    # ------------------------------------------------------------------------------
    def msgPage22_RowingData(self,Channel, StrokeCount, Cadence, InstPower):
        DataPageNumber = 22
        Reserved = 0xff
        Reserved = 0xff
        StrokeCount = int(min(0xff, StrokeCount))
        Cadence = int(min(0xfe, Cadence))
        InstPower = int(min(0xfffe, InstPower))
        Flags = 0x31  # 00110000 Hmmm.... leave as is but do not understand the value
        #todo: thin about the lap flag for 500m splits

        fChannel = sc.unsigned_char  # First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
        fReserved = sc.unsigned_char
        fStrokeCount = sc.unsigned_char
        fCadence = sc.unsigned_char
        fInstPower = sc.unsigned_short  # The first four bits have another meaning!!
        fFlags = sc.unsigned_char

        format = sc.no_alignment + fChannel + fDataPageNumber + fReserved + fReserved + fStrokeCount + fCadence + fInstPower + fFlags
        info = struct.pack(format, Channel, DataPageNumber, Reserved, Reserved, StrokeCount, Cadence, InstPower, Flags)

        return info


    def msgUnPage22_RowingData(self,info):
        fChannel = sc.unsigned_char  # First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
        fReserved = sc.unsigned_char
        fStrokeCount = sc.unsigned_char
        fCadence = sc.unsigned_char
        fInstPower = sc.unsigned_short
        fFlags = sc.unsigned_char

        format = sc.no_alignment + fChannel + fDataPageNumber + fReserved + fReserved + fStrokeCount + fCadence + fInstPower + fFlags
        tuple = struct.unpack(format, info)

        return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6], tuple[7]



    # ------------------------------------------------------------------------------
    # P a g e 8 0 _ M a n u f a c t u r e r I n f o
    # ------------------------------------------------------------------------------
    # Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
    # D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
    # Common Data Page 80: (0x50) Manufacturers Information
    # ------------------------------------------------------------------------------
    def msgPage80_ManufacturerInfo(self,Channel, Reserved1, Reserved2, HWrevision, ManufacturerID, ModelNumber):
        DataPageNumber = 80

        fChannel = sc.unsigned_char  # First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
        fReserved1 = sc.unsigned_char
        fReserved2 = sc.unsigned_char
        fHWrevision = sc.unsigned_char
        fManufacturerID = sc.unsigned_short
        fModelNumber = sc.unsigned_short

        # page 28 byte 4,5,6,7- 15=dynastream, 89=tacx
        # antifier used 15 : "a4 09 4e 00 50 ff ff 01 0f 00 85 83 bb"
        # we use 89 (tacx) with the same ModelNumber
        #
        # Should be variable and caller-supplied; perhaps it influences pairing
        # when trainer-software wants a specific device?
        #
        format = sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fReserved2 + fHWrevision + fManufacturerID + fModelNumber
        info = struct.pack(format, Channel, DataPageNumber, Reserved1, Reserved2, HWrevision, ManufacturerID, ModelNumber)

        return info


    def msgUnpage80_ManufacturerInfo(self,info):
        fChannel = sc.unsigned_char  # 0 First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # 1 First byte of the ANT+ datapage (payload)
        fReserved1 = sc.unsigned_char  # 2
        fReserved2 = sc.unsigned_char  # 3
        fHWrevision = sc.unsigned_char  # 4
        fManufacturerID = sc.unsigned_short  # 5
        fModelNumber = sc.unsigned_short  # 6

        format = sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fReserved2 + fHWrevision + fManufacturerID + fModelNumber
        tuple = struct.unpack(format, info)

        return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6]


    # ------------------------------------------------------------------------------
    # P a g e 8 1   P r o d u c t I n f o r m a t i o n
    # ------------------------------------------------------------------------------
    # Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
    # D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
    # Common Data Page 81: (0x51) Product Information
    # ------------------------------------------------------------------------------
    def msgPage81_ProductInformation(self,Channel, Reserved1, SWrevisionSupp, SWrevisionMain, SerialNumber):
        DataPageNumber = 81

        fChannel = sc.unsigned_char  # First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
        fReserved1 = sc.unsigned_char
        fSWrevisionSupp = sc.unsigned_char
        fSWrevisionMain = sc.unsigned_char
        fSerialNumber = sc.unsigned_int

        format = sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fSWrevisionSupp + fSWrevisionMain + fSerialNumber
        info = struct.pack(format, Channel, DataPageNumber, Reserved1, SWrevisionSupp, SWrevisionMain, SerialNumber)

        return info


    def msgUnpage81_ProductInformation(self,info):
        fChannel = sc.unsigned_char  # 0 First byte of the ANT+ message content
        fDataPageNumber = sc.unsigned_char  # 1 First byte of the ANT+ datapage (payload)
        fReserved1 = sc.unsigned_char  # 2
        fSWrevisionSupp = sc.unsigned_char  # 3
        fSWrevisionMain = sc.unsigned_char  # 4
        fSerialNumber = sc.unsigned_int  # 5

        format = sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fSWrevisionSupp + fSWrevisionMain + fSerialNumber
        tuple = struct.unpack(format, info)

        return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5]