#!/usr/bin/env python3

# ---------------------------------------------------------------------------
# Original code from the PunchThrough Repo espresso-ble
# https://github.com/PunchThrough/espresso-ble
# ---------------------------------------------------------------------------
#
import logging
import signal
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import struct

from ble import (
    Advertisement,
    Characteristic,
    Service,
    Application,
    find_adapter,
    Descriptor,
    Agent,
)

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

# Function is needed to trigger the reset of the waterrower. It puts the "reset_ble" into the queue (FIFO) in order
# for the WaterrowerInterface thread to get the signal to reset the waterrower.

def request_reset_ble():
    out_q_reset.put("reset_ble")

def Convert_Waterrower_raw_to_byte():

    WaterrowerValuesRaw = ble_in_q_value.pop()
    WRBytearray = []
    #print("Ble Values: {0}".format(WaterrowerValuesRaw))
    for keys in WaterrowerValuesRaw:
        WaterrowerValuesRaw[keys] = int(WaterrowerValuesRaw[keys])
    #todo refactor this part with the correct struct.pack e.g. 2 bytes use "H" instand of bitshifiting ?
    #print(WaterrowerValuesRaw)
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['stroke_rate'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_strokes'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_strokes'] & 0xff00) >> 8))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_distance_m'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_distance_m'] & 0xff00) >> 8))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_distance_m'] & 0xff0000) >> 16))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['instantaneous pace'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['instantaneous pace'] & 0xff00) >> 8))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['watts'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['watts'] & 0xff00) >> 8))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal'] & 0xff00) >> 8))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal_hour'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal_hour'] & 0xff00) >> 8))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal_min'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['heart_rate'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['elapsedtime'] & 0xff)))
    WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['elapsedtime'] & 0xff00) >> 8))
    return WRBytearray


class DeviceInformation(Service):
    DEVICE_INFORMATION_UUID = '180A'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.DEVICE_INFORMATION_UUID, True)
        self.add_characteristic(ManufacturerNameString(bus, 0, self))
        self.add_characteristic(ModelNumberString(bus, 1, self))
        self.add_characteristic(SerialNumberSring(bus,2,self))
        self.add_characteristic(HardwareRevisionString(bus,3,self))
        self.add_characteristic(FirmwareRevisionString(bus,4,self))
        self.add_characteristic(SoftwareRevisionString(bus, 5, self))


class ManufacturerNameString(Characteristic):
    MANUFACTURER_NAME_STRING_UUID = '2a29'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.MANUFACTURER_NAME_STRING_UUID,
            ['read'],
            service)
        self.notifying = False
        self.ManuName = bytes('Waterrower', 'utf-8')
        self.value = dbus.Array(self.ManuName)  # ble com module waterrower software revision


    def ReadValue(self, options):
        print('ManufacturerNameString: ' + repr(self.value))
        return self.value

class ModelNumberString(Characteristic):
    MANUFACTURER_NAME_STRING_UUID = '2a24'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.MANUFACTURER_NAME_STRING_UUID,
            ['read'],
            service)
        self.notifying = False
        self.ManuName = bytes('4', 'utf-8')
        self.value = dbus.Array(self.ManuName)  # ble com module waterrower software revision


    def ReadValue(self, options):
        print('ModelNumberString: ' + repr(self.value))
        return self.value

class SerialNumberSring(Characteristic):
    MANUFACTURER_NAME_STRING_UUID = '2a25'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.MANUFACTURER_NAME_STRING_UUID,
            ['read'],
            service)
        self.notifying = False
        self.ManuName = bytes('0000', 'utf-8')
        self.value = dbus.Array(self.ManuName)  # ble com module waterrower software revision


    def ReadValue(self, options):
        print('SerialNumberSring: ' + repr(self.value))
        return self.value

class HardwareRevisionString(Characteristic):
    MANUFACTURER_NAME_STRING_UUID = '2a27'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.MANUFACTURER_NAME_STRING_UUID,
            ['read'],
            service)
        self.notifying = False
        self.ManuName = bytes('2.2BLE', 'utf-8')
        self.value = dbus.Array(self.ManuName)  # ble com module waterrower software revision


    def ReadValue(self, options):
        print('HardwareRevisionString: ' + repr(self.value))
        return self.value

class FirmwareRevisionString(Characteristic):
    MANUFACTURER_NAME_STRING_UUID = '2a26'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.MANUFACTURER_NAME_STRING_UUID,
            ['read'],
            service)
        self.notifying = False
        self.ManuName = bytes('0.30', 'utf-8')
        self.value = dbus.Array(self.ManuName)  # ble com module waterrower software revision


    def ReadValue(self, options):
        print('FirmwareRevisionString: ' + repr(self.value))
        return self.value

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

class FTMservice(Service):
    FITNESS_MACHINE_UUID = '1826'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.FITNESS_MACHINE_UUID, True)
        self.add_characteristic(FitnessMachineFeature(bus,0,self))
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

        if ble_in_q_value:

            Waterrower_byte_values = Convert_Waterrower_raw_to_byte()

            value = [dbus.Byte(0x2C), dbus.Byte(0x0B),
                     dbus.Byte(Waterrower_byte_values[0]), dbus.Byte(Waterrower_byte_values[1]), dbus.Byte(Waterrower_byte_values[2]),
                     dbus.Byte(Waterrower_byte_values[3]), dbus.Byte(Waterrower_byte_values[4]), dbus.Byte(Waterrower_byte_values[5]),
                     dbus.Byte(Waterrower_byte_values[6]), dbus.Byte(Waterrower_byte_values[7]),
                     dbus.Byte(Waterrower_byte_values[8]), dbus.Byte(Waterrower_byte_values[9]),
                     dbus.Byte(Waterrower_byte_values[10]), dbus.Byte(Waterrower_byte_values[11]),dbus.Byte(Waterrower_byte_values[12]),dbus.Byte(Waterrower_byte_values[13]),dbus.Byte(Waterrower_byte_values[14]),
                     dbus.Byte(Waterrower_byte_values[15]),
                     dbus.Byte(Waterrower_byte_values[16]), dbus.Byte(Waterrower_byte_values[17]),
                     ]

            self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': value }, [])
            return self.notifying
        else:
            logger.warning("no data from s4 interface")
            pass

    def _update_Waterrower_cb_value(self):
        print('Update Waterrower Data')

        if not self.notifying:
            return

        GLib.timeout_add(200, self.Waterrower_cb)

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

# class HeartRate(Service):
#     HEART_RATE = '180D'
#
#     def __init__(self, bus, index):
#         Service.__init__(self, bus, index, self.HEART_RATE, True)
#         self.add_characteristic(HeartRateMeasurement(bus, 0, self))
#
# class HeartRateMeasurement(Characteristic):
#     HEART_RATE_MEASUREMENT = '2a37'
#
#     def __init__(self, bus, index, service):
#         Characteristic.__init__(
#             self, bus, index,
#             self.HEART_RATE_MEASUREMENT,
#             ['notify'],
#             service)
#         self.notifying = False
#
#
#
#     def StartNotify(self):
#         if self.notifying:
#             print('Already notifying, nothing to do')
#             return
#
#         self.notifying = True
#
#     def StopNotify(self):
#         if not self.notifying:
#             print('Not notifying, nothing to do')
#             return
#
#         self.notifying = False


class FTMPAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x77, 0x72],
        )
        self.add_service_uuid(DeviceInformation.DEVICE_INFORMATION_UUID)
        self.add_service_uuid(FTMservice.FITNESS_MACHINE_UUID)
        #self.add_service_uuid(HeartRate.HEART_RATE)

        self.add_local_name("S4 COMMS PI")
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


def main(out_q,ble_in_q): #out_q
    global mainloop
    global out_q_reset
    global ble_in_q_value
    out_q_reset = out_q
    ble_in_q_value = ble_in_q

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
    #app.add_service(HeartRate(bus,3))

    mainloop = MainLoop()

    agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput") # register the bluetooth agent with no input and output which should avoid asking for pairing 

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

#
# if __name__ == "__main__":
#     signal.signal(signal.SIGINT, sigint_handler)

