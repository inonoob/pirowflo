# TODO.md

version: 23.02.2021

## Bug Fixes

see github issues

## Possible Features

- [ ] Identify user by HRM device ID in order to pick correct user and password for Garmin Connect auto uploader
- [ ] AutoUpdate/manual function of PiRowFlo 
- [ ] Second BLE GATT server to passthrough SmartRow data to SmartRow App. Second BLE Server as Bluetooth Passthrough for SmartRow App #26
- [ ] Create Image of the project
- [ ] FIT file export of a workout for Strava and Garmin-connect. Use Python lib garmin-connect
- [ ] Auto disconnect from SmartRow if no activity is register after 5 min or more minutes to save batterie
- [ ] add support for heart rate monitors via Ant+ (pi is a client) use other channel of the 8 available from 
the ant node.
- [ ] add HRM data from S4 waterrower to the Ble heart rate prfile as it is already available in the fitness equipment
profile
- [ ] the Pi sees HRM signal on the S4 and sends it through on ANT+. 
  Or the Pi sees NO HRM signal on the S4 and tells the watch to get its own.
  
  
## DONE
- [x] 24.02.2021 Screensaver OLED in order to protect OLED display from burn-in effect. Screensaver for OLED display #27
- [x] 24.02.2021 Shutdown of Raspberry pi via Supervisor
- [x] 23.02.2021 Quit script gracefully in waterrowerthreads script 
- [x] 21.02.2021 Add screen to project
- [x] 12.02.2021 add webserver to control the start/stop/restart of the script (supervisor)
- [x] 01.02.2021 add Smartrow as an interface for the Rowing data 
- [x] 19.01.2021 WaterRower Connect finding S4 Comm Pi but won't connect. Might be the fact that not all the Services and 
  charateristics are implemented. Full Implementation of Service "Device Information" is required. 
  Change from 0x30 to 0x31. This is due to the HRM flag in the antdongle.py specification for Fitness equipment
  see page 31 8.5.2.6 of Ant+ Fitness equipment device profile rev 5.0
  
  
- [x] 10.01.2021 if the deque is empty and is called it produces an error which kills the bluetooth thread. This error must
catch. Possible solution check size of the deque message and if smaller than 1 then pass. Check in the def Waterrower_cb(self): 
function for the size before. if smaller than 1 pass and wait next message.
  

    WaterrowerValuesRaw = ble_in_q_value.pop()
  

- [x] 09.01.2021 add check for the which ANT+ dongle is available vendorid and productid e.g.  
- [x] 09.01.2021 Install.sh file which does all the installation stuff
- [x] 05.01.2021 add argparser module in order to make choose e.g choose to have ant+ activate or heart rate monitor over 
ant+ ( not yet availalbe). This module would make it more flexible.
- [x] 04.01.2021 Fix conversion from waterrower to Ant+ format (elasped time 1 = 0.25s. That needs to multiply the elapsed time 
  by 4 for ant+ in order to make complete seconds. )
- [x] 28.12.2020 python requirement.txt
- [x] XX.12.2020 add Ant+ capability to send data





    




