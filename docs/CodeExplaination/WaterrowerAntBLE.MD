c

# WaterrowerAntBle project code 

In this document, it would like to explain how the complete project is build and the workflow of the project.
I recently learn that no one should be forced to read source code, and I thought it would be easier to have
something written in english instant of reading lots of code. For more detailed information about the scripts
and code explanations, please check the script.md files.

## Project composition

- Main script (WaterrowerThreads.py)
- Waterrower interface for the S4 Monitor (WaterrowerInterface.py)
- Waterrower data converter and dispatcher to serve the BLE and ANT+ threads (WRtoBLEANT.py)
- Bluetooth Gatt advertiser and Server (WaterrowerBle.py and Ble.py)
- Ant+ Server (WaterrowerAnt.py anfFE.py antDongle.py)

## The Logic behind the project: 

by starting "WaterrowerThready.py",beside the empty main loop, three threads are created. 

1. WRtoBLEANT.py which initialise the connection to the Waterrower via USB to serial connection 
2. The Bluetooth Gatt Server and advertiser is initialised and then started 
3. the Ant+ server is initialised and then started 

Once all threads are running, the following happens: 

The "WaterrowerInterface.py" has itself 2 threads with one sending all the request to read the different 
memory parts from the waterrower with a frequency of 0.025s (see Water Rower S4 S5 USB Protocol Iss 1 04.pdf).The second
thread gets all the responses from the waterrower and processing it. 

Each so called "event", an "event" is a feedback from the waterrower, the 3 register callback
function from "WRtoBLEANT.py" get called. Each event triggers a different result from those function. 
For example if the waterrower receives the command "reset" over BLE (is explained in detail in WaterrowerBle.py),
"WaterrowerInterface.py" will respond with the event "reset" and the callback function reset in "WRtoBLEANT.py"
will set all the information concerning rowing to 0. e.g Stroke rate = 0, Strokes = 0 and so on... 

The event with the needed data e.g stroke rate is received by the WaterrowerInterface.py and also send to a
callback function responsible to create a dictionary with the different data e.g stroke rate, stroke count,
distance, .... 

The filled dictionary with the data is checked against some condition.
Before serving those value to the handlers responsible to give it to the "WaterrowerBle.py" and "WaterrowerAnt.py"
Some conditions are check and depending on the result the dictionary with the data are different. 

1. Is the waterrower in reset mode. (blinking display S4 Monitor) if yes then set the raw data from 
   waterrower to 0 and ignore the data coming from the "waterrowerInterface.py". 
   The waterrower has the issue that even after a reset the data are not overwritten in memory.
    

2. check if waterrower is not in reset condition, and the paddle is not turning. If this is the case set
instantaneous data to 0. e.g instantaneous power, stroke rate, instantaneous pace, speed. But keep the 
   data e.g distance, keep counting elapsed time. Why is this important. As previously mentioned the waterrower
   don't reset those value if the rower is at standstill. Image the following you do HIIT training, you 
   stop because you just have performed your 30 sec all out. The S4 monitor goes to 0 the moment the paddle
   stops turning but here is the catch the waterrower memory keeps the last none 0 instantaneous value. 
   So that means you monitor shows 0 but your data shows the last full power value of your all out workout. 
   this is why "WRtoBLEANT.py" checks if the paddle is at standstill and we are in a workout. 
   

3. If none of the above is True, then take all the values from the "WaterrowerInterface.py" without touching
them. 
   
The dictionary with the data is then given to the deque data handlers for BLE and Ant+ (FILA: First In Last Out) 
This is done all every 0.1 seconds even if "WaterrowerBLE.py" and "WaterrowerANT.py" don't collets the data out 
of the handlers. They are constantly overwritten. The Data are oversampled as BLE only collets every 1 second
the data and Ant+ only 0.25 seconds.

"WRtoBLEANT.py" beside having the data ready for "WaterrowerBLE.py" and "WaterrowerANT.py" also checks for 
the "reset" command coming from "WaterrowerBLE.py". As this project has implemented the 
"FITNESS_MACHINE_CONTROL_POINT" characteristic of the bluetooth profile Fitness Machine Service. 
If "WaterrowerBLE.py" sends the command via queue handler to the "WRtoBLEANT.py". "WRtoBLEANT.py" call the 
reset function within the "WaterrowerInterface.py". 

Let's assume we want now to connect via bluetooth with the android app Coxswain. We go in the app and search
for the "S4 comm Pi" module. Once the connection is etablished the console will show 

    request control 

which means the app coxswain has sync with the Gatt server and it also triggers a reset of the waterrower. 
This is where we know the system is running and ready. At this point the "WaterrowerBLE.py" is already 
broadcasting data. This is done by clearing the handler which has been filed by the "WRtoBLEANT.py". 
This is done every second. (low frquency). But before the data can be send over bluetooth, the data needs
to be converter from integer numbers to bytes. Here we use within "WaterrowerBLE.py" some magic with 
bitshiffing.(for more details check the WaterrowerBle.MD)

On the ANT side, the "WaterrowerANT.py" is broadcasting from the very beginning. It start the so-called Node 
(ant+ usb dongle with the 8 channel, set the network key needed for ant+), then setups the use 
channel 0 and use the fitness equipment profile to set the correct frequency 2057MHz and all other needed
detail to meet the ant+ requirements to be recognized as rowing machine. 
The Ant+ part can't control the Waterrower. It just a sensor emitting data. 
The "WaterrowerANT.py" gets it data from the deque data handler which has been filled by "WRtoBLEANT.py" 
This is done every 0.25 which is also a ant+ specification. 

and that's how the project WaterrowerAntBle works 

EOF

   