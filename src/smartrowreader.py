import gatt
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
filelogHandler = logging.FileHandler("logs.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
filelogHandler.setFormatter(formatter)
logger.addHandler(filelogHandler)
logger.addHandler(logHandler)

#This SDK requires you to create subclasses of gatt.DeviceManager and gatt.Device. The other two classes gatt.Service and gatt.Characteristic are not supposed to be subclassed.

#The SDK entry point is the DeviceManager class. Check the following example to dicover any Bluetooth Low Energy device nearby.


class SmartRow(gatt.Device):

    SERVICE_UUID_SMARTROW = "00001234-0000-1000-8000-00805f9b34fb"
    CHARACTERISTIC_UUID_ROWWRITE = "00001235-0000-1000-8000-00805f9b34fb"
    CHARACTERISTIC_UUID_ROWDATA = "00001236-0000-1000-8000-00805f9b34fb"

    def __init__(self, mac_address, manager):
        super().__init__(mac_address=mac_address, manager=manager)
        self._callbacks = set()

    def connect_succeeded(self):
        super().connect_succeeded()
        logger.info("Connected to [{}]".format(self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        logger.info("Connection failed [{}]: {}".format(self.mac_address, error))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        logger.info("Disconnected [{}]".format(self.mac_address))

    # def characteristic_write_value_succeeded(self, characteristic):
    #     super().characteristic_write_value_succeeded()
    #     logger.debug('Successfully wrote to chrstc [{}]'.format(characteristic.uuid))
    #
    # def characteristic_write_value_failed(self, characteristic, error):
    #     super().characteristic_write_value_failed()
    #     logger.debug('Failed to wirte to chrstc [{}]: {}'.format(characteristic.uuid, error))
    #
    # def characteristic_enable_notifications_succeeded(self, characteristic):
    #     super().characteristic_enable_notifications_succeeded()
    #     logger.debug('Successfully enabled notifications for chrstc [{}]'.format(characteristic.uuid))
    #
    # def characteristic_enable_notifications_failed(self, characteristic, error):
    #     super().characteristic_enable_notifications_succeeded()
    #     logger.debug('Failed to enabled notifications for chrstc [{}]: {}'.format(characteristic.uuid, error))


    def find_service(self, uuid):
        for service in self.services:
            if service.uuid == uuid:
                return service

        return None

    def find_characteristic(self, service, uuid):
        for chrstc in service.characteristics:
            if chrstc.uuid == uuid:
                return chrstc

        return None

    def services_resolved(self):
        super().services_resolved()

        logger.info("Resolved services [{}]".format(self.mac_address))
        for service in self.services:
            logger.info("\t[{}] Service [{}]".format(self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                logger.info("\t\tCharacteristic [{}]".format(characteristic.uuid))

        self.serviceSmartRow = self.find_service(self.SERVICE_UUID_SMARTROW)
        self.chrstcRowData = self.find_characteristic(self.serviceSmartRow, self.CHARACTERISTIC_UUID_ROWDATA)
        self.chrstcRowData.enable_notifications()

        self.chrstcRowWrite = self.find_characteristic(self.serviceSmartRow, self.CHARACTERISTIC_UUID_ROWWRITE)

    def characteristic_value_updated(self, characteristic, value):
        super().characteristic_value_updated(characteristic, value)
        self.buffer = value.decode()
        #print(self.buffer)
        self.notify_callbacks(self.buffer)


    def characteristic_write_value(self, value):
        #logging.debug("[{}] Writing data to {} - {} ({})".format(self.logger_name, self.chrstcRowWrite, value, bytearray(value).hex()))
        self.writing = value
        print(value)
        self.chrstcRowWrite.write_value(value)

    def register_callback(self, cb):
        self._callbacks.add(cb)

    def remove_callback(self, cb):
        self._callbacks.remove(cb)

    def notify_callbacks(self, event):
        for cb in self._callbacks:
            cb(event)

#TODO: Add the device manager part in order to look for the smartrow and then connnect to it. The smartrow must be found via MAC address

class SmartRowManager(gatt.DeviceManager):
    def device_discovered(self, device):
        if device.alias() == "FAKE SmartRow":
            print("found Fakre rower")
            print(device.mac_address)
            self.smartrowmac = device.mac_address
            self.stop()


def connecttosmartrow():
    manager = SmartRowManager(adapter_name='hci0')
    manager.start_discovery()  # from the DeviceManager class call the methode start_discorvery
    manager.run()
    macaddresssmartrower = manager.smartrowmac
    return macaddresssmartrower


if __name__ == '__main__':

    # def hellotest(event):
    #     print("hello test {0}".format(event))

    manager = gatt.DeviceManager(adapter_name='hci1')

    device = SmartRow(mac_address="00:1A:7D:DA:71:04", manager=manager)
    #device.register_callback(hellotest)
    device.connect()

    manager.run()

    # manager = SmartRoweManager(adapter_name='hci0')
    # manager.start_discovery()
    # try:
    #     manager.run()
    # except KeyboardInterrupt:
    #     for device in manager.devices():
    #         if device.is_connected():
    #             device.disconnect()
    #     manager.stop()