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

Tip: if you see on the nFR app when try to read or write and it say 0x03 no write to write then
you have error in you python code !!!

## Resources: 

### DBUS

Dbus Tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-tutorial.html)

Python dbus Tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)

Python dbus types: [Link](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html#basic-types)

### BLE

BLE waterrower cycling profile: [link to waterrower BLE cycling](https://github.com/MostTornBrain/Waterrower)

BLE expresso machine example from punchthrough: 
[Link to repo](https://github.com/PunchThrough/espresso-ble), [Link to blog](https://punchthrough.com/creating-a-ble-peripheral-with-bluez/)

Bluez API overview: [link to Bluez gatt-api](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/gatt-api.txt), [Link](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc)

BLE Server exposing Treadmill Data Characteristics and Control Points. This is written for an Arduino ESP-32.: [Link](https://github.com/changer65535/hangermill)

BLE Gatt description: [link](http://software-dl.ti.com/lprf/sdg-latest/html/ble-stack-3.x/gatt.html)

Bluetooth format types: [Link](https://www.bluetooth.com/specifications/assigned-numbers/format-types/)

Bluetooth UUID overview (PDF): [Link](https://specificationrefs.bluetooth.com/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf)

Bluetooth GATT specifications: [Link](https://www.bluetooth.com/specifications/gatt/)

Android app nRF Connect for Mobile: [Link](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp&hl=en_US&gl=US)

### ANT+ 

Track heart rate Ant+ and Raspberry pi: [Link](https://johannesbader.ch/blog/track-your-heartrate-on-raspberry-pi-with-ant/)

ANT+ Virtual Power Meter: [Link](https://github.com/dhague/vpower)

Kettler Ant+ Support: [Link](https://github.com/joekearney/kettler-to-ant)

## License