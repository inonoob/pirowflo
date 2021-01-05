# TODO.md

## Bug Fixes

- [ ] Elapsed time is bugging. Bluetooth and ANT+ shows 0 or just 00.01 value. Needs to be investigate. 
May be thing about to create the elapse time in the code it self and not with the 
  waterrower data. e.g something like that 
  

    Time.time()

### WaterrowerThreads.py 

- [ ] add argparser module in order to make choose e.g choose to have ant+ activate or heart rate monitor over 
ant+ ( not yet availalbe). This module would make it more flexible. 
 
### Install.sh 

- [ ] add check for the which ANT+ dongle is available vendorid and productid e.g.
- [ ] double check if pi user is part of the group "dialout" or the user won't have access to the bluetooth or 
ant+ dongle 
  

    "0fcf:1008 Dynastream Innovations, Inc. ANTUSB2 Stick"
this is needed in order to add it to udev 
as a rule. This is needed to load it via the FTDI serial driver. 
  
  
    ACTION=="add", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="1008", RUN+="/sbin/modprobe ftdi_sio" RUN+="/bin/sh -c 'echo 0fcf 1008 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'"



## needed Feature
- [ ] Fix conversion from waterrower to Ant+ format (elasped time 1 = 0.25s. That needs to multiply the elapsed time 
  by 4 for ant+ in order to make complete seconds. )
- [ ] add webserver to control the start/stop/restart of the script (Flask or web.py)
- [ ] Install.sh file which does all the installation stuff
- [ ] add support for heart rate monitors via Ant+ (pi is a client) use other channel of the 8 available from 
the ant node. 
  

## DONE
- [x] add Ant+ capabiltiy to send data
- [x] python requirement.txt

