Version 13.01.2021

# waterrowerant.py

this part is called as thread in order to start the Ant+ 
FE equipement part. It is called by the waterrowerthreads 
script as daemonize thread. it is responsible to start the ant
dongle, setup channels and send the messaged in a 0.25s intervall


## Global overview 

The function required to have the deque data handler as input of the function main
This is in order to get the data from waterbleant from the waterrower either the S4 or Smartrow 
. 

The scripts start by setting the EventCounter to 0 which is used to send the different 
message with a pattern. This eventCounter is feed into the antFE. And according to the 
current event number a specific message is send. This is done to be compliant with the ant+
fitness equipement profile. 

The antdongle is initialised by creating an instance of the class 
Antdongle. 

    Antdongle = ant.clsAntDongle()

Then the methode calibrate is called. This reset the usb ant+ dongle 
and request the capabilites and ant version and also important set the 
ant+ networkkey. Which is here the default public one. This setup the so 
called ant+ node 

then the ant+ channel is configured and setup. The ant+ protocol works
with differnt channels and patterns. For the Fitness equipement pattern 
the channel number and frequency is set. 

    Antdongle.Trainer_ChannelConfig() 

The ant+ node and defined frequency are then given as parameter to the 
antFE instance of the class antFE. This will give the antFE instance
the ability to access the ant+ node and send message over the defined 
ant+ channel. 

    Waterrower = fe.antFE(Antdongle)

Then the while loop is created. it checks if new data has been 
put by the wrtobleant.py function into the data handler deque. if not it pass
and retry in 0.25 sec as this is the message send cycle. 
If new data has been found to be in the deque data handler send from the
wrtobleant.py, it is remove from the deque and store into a variable. 

The eventCounter is check. If it is over 255 it is set to 0 and the message
array is cleared
    
    while True:
    if len(ant_in_q) != 0: #as long as the deque data from WR are not empty
        WaterrowerValuesRaw = ant_in_q.pop() # remove it from the deque and put in variable

        if EventCounter < 255:

        else:
            EventCounter = 0
            messages = []



if the eventCounter is small than 255, the eventcounter is set in the 
antFE instance in order to perform the check of which message needs to be 
send out next. We remember that ant+ defined a pattern to send data.

    Waterrower.EventCounter = EventCounter

Then the methode from the antFE instance is called to generate the message
which depeding on the eventcounter is choosen. 

    Waterrower.BroadcastTrainerDataMessage(WaterrowerValuesRaw)

This is then added to the message array. 

    messages.append(Waterrower.fedata)

if this message array is greater that 0 which means has data 
then trigger the methode from the antdongle instance to send the message. 

    Antdongle.Write(messages, True, False) 

once done add 1 to the eventcounter and pause for 0.25s which is 4Hz. 
Which is the message frequency defined by the ant+ fe profile. 

