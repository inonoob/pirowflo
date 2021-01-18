import gatt

class AnyDeviceManager(gatt.DeviceManager):
    def device_discovered(self, device):
        if device.alias() == "FAKE SmartRow":
            print("found Fakre rower")
            print(device.mac_address)
        #print("Discovered [%s] %s" % (device.mac_address, device.alias()))
        #print(device.alias())




manager = AnyDeviceManager(adapter_name='hci0') # AnyDeviceManage(gatt.DeviceManager(adapter_name='hci0')) subclassed devicemanager
manager.start_discovery() # from the DeviceManager class call the methode start_discorvery
manager.run()               # form the devicemanager class call the methode run to run in a loop