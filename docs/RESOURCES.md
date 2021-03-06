# Resources

## Waterrower Serial
interface to Waterrower serial [link](https://github.com/bfritscher/waterrower/blob/master/waterrower/interface.py)

- links to the waterrowerInterface.py which is also used in this project. 

Waterrower interface [link](https://github.com/bfritscher/waterrower)

- Water Rower S4 S5 USB Protocol Iss 1 04.pdf is the document specifying the USB specification.   

## BLE
used for: 
- ble.py
- waterrowerble.py

Gatt-sdk client [link](https://github.com/getsenic/gatt-python) 

Gatt example client [link](https://github.com/Aloz1/iot-raspi/blob/master/gatt_manager.py)

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

Gatt clietn python [link](https://github.com/oscaracena/pygattlib#python-pip)

bluetoot name changer for raspberry pi [link](https://stackoverflow.com/questions/26299053/changing-raspberry-pi-bluetooth-device-name)

## DBUS
used for:
- ble.py
- waterrowerble.py 

Dbus Tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-tutorial.html)

Python dbus Tutorial: [Link](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)

Python dbus types: [Link](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html#basic-types)

## ANT+
used for: 
- antdongle.py
- antfe.py
- waterrowerant.py

common pages D00001198 

Most up to date ant+ lib [link](https://github.com/mch/python-ant)

Track heart rate Ant+ and Raspberry pi: [Link](https://johannesbader.ch/blog/track-your-heartrate-on-raspberry-pi-with-ant/)

ANT+ Virtual Power Meter: [Link](https://github.com/dhague/vpower)

Kettler Ant+ Support: [Link](https://github.com/joekearney/kettler-to-ant)

GoldenCheetah [link](https://github.com/GoldenCheetah/GoldenCheetah/blob/master/src/ANT/ANTMessage.cpp)

hacking ant [link](https://hackingantblog.wordpress.com/)

## bash
used for: 
- install.sh

Bash If statements [link](https://ryanstutorials.net/bash-scripting-tutorial/bash-if-statements.php)
udev rules for ant+ stick [link](https://unix.stackexchange.com/questions/81754/how-to-match-a-ttyusbx-device-to-a-usb-serial-device))
udev rules for ant+ stick so it can be viewed as ttyUSB0 [link](https://unix.stackexchange.com/questions/67936/attaching-usb-serial-device-with-custom-pid-to-ttyusb0-on-embedded)
udev rules for more serial stuff [link](https://medium.com/@inegm/persistent-names-for-usb-serial-devices-in-linux-dev-ttyusbx-dev-custom-name-fd49b5db9af1)

## Converter e.g dec to hex 

Convert dec to hex and so on[link](https://www.binaryhexconverter.com/decimal-to-hex-converter)


## Case for raspberry pi zero: 

Pi zero case which need to be change in oreder to fit the usbhub. [link](https://www.thingiverse.com/thing:4297526)
Pi zero case rev 2 [link](https://www.thingiverse.com/thing:4607660/files)

## Fixe bluetooth raspberry pi onboard 

https://github.com/pelwell/pi-bluetooth/blob/master/usr/bin/btuart 

$HCIATTACH /dev/serial1 bcm43xx 921600 noflow - $BDADDR

        sudo /usr/bin/hciattach /dev/serial1 bcm43xx 921600 noflow - b8:27:eb:10:10:10

## Raspberry pi Oled screen sh1106 Waveshare. 

Oled screen configratuion and display [link](https://luma-oled.readthedocs.io/en/latest/api-documentation.html)
Oled github 


## Raspberry pi TFT screen 

TFT screen configuration and display [link](https://github.com/juj/fbcp-ili9341)

## systemd stuff

https://www.howtogeek.com/687970/how-to-run-a-linux-program-at-startup-with-systemd/ 

Supervisor to run as normal user: 

https://drumcoder.co.uk/blog/2010/nov/24/running-supervisorctl-non-root/ 

## Create gifs from mp4 

ffmpeg \
  -i opengl-rotating-triangle.mp4 \
  -r 15 \
  -vf scale=512:-1 \
  -ss 00:00:03 -to 00:00:06 \
  opengl-rotating-triangle.gif

https://askubuntu.com/questions/648603/how-to-create-an-animated-gif-from-mp4-video-via-command-line 

