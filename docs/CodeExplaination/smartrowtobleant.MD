Version 27.01.2021

# smartrowtobleant

## Global overview 

this script is responsible to etablish a connection to the smartrow 
register the callback function for the incoming data, fill the data handlers
with the data in order to get process by the GATT ble Server and ANT+. 
Addtionaly it check if an reset has been requested which is then proceed and 
send to the smartrow. 

the main function is also the function which is started from the 
waterrowerthreads as a deamon. 

    
    def main(in_q, ble_out_q,ant_out_q):
        macaddresssmartrower = smartrowreader.connecttosmartrow()

        manager = gatt.DeviceManager(adapter_name='hci1')
        smartrow = smartrowreader.SmartRow(mac_address=macaddresssmartrower, manager=manager)
        SRtoBLEANT = DataLogger(smartrow)
        #sleep(10)
    
        #try:
        BC = threading.Thread(target=connectSR, args=(manager,smartrow))
        BC.daemon = True
        BC.start()
    
        logger.info("SmartRow Ready and sending data to BLE and ANT Thread")
    
        sleep(5)
    
        HB = threading.Thread(target=heartbeat, args=([smartrow]))
        HB.daemon = True
        HB.start()
    
        reset(smartrow)
        sleep(1)
    
        while True:
            if not in_q.empty():
                ResetRequest_ble = in_q.get()
                print(ResetRequest_ble)
                reset(smartrow)
            else:
                pass
            ble_out_q.append(SRtoBLEANT.WRValues)
            ant_out_q.append(SRtoBLEANT.WRValues)

let's start the the main function takes as input queue in order to 
exchange values accroes threads. 

- in_q used for the reset request 
- ble_out_q used to feed the ble gatt server script 
- ant_out_q used to feed the ant+

we first start by calling the function from smartrowreader.py to retrieve
the mac address of teh smartrow. This is stored in a variable. We needed to
ensure that the smartrow is blink blue so that the script can find the 
smartrow

    macaddresssmartrower = smartrowreader.connecttosmartrow()

then we initilize the gatt.DeviceManager with the bluetooth dongle we wanna 
use. In that case "hc1"

        manager = gatt.DeviceManager(adapter_name='hci1')

once defined, we create th smartrow instance to create the bluetooth app with 
the services and charatereicis. The input here are the mac address and 
also which bluetooth dongle to use. Remember the manager is the bluetooth device

    smartrow = smartrowreader.SmartRow(mac_address=macaddresssmartrower, manager=manager)

then we create the instance of the class datalogger to register the callback
and also have access to the reset and heartbeat methodes. 

    SRtoBLEANT = DataLogger(smartrow) 

Now we can iniate a connection to the smartrow. We will get a connection. 
We start the connection procedure in a seperate thread as this is 
a infinit loop to keep the connection up. We daeonize that thread,
so in order to kill it if the main thread is stopped. 

    BC = threading.Thread(target=connectSR, args=(manager,smartrow))
    BC.daemon = True
    BC.start() 

the function called here is: 

    def connectSR(manager,smartrow):
        smartrow.connect()
        manager.run()

it is just the connect function and to run it in an infinit loop as 
defined by the gatt library 

We put an extra 5 second of sleep in order to give it time to perform 
all the handshakes and to stabilise the connection: 

    sleep(5)

After a connection has been etablisedh with the smartrow, the smartrow 
still expect to have some more. The bluetooth connection is present but 
the smartrow itself need to get the so called heart beat. If it doesn't get it 
the Smartrow will terminate the bluetooth connection after 1 minute. 

The heartbeat function is charatere $ in ascii which needs to be send every
seconded via the write charaterieics. In order to do so we define a function
and also put it in his own thread: 

    HB = threading.Thread(target=heartbeat, args=([smartrow]))
    HB.daemon = True
    HB.start()

this thread call the function: 

    def heartbeat(sr):
    while True:
        sr.characteristic_write_value(struct.pack("<b", 36))
        sleep(1)

as input it takes the smartrow instance which is the connection to the 
smartrow with the defined service and charatereis. We use the write charateris
to the smartrow to send the $ heartbeat. In hex it is the number 36. 
And this char is end every second. If the smartrow get that char, it
will stop to blink and will be ready. At that point it already should
start sending data to the pi. 

Then we send the reset command to the smartrow to have a fresh 
start on the unit. That is done with the function: 

    def reset(smartrow):
        smartrow.characteristic_write_value(struct.pack("<b", 13))
        sleep(0.002)
        smartrow.characteristic_write_value(struct.pack("<b", 86))
        sleep(0.002)
        smartrow.characteristic_write_value(struct.pack("<b", 64))
        sleep(0.002)
        smartrow.characteristic_write_value(struct.pack("<b", 13))

The reset of the smartrow is to send 4 ascii char which are \r V @ \r. 
a little delay is insert in order to give the smartrow some time to 
process the chars. 

after reseting the smartrow, the while true loop start: 

    while True:
        if not in_q.empty():
            ResetRequest_ble = in_q.get()
            print(ResetRequest_ble)
            reset(smartrow)
        else:
            pass
        ble_out_q.append(SRtoBLEANT.WRValues)
        ant_out_q.append(SRtoBLEANT.WRValues)

This does 2 major things: 

- Check if a reset has been requested via the data handler in_q 
- fill the data handlers for the bluetooth GATT server and ANT+ 

It does this by getting the latest data from the instance of dataloger class
This is where the interperation of the comming smartrow data are done 
and this is also where we have defined the callback function to be used. 


