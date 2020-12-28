# -*- coding: utf-8 -*-
import threading
import logging
import time
import serial
import serial.tools.list_ports

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

# Display Settings (not used)
DISPLAY_SET_INTENSITY_MPS_REQUEST = "DIMS"
DISPLAY_SET_INTENSITY_MPH_REQUEST = "DIMPH"
DISPLAY_SET_INTENSITY_500M_REQUEST = "DI500"
DISPLAY_SET_INTENSITY_2KM_REQUEST = "DI2KM"
DISPLAY_SET_INTENSITY_WATTS_REQUEST = "DIWA"
DISPLAY_SET_INTENSITY_CALHR_REQUEST = "DICH"
DISPLAY_SET_INTENSITY_AVG_MPS_REQUEST = "DAMS"
DISPLAY_SET_INTENSITY_AVG_MPH_REQUEST = "DAMPH"
DISPLAY_SET_INTENSITY_AVG_500M_REQUEST = "DA500"
DISPLAY_SET_INTENSITY_AVG_2KM_REQUEST = "DA2KM"
DISPLAY_SET_DISTANCE_METERS_REQUEST = "DDME"
DISPLAY_SET_DISTANCE_MILES_REQUEST = "DDMI"
DISPLAY_SET_DISTANCE_KM_REQUEST = "DDKM"
DISPLAY_SET_DISTANCE_STROKES_REQUEST = "DDST"

# Interactive mode

INTERACTIVE_MODE_START_RESPONSE = "AIS"        # interactive mode requested by device
INTERACTIVE_MODE_START_ACCEPT_REQUEST = "AIA"  # confirm interactive mode, key input is redirect to PC
INTERACTIVE_MODE_END_REQUEST = "AIE"           # cancel interactive mode
INTERACTIVE_KEYPAD_RESET_RESPONSE = "AKR"      # RESET key pressed, interactive mode will be cancelled
INTERACTIVE_KEYPAD_UNITS_RESPONSE = "AK1"      # Units button pressed
INTERACTIVE_KEYPAD_ZONES_RESPONSE = "AK2"      # Zones button pressed
INTERACTIVE_KEYPAD_WORKOUT_RESPONSE = "AK3"    # Workout button pressed
INTERACTIVE_KEYPAD_UP_RESPONSE = "AK4"         # Up arrow button pressed
INTERACTIVE_KEYPAD_OK_RESPONSE = "AK5"         # Ok button pressed
INTERACTIVE_KEYPAD_DOWN_RESPONSE = "AK6"       # Down arrow button pressed
INTERACTIVE_KEYPAD_ADVANCED_RESPONSE = "AK7"   # Advanced button pressed
INTERACTIVE_KEYPAD_STORED_RESPONSE = "AK8"     # Stored Programs button pressed
INTERACTIVE_KEYPAD_HOLD_RESPONSE = "AK9"       # Hold/cancel button pressed

# Workout
WORKOUT_SET_DISTANCE_REQUEST = "WSI"                 # Define a distance workout + x(unit, 1-4) + YYYY = ACH
WORKOUT_SET_DURATION_REQUEST = "WSU"                 # Define a duration workout + YYYY = ACH seconds
WORKOUT_INTERVAL_START_SET_DISTANCE_REQUEST = "WII"  # Define an interval distance workout
WORKOUT_INTERVAL_START_SET_DURATION_REQUEST = "WIU"  # Define an interval duration workout
WORKOUT_INTERVAL_ADD_END_REQUEST = "WIN"             # Add/End an interval to a workout XXXX(==FFFFF to end) + YYYY

# UNITS
UNIT_METERS = 1
UNIT_MILES = 2
UNIT_KM = 3
UNIT_STROKES = 4

SIZE_MAP = {'single': 'IRS',
            'double': 'IRD',
            'triple': 'IRT',}

UNIT_MAP = {'meters': 1,
            'miles': 2,
            'km': 3,
            'strokes': 4}

SIZE_PARSE_MAP = {'single': lambda cmd: cmd[6:8],
                  'double': lambda cmd: cmd[6:10],
                  'triple': lambda cmd: cmd[6:12]}



def find_port():
    ports = serial.tools.list_ports.comports()
    for (i, (path, name, _)) in enumerate(ports):
        if "WR" in name:
            print("port found: %s" % path)
            return path

    print("port not found retrying in 5s")
    time.sleep(5)
    return find_port()


def build_daemon(target):
    t = threading.Thread(target=target)
    t.daemon = True
    return t


def build_event(type, value=None, raw=None):
    return {"type": type,
            "value": value,
            "raw": raw,
            "at": int(round(time.time() * 1000))}


def is_live_thread(t):
    return t and t.is_alive()


def read_reply(cmd):
    address = cmd[3:6]
    memory = MEMORY_MAP.get(address)
    if memory:
        size = memory['size']
        value_fn = SIZE_PARSE_MAP.get(size, lambda cmd: None)
        value = value_fn(cmd)
        if value is None:
            logging.error('unknown size: %s', size)
        else:
            return build_event(memory['type'], int(value, base=memory['base']), cmd)
    else:
        logging.error('cannot read reply for %s', cmd)


def event_from(line):
    try:
        cmd = line.strip()  # to ensure no space are in front or at the back call the function strip()
        cmd = cmd.decode('utf8')  # encode it to utf8 ro remove b'
        if cmd == STROKE_START_RESPONSE:  # with is "SS" from the waterrower
            return build_event(type='stroke_start', raw=cmd)  # Call the methode to create a dict with the name stroke_start and the row command used for it "SS"
        elif cmd == STROKE_END_RESPONSE:  # with is "SE" from the waterrower
            return build_event(type='stroke_end', raw=cmd)  # Call the methode to create a dict with the name stroke_end and the row command used for it "SE"
        elif cmd == OK_RESPONSE:  # If waterrower responce "OK" do nothing
            return None
        elif cmd[:2] == MODEL_INFORMATION_RESPONSE:  # If MODEL information has been request, the model responce would be "IV"
            return build_event(type='model', raw=cmd)  # Call the methode to create a dict with the model and the row command used for it "SE"
        elif cmd[:2] == READ_MEMORY_RESPONSE:  # if after memory request the responce comes from the waterrower
            return read_reply(cmd)  # proced to the function read_reply which strips away everything and keeps the value and create the event dict for that request
        elif cmd[:4] == PING_RESPONSE:  # if Ping responce is recived which is all the time the rower is in standstill
            return build_event(type='ping', raw=cmd)  # do nothing
        elif cmd[:1] == PULSE_COUNT_RESPONSE:  # Pluse count count the amount of 25 teeth passed 25teeth passed = P1
            return build_event(type='pulse', raw=cmd)  # do nothing
        elif cmd == ERROR_RESPONSE:  # If Waterrower responce with an error
            return build_event(type='error', raw=cmd)  # crate an event with the dict entry error and the raw command
        else:
            return None
    except Exception as e:
        logging.error('could not build event for: %s %s', line, e)


class Rower(object):
    def __init__(self, options=None):
        self._callbacks = set()
        self._stop_event = threading.Event()
        self._demo = False
        # if options and options.demo:
        #     from demo import FakeS4
        #     self._serial = FakeS4()
        #     self._demo = True
        # else:
        self._serial = serial.Serial()
        self._serial.baudrate = 19200

        self._request_thread = build_daemon(target=self.start_requesting)
        self._capture_thread = build_daemon(target=self.start_capturing)
        self._request_thread.start()
        self._capture_thread.start()

    def is_connected(self):
        return self._serial.isOpen() and is_live_thread(self._request_thread) and \
            is_live_thread(self._capture_thread)

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

    def open(self):
        if self._serial and self._serial.isOpen():
            self._serial.close()
        self._find_serial()
        if self._stop_event.is_set():
            print("reset threads")
            self._stop_event.clear()
            self._request_thread = build_daemon(target=self.start_requesting)
            self._capture_thread = build_daemon(target=self.start_capturing)
            self._request_thread.start()
            self._capture_thread.start()
        self.write(USB_REQUEST)

    def close(self):
        self.notify_callbacks(build_event("exit"))
        if self._stop_event:
            self._stop_event.set()
        if self._serial and self._serial.isOpen():
            self.write(EXIT_REQUEST)
            time.sleep(0.1)  # time for capture and request loops to stop running
            self._serial.close()

    def write(self, raw):
        try:
            self._serial.write(str.encode(raw.upper() + '\r\n'))
            self._serial.flush()
        except Exception as e:
            print(e)
            print("Serial error try to reconnect")
            self.open()

    def start_capturing(self):
        while not self._stop_event.is_set():
            if self._serial.isOpen():
                try:
                    line = self._serial.readline()
                    event = event_from(line)
                    if event:
                        self.notify_callbacks(event)
                except Exception as e:
                    print("could not read %s" % e)
                    try:
                        self._serial.reset_input_buffer()
                    except Exception as e2:
                        print("could not reset_input_buffer %s" % e2)

            else:
                self._stop_event.wait(0.1)

    def start_requesting(self):
        while not self._stop_event.is_set():
            if self._serial.isOpen():
                for address in MEMORY_MAP:
                    if 'not_in_loop' not in MEMORY_MAP[address]:
                        self.request_address(address)
                        self._stop_event.wait(0.025)
            else:
                self._stop_event.wait(0.1)


    def reset_request(self):
        self.write(RESET_REQUEST)
        self.notify_callbacks(build_event('reset'))

    def request_info(self):
        self.write(MODEL_INFORMATION_REQUEST)
        self.request_address('0A9')

    def request_address(self, address):
        size = MEMORY_MAP[address]['size']
        cmd = SIZE_MAP[size]
        self.write(cmd + address)

    def register_callback(self, cb):
        self._callbacks.add(cb)

    def remove_callback(self, cb):
        self._callbacks.remove(cb)

    def notify_callbacks(self, event):
        for cb in self._callbacks:
            cb(event)



