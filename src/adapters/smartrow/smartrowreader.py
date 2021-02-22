import gatt
import logging
import threading
from time import time

logger = logging.getLogger(__name__)

#This SDK requires you to create subclasses of gatt.DeviceManager and gatt.Device. The other two classes gatt.Service and gatt.Characteristic are not supposed to be subclassed.

#The SDK entry point is the DeviceManager class. Check the following example to dicover any Bluetooth Low Energy device nearby.


class SmartRow(gatt.Device):

    SERVICE_UUID_SMARTROW = "00001234-0000-1000-8000-00805f9b34fb"
    CHARACTERISTIC_UUID_ROWWRITE = "00001235-0000-1000-8000-00805f9b34fb"
    CHARACTERISTIC_UUID_ROWDATA = "00001236-0000-1000-8000-00805f9b34fb"

    def __init__(self, mac_address, manager):
        super().__init__(mac_address=mac_address, manager=manager)
        self._callbacks = set()
        self.lock = threading.Lock()
        self.is_connected = False

    def ready(self):
      with self.lock: #"Lock Acquired"
          return self.is_connected
      
    def connect_succeeded(self):
        super().connect_succeeded()
        logger.info("Connected to [{}]".format(self.mac_address))


    def connect_failed(self, error):
        super().connect_failed(error)
        logger.info("Connection failed [{}]: {}".format(self.mac_address, error))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        logger.info("Disconnected [{}]".format(self.mac_address))

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
        with self.lock: #"Lock Acquired"
            self.is_connected = True
        
    def characteristic_value_updated(self, characteristic, value):
        super().characteristic_value_updated(characteristic, value)
        self.buffer = value.decode()
        self.notify_callbacks(self.buffer)


    def characteristic_write_value(self, value):
        self.writing = value
        #print(value)
        self.chrstcRowWrite.write_value(value)

    def register_callback(self, cb):
        self._callbacks.add(cb)

    def remove_callback(self, cb):
        self._callbacks.remove(cb)

    def notify_callbacks(self, event):
        for cb in self._callbacks:
            cb(event)

class SmartRowManager(gatt.DeviceManager):
    def __init__(self,*args,**kwargs):
        gatt.DeviceManager.__init__(self, *args, **kwargs)
        self.lock = threading.Lock()
        self.discovered=False 

    def ready(self):
        with self.lock:
            return self.discovered
        
    def device_discovered(self, device):
        if device.alias() == "SmartRow":
            logging.info("found SmartRow")
            logging.info(device.mac_address)
            self.smartrowmac = device.mac_address
            self.stop()
            with self.lock: #"Lock Acquired"
                self.discovered=True


def connecttosmartrow():
    manager = SmartRowManager(adapter_name='hci0')
    logger.info("starting discovery")
    manager.start_discovery()  # from the DeviceManager class call the methode start_discorvery
    manager.run()
    while not manager.ready(): # hold the thread locked a checks if SmartRow has been found. Then gives other process 0.2 sec time to work
        time.sleep(0.2)
    logger.info("found SmartRow macaddress")
    macaddresssmartrower = manager.smartrowmac    
    return macaddresssmartrower


if __name__ == '__main__':

    manager = gatt.DeviceManager(adapter_name='hci1')
    device = SmartRow(mac_address="", manager=manager)
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
