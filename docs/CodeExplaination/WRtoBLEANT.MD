Version 06.01.2021

# WRtoBLEANT.py 

## Global overview

the script invokes an instance of the class WaterrowerInterface in order to get a connection to 
the waterrower. Once this instance created it will start the communicating with the Waterrower. 
The script then invokes the class called DataLogger which is defined in this file. This class 
registers 3 call back function in the WaterrowerInterface instance. Those functions get triggered
if a so called "event" is register from the waterrower. It is then processed by those callback 
function. 
- one is responsible for the values coming from the Waterrower 
- one is responsible to check if the paddle of the waterrower is still turning 
- one is responsible to check if a reset as been requested 

The process data from the waterrower are sent and given to the data handlers which then are share 
across the different thread e.g. Bluetooth or ANT. This happens every 0.1s 

Beside the data processing the system is constantly checking if a reset has been trigger by someone
externaly. So if for example the bluetooth thread has filled the reset handler with the signal to
reset the waterrower, WRtoBLEANT will check it and perform the reset as requested. 

## Details 

The script start with the import of the needed modules and also with the WaterrowerInterface 

    import threading
    import time
    import datetime
    import logging
    import numpy
    
    import WaterrowerInterface

Then comes the logging part definition, which will write if needed into the logs.log file if 
requested in the code 

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler()
    filelogHandler = logging.FileHandler("logs.log")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logHandler.setFormatter(formatter)
    filelogHandler.setFormatter(formatter)
    logger.addHandler(filelogHandler)
    logger.addHandler(logHandler)

### Main

The main function is the Interface daemonized thread to communicate with the waterrower. 
The function is to init the WaterrowerInterface in order to start a communication with the waterrower 

    def main(in_q, ble_out_q,ant_out_q):
        S4 = WaterrowerInterface.Rower()
        S4.open()
        S4.reset_request()

Once done it initialized the DataLogger instance itself 

        WRtoBLEANT = DataLogger(S4) 

then comes the part with the main loop which keeps the thread alive. It checks every 0.1 seconds
if a request for reset has been triggered. This is done by checking the queue.queue data handler. 

        while True:
            if not in_q.empty():
                ResetRequest_ble = in_q.get()
                print(ResetRequest_ble)
                S4.reset_request()
            else:
                pass


still in this main loop after the reset request check, the function check according to the value
received from the waterrower in which state it is. 

- In "reset mode" Reset has been trigger waterrower is at standstill. all value are set to zero.
- In "Hiit or waiting mode" The waterrower is not in reset stat but the paddle is in standstill 
this result in all the instanteansoue value being set to zero equal what the S4 display shows.
  This is needed as the waterrower don't zero the value in memeory even if it shows zero on the
  s4 monitor. The last none zero value is store. This is why it must be set to 0 for those values
  
- In "rowing mode" normal workout, take the data from the waterrower and send them to the 
data handlers. 


        WRtoBLEANT.SendToBLE()
        WRtoBLEANT.SendToANT()

Then the data handlers for Bluetooth and Ant+ are 
field with new data. For those data handlers we use the "collections import deque". This has the 
advantage we are not limited to the (First in First out) problem. The script overwrites every 0.1s
those value. The Ant+ only grabs those data every 0.25 and Bluetooth is currently set to 0.5s. 
Here is a link to stockoverflow why: [link](https://stackoverflow.com/questions/29949697/multithreading-overwrite-old-value-in-queue)


        ble_out_q.append(WRtoBLEANT.BLEvalues)
        ant_out_q.append(WRtoBLEANT.ANTvalues) # here it is a class deque
        time.sleep(0.1)



### class DataLogger(object): 

we first start with the initializing of the different variable. e.g the Waterrower data for reset 
is set to 0 for all the needed values. e.g.

