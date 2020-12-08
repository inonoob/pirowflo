##

code transfered from waterrower git https://github.com/MostTornBrain/Waterrower
to https://github.com/PunchThrough/espresso-ble punchtrhough code

## Resources: 

How to BLE Gatt server with D-bus and Bluez

https://punchthrough.com/creating-a-ble-peripheral-with-bluez/ 


http://software-dl.ti.com/lprf/sdg-latest/html/ble-stack-3.x/gatt.html


https://github.com/changer65535/hangermill

https://github.com/an-erd/ble_beacon


https://www.bluetooth.com/specifications/assigned-numbers/format-types/

glib is 


Bluez is a kernel module for bluetooth 

Bluetooth api dbus 
https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc

in order to talk from the python script to the bluetooth api dbus is used

dbus is a system for interporcess communication. Which means that a python script can talk to the bluetooth bluez kernel
module via the dbus system. 

The dbus system has 

if you see on the nFR app when try to read or write and it say 0x03 no write to write then
you have error in you python code !!!