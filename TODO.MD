# TODO.md

version: 14.01.2021

## Bug Fixes

see  

## Possible Features

## Possible Features

- [ ] add webserver to control the start/stop/restart of the script (Tornado)
- [ ] add support for heart rate monitors via Ant+ (pi is a client) use other channel of the 8 available from 
the ant node.
  
- [ ] FIT file export of a workout for Strava and Garmin-connect 
- [ ] Add Ant HRM data from the waterrower. So don't set it to zero take it directly from the memory map of the waterrower
- [ ] add HRM data from S4 waterrower to the Ble heart rate prfile as it is already available in the fitness equipment
profile
  
- [ ] the Pi sees HRM signal on the S4 and sends it through on ANT+. 
  Or the Pi sees NO HRM signal on the S4 and tells the watch to get its own.
  
## ON HOLD 

- [ ] Elapsed time is bugging. Bluetooth and ANT+ shows 0 or just 00.01 value. Needs to be investigate. 
May be thing about to create the elapse time in the code it self and not with the 
  waterrower data. e.g something like that 
  

    Time.time()


## DONE


- [x] 01.02.2021 add Smartrow as an interface for the Rowing data 
- [x] 19.01.2021 WaterRower Connect finding S4 Comm Pi but won't connect. Might be the fact that not all the Services and 
  charateristics are implemented. Full Implementation of Service "Device Information" is required. 
  Change from 0x30 to 0x31. This is due to the HRM flag in the antdongle.py specification for Fitness equipment
  see page 31 8.5.2.6 of Ant+ Fitness equipement device profile rev 5.0
  
  
- [x] 10.01.2021 if the deque is empty and is called it produces an error which kills the bluetooth thread. This error must
catch. Possible solution check size of the deque message and if it smaller than 1 then pass. Check in the def Waterrower_cb(self): 
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





    




