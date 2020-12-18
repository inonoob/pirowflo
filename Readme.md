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