#!/usr/bin/env python3

import logging

import signal

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from queue import Queue

from ble import (
    Advertisement,
    Characteristic,
    Service,
    Application,
    find_adapter,
    Descriptor,
    Agent,
)

import struct
import array
from enum import Enum

import sys

MainLoop = None
try:
    from gi.repository import GLib

    MainLoop = GLib.MainLoop
except ImportError:
    import gobject as GObject

    MainLoop = GObject.MainLoop

DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"

GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
GATT_DESC_IFACE = "org.bluez.GattDescriptor1"

LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
filelogHandler = logging.FileHandler("logs.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
filelogHandler.setFormatter(formatter)
logger.addHandler(filelogHandler)
logger.addHandler(logHandler)

out_q = []

mainloop = None

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.InvalidValueLength"


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Failed"


def register_app_cb():
    logger.info("GATT application registered")


def register_app_error_cb(error):
    logger.critical("Failed to register application: " + str(error))
    mainloop.quit()

def request_reset_ble():
    out_q.put("reset_ble")
    return out_q


class DeviceInformation(Service):
    DEVICE_INFORMATION_UUID = '180A'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.DEVICE_INFORMATION_UUID, True)
        self.add_characteristic(ManufacturerNameString(bus, 0, self))
        self.add_characteristic(SoftwareRevisionString(bus, 1, self))


class SoftwareRevisionString(Characteristic):
    SOFTWARE_REVISION_STRING_UUID = '2a28'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.SOFTWARE_REVISION_STRING_UUID,
            ['read'],
            service)
        self.notifying = False
        #self.value = [dbus.Byte(0), dbus.Byte(0), dbus.Byte(0), dbus.Byte(0)]  # ble com module waterrower software revision
        self.value = [dbus.Byte(0), dbus.Byte(0), dbus.Byte(0)]  # ble com module waterrower software revision

        self.value[0] = 0x34
        self.value[1] = 0x2E
        self.value[2] = 0x33
        #self.value[3] = 0x30

    def ReadValue(self, options):
        print('SoftwareRevisionString: ' + repr(self.value))
        return self.value


class ManufacturerNameString(Characteristic):
    MANUFACTURER_NAME_STRING_UUID = '2a29'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.MANUFACTURER_NAME_STRING_UUID,
            ['read'],
            service)
        self.notifying = False
        self.ManuName = bytes('WaterRower', 'utf-8')
        self.value = dbus.Array(self.ManuName)  # ble com module waterrower software revision


    def ReadValue(self, options):
        print('SoftwareRevisionString: ' + repr(self.value))
        return self.value

class FTMservice(Service):
    FITNESS_MACHINE_UUID = '1826'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.FITNESS_MACHINE_UUID, True)
       # self.add_characteristic(FitnessMachineFeature(bus,0,self))
        self.add_characteristic(RowerData(bus, 1, self))
        self.add_characteristic(FitnessMachineControlPoint(bus, 2, self))


class FitnessMachineFeature(Characteristic):

    FITNESS_MACHINE_FEATURE_UUID = '2acc'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.FITNESS_MACHINE_FEATURE_UUID,
            ['read'],
            service)
        self.notifying = False
        self.value = [dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0)]  # ble com module waterrower software revision

        self.value[0] = 0x26
        self.value[1] = 0x56
        self.value[2] = 0x00
        self.value[3] = 0x00
        self.value[4] = 0x00
        self.value[5] = 0x00
        self.value[6] = 0x00
        self.value[7] = 0x00

        #00100110           01010110

#0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff


    def ReadValue(self, options):
        print('Fitness Machine Feature: ' + repr(self.value))
        return self.value

class RowerData(Characteristic):
    ROWING_UUID = '2ad1'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.ROWING_UUID,
            ['notify'],
            service)
        self.notifying = False
        self.iter = 0

    def Waterrower_cb(self):
        # value = [dbus.Byte(0x7F), dbus.Byte(0x3F), dbus.Byte(0), dbus.Byte(0),dbus.Byte(0),
        #         dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),
        #         dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),
        #         dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),dbus.Byte(0),
        #         ]

        value = [#dbus.Byte(0x7F), dbus.Byte(0x3F), # flag for all values
                 dbus.Byte(0x2C), dbus.Byte(0x0B),
                 dbus.Byte(0x48), dbus.Byte(0x01), dbus.Byte(0x00), #0 0 8 16 stroke rate + stroke count
                 #dbus.Byte(0x02), ## 1 1 8 av stroke rate
                 dbus.Byte(0x03), dbus.Byte(0x00), dbus.Byte(0x00), # 2 1 16 + 8 distance
                 dbus.Byte(0x04), dbus.Byte(0x00),# 3 1 16 instantaneous pace
                 #dbus.Byte(0xFF), dbus.Byte(0xFF), # 4 1 16 average pace
                 dbus.Byte(0x0C), dbus.Byte(0x00), # 5 1 16 instantaneous power
                 #dbus.Byte(0xFF), dbus.Byte(0xFF), # 6 1 16 average power
                 #dbus.Byte(0xFF), dbus.Byte(0xFF), # 7 1 16 resitance level
                 dbus.Byte(0x09), dbus.Byte(0x00),dbus.Byte(0x0F), dbus.Byte(0x00),dbus.Byte(0x01), # 8 1 16 + 16 +16 Total energy, energy per hour, energy per minute
                 dbus.Byte(0x0F), # 9 1  8 heart rate
                 #dbus.Byte(0xFF), # 10 1 8 metabolic equivalent 0.1
                 dbus.Byte(0x0F),dbus.Byte(0x00), # 11 1 16 elapsed time
                 #dbus.Byte(0xFF),dbus.Byte(0xFF), # 12 1 16 reamaining time
                 ]
                 #   1111111111110
        #0111111111111


        # 0 0 8 16 stroke rate + stroke count
        # 1 1 8 av stroke rate
        # 2 1 16 + 8 distance
        # 3 1 16 instantaneous pace
        # 4 1 16 average pace
        # 5 1 16 instantaneous power
        # 6 1 16 average power
        # 7 1 16 resitance level
        # 8 1 16 + 16 +16 Total energy, energy per hour, energy per minute
        # 9 1  8 heart rate
        # 10 1 8 metabolic equivalent 0.1
        # 11 1 16 elapsed time
        # 12 1 16 reamaining time

        # #value[0] = 0x01
        # #value[1] = 0x02
        # value[2] = 0x30 # stroke count 1 byte /2
        # value[3] = 0x01 # Stroke Count (4 3)
        # value[4] = 0x01 # Stroke Count
        # value[5] = 0x01 # Total Distance (7 5 6)
        # value[6] = 0x01 # Total Distance
        # value[7] = 0x01 # Total Distance
        # value[8] = 0x01  # Instantaneous Pace (9 8)
        # value[9] = 0x02  # Instantaneous Pace
        # value[10] = 0x96 # Instantaneous Power (11 10) (0x96)
        # value[11] = 0x01# Instantaneous Power
        # value[12] = 0x08 # Total Energy (13 12)
        # value[13] = 0x02 # Total Energy
        # value[14] = 0x01 # Energy per Hour
        # value[16] = 0x01 # Energy per Minute
        # value[17] = 0x02 # Heart Rate
        # value[18] = 0x02 # Elasped time (19 18)
        # value[19] = 0x02 # Elasped time

        # value[2] = 0x00 # stroke count 1 byte /2
        # value[3] = 0x00 # Stroke Count (4 3)
        # value[4] = 0x00  # Stroke Count
        # value[5] = 0x0A # Total Distance (7 5 6)
        # value[6] = 0x00  # Total Distance
        # value[7] = 0x00  # Total Distance
        # value[8] = 0x00  # Instantaneous Pace (9 8)
        # value[9] = 0x00  # Instantaneous Pace
        # value[10] = 0x00 # Instantaneous Power (11 10)
        # value[11] = 0x00# Instantaneous Power
        # value[12] = 0x00 # Total Energy (13 12)
        # value[13] = 0x00 # Total Energy
        # value[14] = 0x00 # Energy per Hour
        # value[16] = 0x00 # Energy per Minute
        # value[17] = 0x00 # Heart Rate
        # value[18] = 0x00 # Elasped time (19 18)
        # value[19] = 0x00 # Elasped time




    #2C - 0B - 00 - 00 - 00 - 00 - FF - FF - 00 - 00 - 00 - 00 - 00 - 00 - 00 - 00 - 00 - 00 - 00 - 00
        self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': value }, [])
        return self.notifying

    def _update_Waterrower_cb_value(self):
        print('Update Waterrower Data')

        if not self.notifying:
            return

        GLib.timeout_add(1000, self.Waterrower_cb)

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_Waterrower_cb_value()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_Waterrower_cb_value()


###### todo: function needed to get all the date from waterrower
# 20 byte is max data send
# example : 0x 2C-0B-00-00-00-00-FF-FF-00-00-00-00-00-00-00-00-00-00-00-00
# first 2 bytes: are for rowing machine details: 0B

class FitnessMachineControlPoint(Characteristic):
    FITNESS_MACHINE_CONTROL_POINT_UUID = '2ad9'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.FITNESS_MACHINE_CONTROL_POINT_UUID,
            ['indicate', 'write'],
            service)
        self.out_q = None

    def fmcp_cb(self, byte):
        print('fmcp_cb activate')
        print(byte)
        if byte == 0:
            value = [dbus.Byte(128), dbus.Byte(0), dbus.Byte(1)]
        elif byte == 1:
            value = [dbus.Byte(128), dbus.Byte(1), dbus.Byte(1)]
            request_reset_ble()
        #print(value)
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])

    def WriteValue(self, value, options):
        self.value = value
        print(value)
        byte = self.value[0]
        print('Fitness machine control point: ' + repr(self.value))
        if byte == 0:
            print('Request control')
            self.fmcp_cb(byte)
        elif byte == 1:
            print('Reset')
            self.fmcp_cb(byte)

class HeartRate(Service):
    HEART_RATE = '180D'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.HEART_RATE, True)
        self.add_characteristic(HeartRateMeasurement(bus, 0, self))

class HeartRateMeasurement(Characteristic):
    HEART_RATE_MEASUREMENT = '2a37'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.HEART_RATE_MEASUREMENT,
            ['notify'],
            service)
        self.notifying = False



    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False


class FTMPAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x77, 0x72],
        )
        self.add_service_uuid(DeviceInformation.DEVICE_INFORMATION_UUID)
        self.add_service_uuid(FTMservice.FITNESS_MACHINE_UUID)
        self.add_service_uuid(HeartRate.HEART_RATE)

        self.add_local_name("S4 COMMS 69")
        self.include_tx_power = True


def register_ad_cb():
    logger.info("Advertisement registered")


def register_ad_error_cb(error):
    logger.critical("Failed to register advertisement: " + str(error))
    mainloop.quit()

def sigint_handler(sig, frame):
    if sig == signal.SIGINT:
        mainloop.quit()
    else:
        raise ValueError("Undefined handler for '{}' ".format(sig))

AGENT_PATH = "/com/inonoob/agent"


def main(out_q):
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # get the system bus
    bus = dbus.SystemBus()
    # get the ble controller
    adapter = find_adapter(bus)

    if not adapter:
        logger.critical("GattManager1 interface not found")
        return

    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, adapter)

    adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")

    # powered property on the controller to on
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    # Get manager objs
    service_manager = dbus.Interface(adapter_obj, GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

    advertisement = FTMPAdvertisement(bus, 0)
    obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

    agent = Agent(bus, AGENT_PATH)

    app = Application(bus)
    app.add_service(DeviceInformation(bus, 1))
    app.add_service(FTMservice(bus, 2))
    app.add_service(HeartRate(bus,3))

    mainloop = MainLoop()

    agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")

    ad_manager.RegisterAdvertisement(
        advertisement.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    logger.info("Registering GATT application...")

    service_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=[register_app_error_cb],
    )

    agent_manager.RequestDefaultAgent(AGENT_PATH)

    mainloop.run()
    # ad_manager.UnregisterAdvertisement(advertisement)
    # dbus.service.Object.remove_from_connection(advertisement)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    main()
