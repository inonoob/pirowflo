# TODO.md

## Bug Fixes

- [x] 13.04.2021 WaterRower Connect finding S4 Comm Pi but won't connect. Might be the fact that not all the Services and 
charateristics are implemented. Full Implementation of Service "Device Information" is required. 
  Change from 0x30 to 0x31. This is due to the HRM flag in the antdongle.py specification for Fitness equipment 
  see page 31 8.5.2.6 of Ant+ Fitness equipement device profile rev 5.0 


    WaterrowerValuesRaw = ble_in_q_value.pop()
  
- [on hold] Elapsed time is bugging. Bluetooth and ANT+ shows 0 or just 00.01 value. Needs to be investigate. 
May be thing about to create the elapse time in the code it self and not with the 
  waterrower data. e.g something like that 

    Time.time()



## needed Feature

- [ ] add smartrow as an interface for the Rowing data 
- [ ] add webserver to control the start/stop/restart of the script (Tornado)
- [ ] add support for heart rate monitors via Ant+ (pi is a client) use other channel of the 8 available from 
the ant node.
  
- [ ] FIT file export of a workout for Strava and Garmin-connect 
- [ ] Add Ant HRM data from the waterrower. So don't set it to zero take it directly from the memory map of the waterrower
- [ ] add HRM data from S4 waterrower to the Ble heart rate prfile as it is already available in the fitness equipment
profile

## DONE

- [x] add Ant+ capability to send data
- [x] python requirement.txt
- [x] Fix conversion from waterrower to Ant+ format (elasped time 1 = 0.25s. That needs to multiply the elapsed time 
  by 4 for ant+ in order to make complete seconds. )
  
- [x] add check for the which ANT+ dongle is available vendorid and productid e.g.
- [x] add user pi to the bluetooth group 
- [x] add argparser module in order to make choose e.g choose to have ant+ activate or heart rate monitor over 
ant+ ( not yet availalbe). This module would make it more flexible. 
    implemented but not tested yet.
    
- [x] Install.sh file which does all the installation stuff

- [x] if the deque is empty and is called it produces an error which kills the bluetooth thread. This error must
catch. Possible solution check size of the deque message and if it smaller than 1 then pass. Check in the def Waterrower_cb(self): 
  function for the size before. if smaller than 1 pass and wait next message.

