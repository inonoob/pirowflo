# -*- coding: utf-8 -*-
import threading
import logging
import time
import serial
import serial.tools.list_ports
import datetime
from queue import Queue

MEMORY_MAP = {'055': {'type': 'total_distance_m', 'size': 'double', 'base': 16},
              '140': {'type': 'total_strokes', 'size': 'double', 'base': 16},
              '088': {'type': 'watts', 'size': 'double', 'base': 16},
              '08A': {'type': 'total_kcal', 'size': 'triple', 'base': 16},
              '14A': {'type': 'avg_distance_cmps', 'size': 'double', 'base': 16},
              '148': {'type': 'total_speed_cmps', 'size': 'double', 'base': 16},
              '1E0': {'type': 'display_sec_dec', 'size': 'single', 'base': 10},
              '1E1': {'type': 'display_sec', 'size': 'single', 'base': 10},
              '1E2': {'type': 'display_min', 'size': 'single', 'base': 10},
              '1E3': {'type': 'display_hr', 'size': 'single', 'base': 10},
              # from zone math
              '1A0': {'type': 'heart_rate', 'size': 'double', 'base': 16},
              '1A6': {'type': '500mps', 'size': 'double', 'base': 16},
              '1A9': {'type': 'stroke_rate', 'size': 'single', 'base': 16},
              # explore
              '142': {'type': 'avg_time_stroke_whole', 'size': 'single', 'base': 16},
              '143': {'type': 'avg_time_stroke_pull', 'size': 'single', 'base': 16},
              #other
              '0A9': {'type': 'tank_volume', 'size': 'single', 'base': 16, 'not_in_loop': True},
             }



# ACH values = Ascii coded hexadecimal
# REQUEST sent from PC to device
# RESPONSE sent from device to PC

USB_REQUEST = "USB"                # Application starting communication’s
WR_RESPONSE = "_WR_"               # Hardware Type, Accept USB start sending packets
EXIT_REQUEST = "EXIT"              # Application is exiting, stop sending packets
OK_RESPONSE = "OK"                 # Packet Accepted
ERROR_RESPONSE = "ERROR"           # Unknown packet
PING_RESPONSE = "PING"             # Ping
RESET_REQUEST = "RESET"            # Request the rowing computer to reset, disable interactive mode
MODEL_INFORMATION_REQUEST = "IV?"  # Request Model Information
MODEL_INFORMATION_RESPONSE = "IV"  # Current model information IV+Model+Version High+Version Low
READ_MEMORY_REQUEST = "IR"         # Read a memory location IR+(S=Single,D=Double,T=Triple) + XXX
READ_MEMORY_RESPONSE = "ID"        # Value from a memory location ID +(type) + Y3 Y2 Y1
STROKE_START_RESPONSE = "SS"       # Start of stroke
STROKE_END_RESPONSE = "SE"         # End of stroke
PULSE_COUNT_RESPONSE = "P"         # Pulse Count XX in the last 25mS, ACH value

SIZE_MAP = {'single': 'IRS',
            'double': 'IRD',
            'triple': 'IRT',}

SIZE_PARSE_MAP = {'single': lambda cmd: cmd[6:8],
                  'double': lambda cmd: cmd[6:10],
                  'triple': lambda cmd: cmd[6:12]}



def ask_for_port():
    print("Choose a port to use:")
    ports = serial.tools.list_ports.comports()
    for (i, (path, name, _)) in enumerate(ports):
        print("%s. %s - %s" % (i, path, name))
        if "WR" in name:
            print("auto-chosen: %s" % path)
            return path
    result = input()
    return ports[int(result)][0]

def find_port():
    ports = serial.tools.list_ports.comports()
    for (i, (path, name, _)) in enumerate(ports):
        print(path,name)
        if "WR" in name:
            print("port found: %s" % path)
            return path

    print("port not found retrying in 5s")
    time.sleep(5)
    return find_port()

# Build daemon is used to create the threading object
def build_daemon(target):
    t = threading.Thread(target=target)
    t.daemon = True # set this thread as background thread. It will stop as soon as the main thread stop or main function
    return t


# build event create a dict with depeding on the kind of responce from the waterrower create the dict with the data. Each dict has at the end a timestamp
def build_event(type, value=None, raw=None):
    return {"type": type,
            "value": value,
            "raw": raw,
            "at": int(round(time.time() * 1000))}

# this function is used to give back the thread and also the feedback if it is alive
def is_live_thread(t):
    return t and t.is_alive()

# This function takes the the 3rd up to the 6th char which is the MEMORY_MAP location eg "08A" depeding on size of the result single, double or triple, take the needed value
def read_reply(cmd):
    address = cmd[3:6]
    memory = MEMORY_MAP.get(address)
    if memory:
        size = memory['size']
        value_fn = SIZE_PARSE_MAP.get(size, lambda cmd: None) # define strip function depeding on the requested value from the waterrower
        value = value_fn(cmd) # Apply function to strip and extract only needed value e.g "IDD0A8015\r\n" this will extract 015
        if value is None: # if the value couldn't find if it was an IDS or IDD or IDT the waterrower responce then print error size unknown
            logging.error('unknown size: %s', size)
        else:
            return build_event(memory['type'], int(value, base=memory['base']), cmd) # create a dict with the input
            # what type it is e.g "Watt" convert byte to int with the correct base and the command itself
    else:
        logging.error('cannot read reply for %s', cmd) # if the response from the waterrower has an invalid memory addres then respond error with the
        # recieved command from the Waterrower

# Depending on the response from the waterrower after a command has been send, check watt has been respond and choose a case
#
def event_from(line):
    try:
        cmd = line.strip()                                      # to ensure no space are in front or at the back call the function strip()
        cmd = cmd.decode('utf8')
        if cmd == STROKE_START_RESPONSE:                        # with is "SS" from the waterrower
            return build_event(type='stroke_start', raw=cmd)    # Call the methode to create a dict with the name stroke_start and the row command used for it "SS"
        elif cmd == STROKE_END_RESPONSE:                        # with is "SE" from the waterrower
            return build_event(type='stroke_end', raw=cmd)      # Call the methode to create a dict with the name stroke_end and the row command used for it "SE"
        elif cmd == OK_RESPONSE:                                # If waterrower responce "OK" do nothing
            return None
        elif cmd[:2] == MODEL_INFORMATION_RESPONSE:             # If MODEL information has been request, the model responce would be "IV"
            return build_event(type='model', raw=cmd)           #  Call the methode to create a dict with the model and the row command used for it "SE"
        elif cmd[:2] == READ_MEMORY_RESPONSE:                   # if after memory request the responce comes from the waterrower
            return read_reply(cmd)                              # proced to the function read_reply which strips away everything and keeps the value and create the event dict for that request
        elif cmd[:4] == PING_RESPONSE:                              # if Ping responce is recived which is all the time the rower is in standstill
            return build_event(type='ping', raw=cmd)                                         # do nothing
        elif cmd[:1] == PULSE_COUNT_RESPONSE:                   # Pluse count count the amount of 25 teeth passed 25teeth passed = P1
            return None                                         # do nothing
        elif cmd == ERROR_RESPONSE:                             # If Waterrower responce with an error
            return build_event(type='error', raw=cmd)           # crate an event with the dict entry error and the raw command
        else:                                                   # for an unforeasable repsonce responde with non
            #print("something is wrong")
            #print(cmd)
            #ignore
            #WR_RESPONSE
            #AND INTERACTIVE_MODE
            return None
    except Exception as e:
        logging.error('could not build event for: %s %s', line, e)

####### WaterRower class ########

class Rower(object):
    def __init__(self, options=None):
        self._callbacks = set()                 # defines an empty set
        self._stop_event = threading.Event()    # defines the stop event in order to stop the threads requesting and capturing
        self._demo = False                      # set demo is set to true then use the fakeS4 but for the moment it is disaalbe
        self._lock = threading.Lock()
        # if options and options.demo:
        #     from demo import FakeS4
        #     self._serial = FakeS4()
        #     self._demo = True
        # else:
        self._serial = serial.Serial()
        self._serial.baudrate = 19200
        self.BleWRValues = {
                            'stroke_rate': 0,
                            'total_strokes': 0,
                            'total_distance_m': 0,
                            'instantaneous pace': 0,
                            'watts': 0,
                            'total_kcal': 0,
                            'total_kcal_hour': 0,
                            'total_kcal_min': 0,
                            'heart_rate': 0,
                            'elapsedtime': 0.0,
                            }

        self.LastPing = 0
        self.event_ble = {}
        self.secondsWR = 0
        self.minutesWR = 0
        self.hoursWR = 0
        self.elapsetime = 0
        self.elapsetimeprev = 0
        # If I wanna stop those thread from outside I just call xxxxx_stop_event.set() to stop it
        self.event = 0
        self._request_thread = build_daemon(target=self.start_requesting) # start the thread requesting during class init
        self._capture_thread = build_daemon(target=self.start_capturing)    # Start the thread capurting during class init
        self._ble_capture_thread = build_daemon(target=self.event_BLE)
        self._request_thread.start()
        self._capture_thread.start()
        self._ble_capture_thread.start()


# This function is used to check if the connection to the waterrower is alive and if the threads request and caputre are running
    def is_connected(self):
        return self._serial.isOpen() and is_live_thread(self._request_thread) and \
            is_live_thread(self._capture_thread)

# This private function tries to find the serial port. Which for waterrower is "/dev/ttyACM0" and if found opens the serial connection
    def _find_serial(self):
        if not self._demo:
            self._serial.port = find_port()
        try:
            self._serial.open()
            print("serial open")
        except serial.SerialException as e:
            print("serial open error waiting")
            time.sleep(5)
            self._serial.close()
            self._find_serial()

# this function open and enable the connection to the waterrower and set it up to be ready
    def open(self):
        if self._serial and self._serial.isOpen():  # checks if serial.serial is true and serial is alreay open
            self._serial.close()                    # if both are true then close the connection
        self._find_serial()                         # and start searching for Serial and open it
        if self._stop_event.is_set():               # if from external the _stop_event is triggered, the reset the threads
            print("reset threads")
            self._stop_event.clear()                # flush the _stop_event from true to false
            self._request_thread = build_daemon(target=self.start_requesting) # define the requesting daemon
            self._capture_thread = build_daemon(target=self.start_capturing)  # define the capturing damemon
            self._ble_capture_thread = build_daemon(target=self.event_BLE)
            self._request_thread.start()    # start the request_thread
            self._capture_thread.start()    # start the capture_thread
            self._ble_capture_thread.start()
        print("write USB_REQUEST")
        self.write(USB_REQUEST)             # call the write function which will write to the serial port "USB\r\n" which the waterrower will aknowledge with "_WR_"

# This function is called to tell the waterrower that the conntection will be terminate close the serial port.
    def close(self):
        self.notify_callbacks(build_event("exit")) # add to the __callback set the exit event
        if self._stop_event:                        # checks if _stop_event is true
            self._stop_event.set()                  # if yes then set it to stop the threads
        if self._serial and self._serial.isOpen():  # check if the serial connection and the serial connection is open
            self.write(EXIT_REQUEST)                # write to the waterrower the exit command
            time.sleep(0.1)                         # time for capture and request loops to stop running
            self._serial.close()                    # close the serial connection to the waterrower

# the write function gets the ready to send command. e.g "RESET" or IDD0A0 which needs to be build with request_address
    def write(self, raw):
        try:
            self._serial.write(str.encode(raw.upper() + '\r\n')) # sends the command with the return carrier and newline carrier encode str python3
            self._serial.flush()                     # clear the send buffer
        except Exception as e:                       # if it didn't work, will try to reconnect to the serial port
            print(e)
            print("Serial error try to reconnect")
            self.open()                              # trigger open function in order to reconnect to the waterrower

# function to capture the waterrower responces in a while loop. This loop can be terminate by setting the _stop_event.set() command .
    def start_capturing(self):
        while not self._stop_event.is_set(): # checks if the stop event has been set. if yes, stop the while loop
            if self._serial.isOpen():        # if event stop is not set check if serial connection is open
                try:
                    line = self._serial.readline() # read incoming lines from serial stream
                    event = event_from(line)       # check what kind of message has been recvied from the waterrower eg. RESET or IDD0A8015 .... and return the dict with the informations
                    if event:                      # if event is not None e.g ping which result in a return none then
                        self.notify_callbacks(event) # call the function TODO: check what the functions does
                        #self.event_BLE(event)
                        self._lock.acquire()
                        self.event = event
                        self._lock.release()
                        #print(self.event)
                except Exception as e:
                    print("could not read %s" % e)
                    try:
                        self._serial.reset_input_buffer() # if couldn't get a responce try to clean the incomming buffer of the serial
                    except Exception as e2:
                        print("could not reset_input_buffer %s" % e2)

            else:
                self._stop_event.wait(0.1)  # if stop event is not set but the serial connection is not yet activate retry in 0.1 sec again.

# function to request from the rower the different data from the differnte memory location on the S4 computer
    def start_requesting(self):
        while not self._stop_event.is_set():    # checks if the stop event has been set. if yes, stop the while loop
            if self._serial.isOpen():           # if event stop is not set check if serial connection is open
                for address in MEMORY_MAP:      # Iterates over the memory map
                    if 'not_in_loop' not in MEMORY_MAP[address]: # if instant of the dict with type the value of this dict is 'not_in_loo' then skip this address and go to the next
                        self.request_address(address)               # trigger function request_address which will format the memory address and call the function write to send it over serial to the waterrower
                        self._stop_event.wait(0.025)                # wait 25ms for the responce according to the Water Rower S4 S5 USB Protocol Issue 1

            else:
                self._stop_event.wait(0.1)                          # is stop event is still false but serial is not true keep looping and the thread running

# This function write to the serial port "RESET/n/r" to reset the waterrower. It then
    def reset_request(self):
        self.write(RESET_REQUEST)                   # This calls the function write in order to write to the serial port
        self.notify_callbacks(build_event('reset'))

#This function request Model and Tank level from the waterrower
    def request_info(self):
        self.write(MODEL_INFORMATION_REQUEST)   # This call the function write and writes "IV?" to check waterrower version
        self.request_address('0A9')             # This ask for tank level with the memory address 0A9.

# This function create the command which needs to be send to the waterrower to get information or to set it
    def request_address(self, address):
        size = MEMORY_MAP[address]['size']  # This checks the byte size of the address in the MEMORY_MAP dict
        cmd = SIZE_MAP[size]                # Checks the Size dict for IRS, IRD or IRT
        self.write(cmd + address)           # This calls the function write in order to write to the serial port

########### I don't know yet what he is doing here ! #######################

    def notify_callbacks(self, event):
        #print(event)
        for cb in self._callbacks:
            cb(event)
            print(cb(event))

    def event_BLE(self):
        while not self._stop_event.is_set():
            self._lock.acquire()
            self.event_ble = self.event
            self._lock.release()
            if self.event_ble:
                if self.event_ble['type'] == 'ping':
                    #print(self.event_ble['raw'] ,self.event_ble['at'])  # problem set value to zero if no movement
                    pass
                if self.event_ble['type'] == 'stroke_rate':
                    self.BleWRValues.update({'stroke_rate': (self.event_ble['value']*2)})
                if self.event_ble['type'] == 'total_strokes':
                    self.BleWRValues.update({'total_strokes': self.event_ble['value']})
                if self.event_ble['type'] == 'total_distance_m':
                    self.BleWRValues.update({'total_distance_m': (self.event_ble['value'])})
                if self.event_ble['type'] == 'avg_distance_cmps':
                    if self.event_ble['value'] == 0:
                        pass
                    else:
                        InstantaneousPace = (500 * 100)/ self.event_ble['value']
                        self.BleWRValues.update({'instantaneous pace': InstantaneousPace})
                # 500 m => 50000 cm, XX cm/s = s (500m  * 100cm/1m) / XX cm/s  =  XX.XXX s
                if self.event_ble['type'] == 'watts':
                    self.BleWRValues.update({'watts': self.event_ble['value']})
                if self.event_ble['type'] == 'total_kcal':
                    self.BleWRValues.update({'total_kcal': (self.event_ble['value'])/1000}) # in cal
                if self.event_ble['type'] == 'total_kcal_h':                                # must calclatre it first
                    self.BleWRValues.update({'total_kcal': 1})
                if self.event_ble['type'] == 'total_kcal_min':                              # must calclatre it first
                    self.BleWRValues.update({'total_kcal': 1})
                if self.event_ble['type'] == 'heart_rate':
                    self.BleWRValues.update({'heart_rate': 0}) # in cal
                if self.event_ble['type'] == 'display_sec':
                    self.secondsWR = self.event_ble['value']
                if self.event_ble['type'] == 'display_min':
                    self.minutesWR = self.event_ble['value']
                if self.event_ble['type'] == 'display_hr':
                    self.hoursWR = self.event_ble['value']
                else:
                    pass
            else:
                #print("running as thread")
                pass
            self.elapsetime = datetime.timedelta(seconds=self.secondsWR,minutes=self.minutesWR,hours=self.hoursWR)
            self.elapsetime = self.elapsetime.total_seconds()
            if self.elapsetimeprev <= self.elapsetime:
                self.BleWRValues.update({'elapsedtime':self.elapsetime})
                #print(self.elapsetime)
                self.elapsetimeprev = self.elapsetime
            else:
                pass
            #print(self.BleWRValues)

# Add and remove stuff from
    def register_callback(self, cb):
        self._callbacks.add(cb)

    def remove_callback(self, cb):
        self._callbacks.remove(cb)

def main(in_q,ble_out_q):
    S4 = Rower()
    S4.open()
    S4.reset_request()
    #def MainthreadWaterrower(in_q):
    print("THREAD - Waterrower started")
    while True:
        #print('test')
        #print('Ble dict {0}'.format(S4.BleWRValues))
        if in_q.empty() == False:
            resetRequest_ble = in_q.get()
            print(resetRequest_ble)
            S4.reset_request()
        else:
            pass
        #ble_out_q.put(S4.BleWRValues)
        ble_out_q.append(S4.BleWRValues)
        print(ble_out_q)
        #print(ble_out_q.qsize())
        #print(S4.is_connected())
        #Queue.task_done()
        time.sleep(0.1)

#  in the while loop create a timestamp and compare it with the previouse one. Create a Delta of 500ms = 0.5 sec
#

if __name__ == '__main__':
    main(None)
