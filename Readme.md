# BLE and Ant+ for Waterrower

## Features and limitations
## Motivation

I wanted to have the ability to use the Android App Coswain and also my Garmin smartwatch. Therefore, I though
why not connect the Waterrower via USB to a raspberry pi and let the raspberry pi being a BLE and Ant+ transmeter. 

### BLE  
So I started looking for projects on github and found the MostTornBrain repo "Waterrower" [link](https://github.com/MostTornBrain/Waterrower)
But he had implemented as indoor-bike in order to use it with Zwift. He used the BLE gatt server and Advertisor from 
the bluez ble example. But I needed the BLE profile for rowing. 
So I digged into the not very well documented BLE documentation which is high level and on some points theroatical and 
not very partical. (Check for Developer section for more details)

### Ant+ 

## Requirements

### Hardware 

Bill of Material(BOM)

(table)

### Software 

## Installation or Getting Started

    git clone https://
    
## Possible improvements 
## For developers

### Hardware

It only works with a linux system which uses the Bluez Official Linux Bluetooth protocol stack. Therefore, a raspberry 
pi is perfect for this project. 

### Software

When you install a fresh Raspbian on a raspberry pi and want to use the script you first must add the user pi to the
group bluetooth. Or your will have an error acces denied. 

Tip: if you see on the nFR app when try to read or write and it say 0x03 no write to write then
you have error in you python code !!!

DO NOT UPDATE after bluez 5.50 because then you will have 2 Device Information 0x180A and Coxswain will check the first
won't see the Software revision string and won't perform the reset! If you do you will see 2 Device Information with 
the first havoing PnP up thing "device information pnp device" !!!

In order to get this working: [link](https://git.kernel.org/pub/scm/bluetooth/bluez.git/commit/?id=d5e07945c4aa36a83addc3c269f55c720c28afdb)

remove the code part from the source and compile the source. By doing this you repair the issue. As it is not documented how to remove it 
via the main.conf file in etc. 

for the exchange between the threads, I choose to use the deque in order to pass the value dict from the waterrower listern to the ble module 
for the reset I used the queue module. I might switch to have a uniq system [link](https://stackoverflow.com/questions/29949697/multithreading-overwrite-old-value-in-queue)

### the script itself

The project consists of 3 python scripts and 1 custom library 

- WaterrowerThreads.py
- WaterrowerInterface.py
- WaterrowerBle.py with the library ble.py

#### WaterrowerThread 

This is the main script which is called. It starts 2 threads which are the WaterrowerInterface and WaterrowerBle
In order to pass the "reset command" and also the "waterrower S4 values", the library queue and deque. 
 - The "reset" command coming from the WaterrowerBle thread is store in the queue. 
 - The waterrower dictionary with the values coming from the WaterrowerInterface uses the deque module
 in order to only use the newest value. 
 
#### WaterrowerInterface

This script when start does the following: 

- Start the main thread 
- init the class Rower 
    - the init class Rower will start 3 daemon threads "start_requesting", "start_capturing", "event_BLE". Those 
    threads will run even no connection is available to the waterrower. They will just idle as long as 
    the main thread is running. 
- next the connection to the Waterrower is established, the script looks automatically for
"/dev/ttyACM0". If not fount the script will retry until a connection is found 
- Request a reset of the rower in order to have a clean start and have the waterrower ready 
- Start the while True loop. 
- check every 0.1 seconds if a reset request have been made via bluetooth by checking the queue.
also populate the deque variable with the latest value from the waterrower. This will then be used
by the WaterrowerBle script to send it over bluetooth Low Energy. 

#### WaterrowerBle

##### Setting up BLE part 

This script has 2 main function: 

- create the GATT server with the FTMP (Fitness Maschine Profile) in this case the rowing one
- create the Advertiser for the GATT server 

This script is based of the BLE expresso machine example from punchthrough: 
[Link to repo](https://github.com/PunchThrough/espresso-ble), [Link to blog](https://punchthrough.com/

Every GATT server has the following: 

- APP
    - Service_0 
        - Characteristic_0
            - Description_0 
        - Characteristic_1
        - Characteristic_2
    - Service_1
        - Characteristic_0 
        - Characteristic_1
            - Description_1
        - Characteristic_2
    - ....
    
Then once a Gatt server build you advertise the service available 
- Advertiser: 
    - App
        - Service_0
        - Service_1 
        - ....

In order to make it work we are going to talk from the python script via dbus with bluez which is the Linux Bluetooth protocol stack
I won't go to much into the details of DBUS. But is like a network between programs which expose api in order 
talk to the different programs. For more details check this DBUS tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-tutorial.html)
Bluez gives in the source code file an example of a gatt and advertiser in python. 

In order to customise it for our needs, we need to create customized classes which bases on the main gatt
and advertiser classes. 

Before me define our customized classes we need to check the bluetooth specification. We wanna build a 
Fitness equipment service. So let's check what UUID is available and also how is the behavior defined.
[Link](https://www.bluetooth.com/specifications/gatt/). The needed documents are FTMP for profile
and FTMS for service. 

From the available information the following service are available (FTMP pdf): 

|Service | Fitness Machine | uuid | 
| :--- | :---| :---|
|Fitness Machine Service | Mandatory | 1826
| User Data Service| Optional | ----
| Device Information Service | Optional | 180A

So as I only need Fitness Machine Service and Device Information Service, I quick check the avaiable 
characterisitc for each of those service. Check the FTMS pdf and also get the Bluetooth UUID overview (PDF): [Link](https://specificationrefs.bluetooth.com/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf)
to know which UUID is used for which Service and Characterstic. 

Start to create the custom classes for those service based on the main service class. e.g 

    class FTMservice(Service):
    FITNESS_MACHINE_UUID = '1826'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.FITNESS_MACHINE_UUID, True)
        ==> characteristic_0 of service FTMservice
        ==> characteristic_1 of service FTMservice
        ...

At that point I had 2 service create which are "Device Information" and "Fitness Machine Service". But those
services are still empty and don't have any charateristics defined, yet. For each of service a full load of
charaterisitcs exists. In order to know which one is needed and also available, it is necceccary to check
the FTMS again. As here every Charaterisitcs of each service is defined. 

For this project only 4 Charaterisitcs are needed. 

 - FTMservice
    - Fitness Machine Feature (2acc): Use to define the machine abilities which is read by the client
    - Rowing Data (2ad1): the rowing profile and the corresponding data which is notified to the client without feedback
    - Fitness Machine Control Point (2ad9): is used to get control over the Rower and to initate a reset by writing
    to the server with a feedback from the server if it worked.
- Device Information
    - Software version string (2a29): this can be read by the client 
    
to define a custom charateristic, a class with needed information is created and sub-classed from the main
charaterisitc class: 

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
        self.value = dbus.Array(self.ManuName) 
    
This Service and corresponding charateristics are used for the project as the consumer of the information
in this case the Coxswain android app don't need more information. 

Once all the Service and Charateristics have been defined. It is time to add those services to the advertiser
    
    class FTMPAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x77, 0x72],   # [W, R] for WaterRower but it is not official from Bluetooth
        )
        self.add_service_uuid(DeviceInformation.DEVICE_INFORMATION_UUID)
        self.add_service_uuid(FTMservice.FITNESS_MACHINE_UUID)

        self.add_local_name("XXXXXX") #  The name which the Advertiser should display the GATT server
        self.include_tx_power = True # if the transmission power should be sent (dB)

##### Feeding the Charaterisitcs whith information

##### main function

The main script:
- Bus is initialised
- Advertiser class is initialised 
- App with Services are initialised
- init the main loop
- Start to register the Advertiser and start broadcasting 
- start the app with the services 
- GLib mainloop is started


## Resources: 

### Waterrower Serial 

interface to Waterrower serial [link](https://github.com/bfritscher/waterrower/blob/master/waterrower/interface.py)


### DBUS

Dbus Tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-tutorial.html)

Python dbus Tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)

Python dbus types: [Link](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html#basic-types)

### BLE

BLE waterrower cycling profile: [link to waterrower BLE cycling](https://github.com/MostTornBrain/Waterrower)

BLE erg cycling with rs232 + ble [link](https://github.com/weinzmi/ergoFACE)

use rs232.py as loop with global available variable + thrading ble and rs232 + ant+ 

BLE example [link](https://scribles.net/creating-ibeacon-using-bluez-example-code-on-raspberry-pi/#Step01)

BLE expresso machine example from punchthrough: 
[Link to repo](https://github.com/PunchThrough/espresso-ble), [Link to blog](https://punchthrough.com/creating-a-ble-peripheral-with-bluez/)

Bluez API overview: [link to Bluez gatt-api](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/gatt-api.txt), [Link](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc)

BLE Server exposing Treadmill Data Characteristics and Control Points. This is written for an Arduino ESP-32.: [Link](https://github.com/changer65535/hangermill)

BLE Gatt description: [link](http://software-dl.ti.com/lprf/sdg-latest/html/ble-stack-3.x/gatt.html)

BLE Gatt server example: [link](https://scribles.net/running-ble-gatt-server-example-on-raspbian-stretch/)

Bluetooth format types: [Link](https://www.bluetooth.com/specifications/assigned-numbers/format-types/)

Bluetooth UUID overview (PDF): [Link](https://specificationrefs.bluetooth.com/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf)

Bluetooth GATT specifications: [Link](https://www.bluetooth.com/specifications/gatt/)

Android app nRF Connect for Mobile: [Link](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp&hl=en_US&gl=US)

BLE gatt server micropython [link](https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_advertising.py)

### ANT+ 

Track heart rate Ant+ and Raspberry pi: [Link](https://johannesbader.ch/blog/track-your-heartrate-on-raspberry-pi-with-ant/)

ANT+ Virtual Power Meter: [Link](https://github.com/dhague/vpower)

Kettler Ant+ Support: [Link](https://github.com/joekearney/kettler-to-ant)

GoldenCheetah [link](https://github.com/GoldenCheetah/GoldenCheetah/blob/master/src/ANT/ANTMessage.cpp)

hacking ant [link](https://hackingantblog.wordpress.com/)

## License

## to investigate:

https://forum.logicmachine.net/showthread.php?tid=1199