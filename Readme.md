# BLE and Ant+ for Waterrower

README is still work in progress 

This python script replaces the Waterrower com module. A Raspberry Pi is connected via usb with the Waterrower. The rowing
data are processed by the python script which is then send via bluetooth Low Energy Fitness equipment profile to the connected App. E.g Android
app Coxswain, Kinomap or Cityrow. 

- [x] Status = Done

Additionally, it is planned to have the processed data to be sent also via Ant+. This is an idea for Garmin watches especially 
the Fenix 6 series as the native rowing app can use thoes Data. The Ant+ profile used here is the Fitness Machine. 

- [ ] Status = Work in progress

even more, the script will be control via a build in webserver that can control the script to Start/stop 
and Restart it.

- [ ] Status = Pending

Last idea would be to track and export the workout to a FIT file which is then used for Garmin-connect or Strava. 

- [ ] Status = Pending

## Features and limitations

- Read Serial Waterrower Data to the Pi
- Send Waterower Data from the Pi over Bluetooth (Build-in or USB-dongle) 

## Planned Features 

- Send Waterrower Data from the Pi over Ant+ 
- Webserver to control script in order to start/stop/restart Bluetooth,Ant or Waterrower


## Parts of the code based on following Repos:

- [Link to repo](https://github.com/bfritscher/waterrower) base code used to get the Waterrower Data over USB Interface 
- [Link to repo](https://github.com/PunchThrough/espresso-ble) base code for the BLE GATT server and Advertiser example which
is self based on the Bluez Gatt server example
- [Link to repo](https://github.com/WouterJD/FortiusANT) base code for the Ant+ part used for this project

Thoses Repos have the base code which then has been rewritten to meet the requirements of this project. 

## Motivation

I wanted to have the ability to use the Android App Coxswain and also my Garmin smartwatch. Therefore, I though
why not connect the Waterrower via USB to a Raspberry pi and let the Raspberry pi being a BLE and Ant+ transmitter. 
And wouldn't be even better if it could be control for the Webbrowser. 

### BLE  
So I started looking for projects on github and found the MostTornBrain repo "Waterrower" [link](https://github.com/MostTornBrain/Waterrower)
But he had implemented as indoor-bike in order to use it with Zwift. He used the BLE gatt server and Advertiser from 
the bluez ble example. But I needed the BLE profile for rowing. 
So I digged into the not very well documented BLE documentation which is high level and on some points theroatical and 
not very partical. (Check for Developer section for more details)

### Ant+

## Requirements

### Hardware 

####Bill of Material(BOM)

| Item for Raspberry pi| 
|------|
| Raspberry Pi || 
| Micro SD card || 
| Mini USB to USB typ A ||  
| Bluetooth USB dongle 4.1 (LogiLink BT0015) || 
| Micro USB to Typ A || 
| 5V USB power supply 2A ||
| **for Ant+ addition** || 
| Ant+ dongle (avoid Cyclone) ||


| Item for Raspberry pi Zero W | 
|------|
| Raspberry Pi Zero W || 
| Micro SD card || 
| Mini USB to Micro USB || 
| 5V USB power supply 2A ||
| Total||
| **for Ant+ addition**  || 
| Ant+ dongle (avoid Cyclone) ||
| Micro USB to USB Hub || 

I would recommend buying the Raspberry pi in a kit where most of the parts are inclued 

### Software 

## Installation or Getting Started

Clone the repo from Github: 

    git clone https://github.com/inonoob/WaterrowerAntBle.git 
    
go into the folder: 

    cd WaterrowerAntBle 

Ensure that python above 3.6 is installed, if not then install it via apt-get 

    python3 --version 
    sudo apt-get install python3 python3-pip -y 

Ensure that Bluez version above 5.49 is installed, if not installed or older version then it is 
recommanded to compile it from source. Bluez version 5.50 is recommended. [link](https://scribles.net/updating-bluez-on-raspberry-pi-from-5-43-to-5-50/)
to tutorial in order to compile bluez from source on the Raspberry pi. 

    bluetoothd --version






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

TODO: might wanna thing about using the callback function as is would be helpfull to only react on callback and not
create concurent thread which could conflict by race condition problems 

Implemented. SO now A logger.py file is available 

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

If Reset send 
- Set reset to True  
- Set all values to 0 
If reset True 

If Reset send paddle still turning 
- Set reset to true 

##### bug coxswain 

Reminder to my self

Might wanna set the instantaneous pace to 65535 (0xff 0xff) if the Waterrower is at standstill. This is due to the fact
that the Com module sends 0xff 0xff as it stands still. In coxswain the speed is calc as follows: 

    if (fields.flag(3)) {
		setSpeed(500 * 100 / fields.get(Fields.UINT16)); // instantaneous pace
						
If instantaneous pace is 0 this results in the equation being divided by 0 which brakes the code. This results in the
code part to check reset has been performed not to be executed and then not working properly. 
Solution : 

either set during standstill the instantaneous pace to 65535 (0xff 0xff) or Coxswain fixes the code in order to be 
more robust against dividing by 0: 

    if (fields.flag(3)) {
        if (fields.get(Fields.UINT16 == 0 || (fields.get(Fields.UINT16 == 65536){ // check if instantaneous pace is zero or 65536 to avoid to divid by 0
            setSpeed(0);
        }else{
            setSpeed(500 * 100 / fields.get(Fields.UINT16)); // instantaneous pace
        }
    }

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

So as I only need Fitness Machine Service and Device Information Service, I quick check the available 
characteristic for each of those service. Check the FTMS pdf and also get the Bluetooth UUID overview (PDF): [Link](https://specificationrefs.bluetooth.com/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf)
to know which UUID is used for which Service and Characteristic. 

Start to create the custom classes for those service based on the main service class. e.g 

    class FTMservice(Service):
    FITNESS_MACHINE_UUID = '1826'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.FITNESS_MACHINE_UUID, True)
        ==> characteristic_0 of service FTMservice
        ==> characteristic_1 of service FTMservice
        ...

At that point I had 2 service create which are "Device Information" and "Fitness Machine Service". But those
services are still empty and don't have any characteristics defined, yet. For each of service a full load of
characteristics exists. In order to know which one is needed and also available, it is necessary to check
the FTMS again. As here every Characteristics of each service is defined. 

For this project only 4 Characteristics are needed. 

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



Fitness Machine Control Point

The response is made by replying with the following byte code (table 4.24)

0x80 reponse code field 
the seco

FMCP = Fitness Machine control point

|Service | Fitness Machine | uuid | 
| :--- | :---| :---|
| 0x80 Responce Code OP code FMCP| 0x00 (request control)| 0x01 (Success)
| 0x80 Responce Code OP code FMCP| 0x01 (request reset) | 0x01 (Succes)


##### Feeding the Characteristics with information

##### main function

The main script:
- Bus is initialised
- Advertiser class is initialised 
- App with Services are initialised
- init the main loop
- Start to register the Advertiser and start broadcasting 
- start the app with the services 
- GLib mainloop is started

### ANT+ 

Before adding anythin we have to add the ant+ dongle as ttyUSB0 module. In order to do that we must call the FTDI driver.
First check lsusb for vendorid and productid

    pi@raspberrypi:/dev $ lsusb
    Bus 001 Device 002: ID 0fcf:1008 Dynastream Innovations, Inc. ANTUSB2 Stick

We do this by creating a udev rule in /etc/udev/rules.d/99-ftdi.rules 

    ACTION=="add", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="1008", RUN+="/sbin/modprobe ftdi_sio" RUN+="/bin/sh -c 'echo 0fcf 1008 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'"



in order to make the Ant+ stick work under linux without root rights create a file in /etc/udev/rules.d/99-garmin.rules and add the following
this will ensure that the pyusb has acces to the ant+ stick as non-root. Also check if the $USER is part of the "dialout" group
Check in "/dev/" if the stick ist ttyUSB0 or ttyAMA0 which is on the raspberry pi zero

    SUBSYSTEM=="usb", ATTR{idVendor}=="0fcf", ATTR{idProduct}=="1008", MODE="666"


## Resources: 

### Converter e.g dec to hex 

Convert dec to hex and so on[link](https://www.binaryhexconverter.com/decimal-to-hex-converter)

### Waterrower Serial 

interface to Waterrower serial [link](https://github.com/bfritscher/waterrower/blob/master/waterrower/interface.py)

Water Rower S4 S5 USB Protocol Iss 1 04.pdf is the document specifying the USB specification.   


### DBUS

Dbus Tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-tutorial.html)

Python dbus Tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)

Python dbus types: [Link](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html#basic-types)

### BLE

BLE uart server [link](https://scribles.net/creating-ble-gatt-server-uart-service-on-raspberry-pi/)

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

common pages D00001198 

Most up to date ant+ lib [link](https://github.com/mch/python-ant)

Track heart rate Ant+ and Raspberry pi: [Link](https://johannesbader.ch/blog/track-your-heartrate-on-raspberry-pi-with-ant/)

ANT+ Virtual Power Meter: [Link](https://github.com/dhague/vpower)

Kettler Ant+ Support: [Link](https://github.com/joekearney/kettler-to-ant)

GoldenCheetah [link](https://github.com/GoldenCheetah/GoldenCheetah/blob/master/src/ANT/ANTMessage.cpp)

hacking ant [link](https://hackingantblog.wordpress.com/)

udev rules for ant+ stick [link](https://unix.stackexchange.com/questions/81754/how-to-match-a-ttyusbx-device-to-a-usb-serial-device))
udev rules for ant+ stick so it can be viewed as ttyUSB0 [link](https://unix.stackexchange.com/questions/67936/attaching-usb-serial-device-with-custom-pid-to-ttyusb0-on-embedded)
udev rules for more serial stuff [link](https://medium.com/@inegm/persistent-names-for-usb-serial-devices-in-linux-dev-ttyusbx-dev-custom-name-fd49b5db9af1)

### bash 

[link](https://ryanstutorials.net/bash-scripting-tutorial/bash-if-statements.php)

## License

     

MIT License

Copyright (c) 2021 Inonoob

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## to investigate:

https://forum.logicmachine.net/showthread.php?tid=1199