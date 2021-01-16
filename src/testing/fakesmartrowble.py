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


class SmartRow(Service):
    SMART_ROW_SERVICE_UUID = '1234'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.SMART_ROW_SERVICE_UUID, True)
        self.add_characteristic(WriteToSmartRow(bus,0,self))
        self.add_characteristic(SmartRowData(bus, 1, self))

class WriteToSmartRow(Characteristic):

    WRITE_TO_SMARTROW_UUID = '1235'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.WRITE_TO_SMARTROW_UUID,
            ['write-without-response'],
            service)
        self.value = 0

    def WriteValue(self, value, options):
        self.value = value
        logger.info(self.value)

class SmartRowData(Characteristic):
    SMARTROW_DATA_UUID = '1236'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.SMARTROW_DATA_UUID,
            ['notify','read'],
            service)
        self.notifying = False
        self.iter = 0

    def Waterrower_cb(self):
        value = dbus.Byte(0)
        if ble_in_q_value:
            Smartrowfakedata = ble_in_q_value.pop()
            #value = [0x22, 0x21]
            if len(Smartrowfakedata) == 17:

               value = [dbus.Byte(Smartrowfakedata[0]), dbus.Byte(Smartrowfakedata[1]),
                         dbus.Byte(Smartrowfakedata [2]), dbus.Byte(Smartrowfakedata [3]),
                         dbus.Byte(Smartrowfakedata [4]), dbus.Byte(Smartrowfakedata [5]),
                         dbus.Byte(Smartrowfakedata [6]), dbus.Byte(Smartrowfakedata [7]),
                         dbus.Byte(Smartrowfakedata [8]), dbus.Byte(Smartrowfakedata [9]),
                         dbus.Byte(Smartrowfakedata [10]), dbus.Byte(Smartrowfakedata [11]),
                         dbus.Byte(Smartrowfakedata [12]), dbus.Byte(Smartrowfakedata [13]),
                         dbus.Byte(Smartrowfakedata [14]), dbus.Byte(Smartrowfakedata [15]),
                         dbus.Byte(Smartrowfakedata [16]),
                         ]
            elif len(ble_in_q_value) == 20:

                value = [dbus.Byte(Smartrowfakedata [0]), dbus.Byte(Smartrowfakedata [1]),
                         dbus.Byte(Smartrowfakedata [2]), dbus.Byte(Smartrowfakedata [3]),
                         dbus.Byte(Smartrowfakedata [4]), dbus.Byte(Smartrowfakedata [5]),
                         dbus.Byte(Smartrowfakedata [6]), dbus.Byte(Smartrowfakedata [7]),
                         dbus.Byte(Smartrowfakedata [8]), dbus.Byte(Smartrowfakedata [9]),
                         dbus.Byte(Smartrowfakedata [10]), dbus.Byte(Smartrowfakedata [11]),
                         dbus.Byte(Smartrowfakedata [12]), dbus.Byte(Smartrowfakedata [13]),
                         dbus.Byte(Smartrowfakedata [14]), dbus.Byte(Smartrowfakedata [15]),
                         dbus.Byte(Smartrowfakedata [16]), dbus.Byte(Smartrowfakedata [17]),
                         dbus.Byte(Smartrowfakedata [18]), dbus.Byte(Smartrowfakedata[19]),
                         ]

            self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': value }, [])
            return self.notifying
        else:
            logger.warning("no data from s4 interface")
            pass

    def _update_Waterrower_cb_value(self):
        print('Update Smartrow Data')

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

class SmartRowAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x77, 0x72],
        )
        self.add_service_uuid(SmartRow.SMART_ROW_SERVICE_UUID)
        self.add_local_name("FAKE SmartRow")
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

    advertisement = SmartRowAdvertisement(bus, 0)
    obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

    agent = Agent(bus, AGENT_PATH)

    app = Application(bus)
    app.add_service(SmartRow(bus, 0))


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

#
# if __name__ == "__main__":
#     signal.signal(signal.SIGINT, sigint_handler)

