# Version 27.01.2021

# smartrowrader.MD

## Global overview 

the smartrow reader uses the gatt library. This libary defines that in oreder
to used it, we should subclass 2 things: 

- gatt.device 
- gattt.DeviceManager 

from smartrowtobleant.py the function connectsmartrow is called: 

    def connecttosmartrow():
        manager = SmartRowManager(adapter_name='hci1')
        manager.start_discovery()  # from the DeviceManager class call the methode start_discorvery
        manager.run()
        macaddresssmartrower = manager.smartrowmac
        return macaddresssmartrower

this function will initialise the instance of the sub-classed 
gatt.DeviceManager. We give as an input the bluetooth dongle. 
This can be check in a terminal by using: 

    pi@raspberrypi:~ $ hcitool dev
    Devices:
	    hci0	XX:XX:XX:XX:XX

In order to make it search for the Smartrow, after initalizing 
the class, we need to call the function responsible for search
devices. 

    manager.start_discovery()

in order to have the search loop looking for a inifite amout of time
we also need to run the loop for it. This is done by calling: 

    manager.run()


the class it self does the following: 

    class SmartRowManager(gatt.DeviceManager):
        def device_discovered(self, device):
            if device.alias() == "SmartRow":
                logging.info("found SmartRow")
                logging.info(device.mac_address)
                self.smartrowmac = device.mac_address
                self.stop()

It takes as an input the bluetooth device (e.g. dongle) then 
it will try to search for all bluetooth devices which has the 
name SmartRow 

    if device.alias() == "SmartRow":

once found we stdout to the console vie the logging but we also
get the corresponding mac address by calling:

    self.smartrowmac = device.mac_address

the stop function is used in order to halt the loop for searching 
for new devices as it has been found. 

once found the function connecttisnartrow will return the 
macaddresse which will be used in the script "smartrowtobleant.py"
As in that script we use the mac address to connect to the
smartrow 

The class Smartrow is use to connect and interact with the bluetooth
device in our case the smartrow. 

first the services and charateriscitcs must be defined. Those
are the specific UUID used by bluetooth to identifie the services
and charaterisiscs. 

In our case the smartrow has: 

- 1 Service
  
    
    SERVICE_UUID_SMARTROW = "00001234-0000-1000-8000-00805f9b34fb"

- 2 Charateristics


    CHARACTERISTIC_UUID_ROWWRITE = "00001235-0000-1000-8000-00805f9b34fb"
    CHARACTERISTIC_UUID_ROWDATA = "00001236-0000-1000-8000-00805f9b34fb"

the first characteristic "1235" is a write command without response
this is use to send the reset command and also the needed heart beat
signal 

the second one is the notify charatersiisc "1236" which sends all 0.1s data. In 
this case the rowing data. 

then comes the init part which is sub-classed from the gatt.device were the init
the callback and also the variable is connected. Here we can also see 
that the function needs to know which mac addresse is should connect to 
but also the manager is which device (bluetooth dongle) should be use for this 
action

        def __init__(self, mac_address, manager):
        super().__init__(mac_address=mac_address, manager=manager)
        self._callbacks = set()
        self.is_connected = False

Then are the funcions: 

- def connect_succeeded(self):
- def connect_failed(self, error):
- def disconnect_succeeded(self):

those are called by bluez via dbus. As their names mention they are used to give 
a feedback about the status of the connection to the device. In our case the 
smartrow. 

Then we have the functions: 

- def find_service(self, uuid):
- def find_characteristic(self, service, uuid): 

those are used in the services_resolved part in order to create the services and
characerstic part. Let's assume from connection to a bluetooth device, there are a lot
of service and charatertisics. With those function it is possible to specific 
which one should be used. 

        def find_service(self, uuid):
        for service in self.services:
            if service.uuid == uuid:
                return service

        return None

The function will look in the list of available services for the one given and 
return the found service. The same applies to the find charateristisc 

the service_resolved part is where create and fill the different variable with 
the services and also with the charaterisics 

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


the first part enumerates all the possible service the device has which we 
are connected to. In our case the Smartrow. 

then we fill the variables with the needed services and charateres 
this is neede because we needed to build the following 

Service is after the app (bluetooth specification) the second layer. 
underneath the service are the chaerarterisc. So what is done: 

get the service: 

    self.serviceSmartRow = self.find_service(self.SERVICE_UUID_SMARTROW) 

get the needed charatersici and put them toghert as the charatei is the 3 layer 
in the bluetooth speifiicaion

app.service.charatereisic 

Here we create the notification charatereisic and also the write charatiere: 

    self.chrstcRowData = self.find_characteristic(self.serviceSmartRow, self.CHARACTERISTIC_UUID_ROWDATA)
    self.chrstcRowWrite = self.find_characteristic(self.serviceSmartRow, self.CHARACTERISTIC_UUID_ROWWRITE)

once done we also activate the fact that we want to have data now. So we tell the bluetooth device, the smartrow 
to enable notification and to send us the data. 

    self.chrstcRowData.enable_notifications()

Now comes the function what to do with the data which get recviecd. 

        def characteristic_value_updated(self, characteristic, value):
            super().characteristic_value_updated(characteristic, value)
            self.buffer = value.decode()
            self.notify_callbacks(self.buffer)

In our case, for each update of the data we want to have them store in the buffer variable but 
also the have them decoded on the spot. This means from hex to ascii values : 

    self.buffer = value.decode() 

then we hand those buffer with the decode value to the callbacks function which expect the new data. 

Beside getting data, we need to be able to write to the smartrow. This is done with the method: 

    def characteristic_write_value(self, value):
        self.writing = value
        print(value)
        self.chrstcRowWrite.write_value(value)

This method takes the value as input and then sends("write") to the write charatereisci ("1235") of the smartrow. 

Then last but not least, we have the part for the callback function. 

we have 3 methodes handeling the callback function: 

- the one which register a callback function to a set 
- the one which removes a callback functon from the set 
- the nofifier for those callback. Which brings the new data from the device. 







