# TODO.md

## Bug Fixes

- [ ] Elapsed time is bugging. Bluetooth and ANT+ shows 0 or just 00.01 value. Needs to be investigate. 
May be thing about to create the elapse time in the code it self and not with the 
  waterrower data. e.g something like that 
  

    Time.time()

## needed Feature

- [ ] add webserver to control the start/stop/restart of the script (Tornado)
- [ ] add support for heart rate monitors via Ant+ (pi is a client) use other channel of the 8 available from 
the ant node.
  
- [ ] FIT file export of a workout for Strava and Garmin-connect 
  

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

