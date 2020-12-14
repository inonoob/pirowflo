import time
import serial
import os
import signal


# Variables for connection
SerialPort = "/dev/ttyACM0"  # ergobike adress; commented to avoid wrong initiation
BauderatePort = 115200
TimeoutPort = 0.2
port = serial.Serial("/dev/ttyACM0", baudrate=19200, timeout=0.2)

# Variable for values
StrokeRate = 0.0  # Stroke Rate stroke/min *0.5 int8
StrokeCount = 0  # actual cycling cadence int16
TotalDistance = 0  # m actual cycling speed int16 + int8
InstantaneousPace = 0 # in sec int16
InstantaneousPower = 0 # in W int16
TotalEnergy = 0 # Kcal int16
EnergyPerHour = 0 # kcal int16
EnergyPerMin = 0 # kcal int8
HeartRate = 0 # bpm int8
ElapsedTime = 0 # s int16

prevMsR = 0

BLEvalueRower = []

def openConncetion():
    print("Open connection to Waterrower")
    port.write(str.encode("USB\r\n"))
    rcv = port.readline()
    if rcv == b"_WR_\r\n":
        print("Waterrower Ready")
    else:
        print("Waterrower hasn't respond")  #
        exit()

def resetRower():

    global StrokeRate # Stroke Rate stroke/min *0.5 int8
    global StrokeCount  # actual cycling cadence int16
    global TotalDistance  # m actual cycling speed int16 + int8
    global InstantaneousPace  # in sec int16
    global InstantaneousPower  # in W int16
    global TotalEnergy  # Kcal int16
    global EnergyPerHour  # kcal int16
    global EnergyPerMin  # kcal int8
    global HeartRate  # bpm int8
    global ElapsedTime  # s int16
    global prevMsR

    print("Waterrower S4 Reset")
    port.write(str.encode("RESET\r\n"))
    print(port.readline())
    StrokeRate = 0.0  # Stroke Rate stroke/min *0.5 int8
    StrokeCount = 0  # actual cycling cadence int16
    TotalDistance = 0  # m actual cycling speed int16 + int8
    InstantaneousPace = 0  # in sec int16
    InstantaneousPower = 0  # in W int16
    TotalEnergy = 0  # Kcal int16
    EnergyPerHour = 0  # kcal int16
    EnergyPerMin = 0  # kcal int8
    HeartRate = 0  # bpm int8
    ElapsedTime = 0  # s int16
    prevMsR = 0

def closeConnection():
    print("Exit Waterrower and close serial connection")
    port.write(str.encode("EXIT\r\n"))
    print(port.readline())
    print("connection to Waterrower terminate")
    port.close()
    print("Serial connection terminate")

def loop():
    global StrokeRate # Stroke Rate stroke/min *0.5 int8
    global StrokeCount  # actual cycling cadence int16
    global TotalDistance  # m actual cycling speed int16 + int8
    global InstantaneousPace  # in sec int16
    global InstantaneousPower  # in W int16
    global TotalEnergy  # Kcal int16
    global EnergyPerHour  # kcal int16
    global EnergyPerMin  # kcal int8
    global HeartRate  # bpm int8
    global ElapsedTime  # s int16
    global prevMsR
    global BLEvalueRower

    print("Check if Serial connection to Waterrower is etablished ")
    if port.isOpen():  #
        print("Serial connection to Waterrower is established and online ")
        while port.isOpen():
            currentMillis = int(round(time.time() * 1000))
            print(currentMillis)

            if (currentMillis - prevMsR) >= 1:
                port.write(str.encode("IRT08A\r\n")) # KCAL
                time.sleep(0.25)
                rcv = port.readlines()
                print(rcv)
                port.write(str.encode("IRS1A9\r\n")) # Stroke rate
                time.sleep(0.25)
                rcv = port.readlines()
                print(rcv)
                port.write(str.encode("IRD14A\r\n")) # Speed
                time.sleep(0.25)
                rcv = port.readlines()
                print(rcv)
                print(rcv)
                port.write(str.encode("IRD140\r\n")) # Stroke count
                time.sleep(0.25)
                rcv = port.readlines()
                print(rcv)
                port.write(str.encode("IRD088\r\n")) # watts
                time.sleep(0.25)
                rcv = port.readlines()
                print(rcv)
                port.write(str.encode("IRD057\r\n")) #Distance
                time.sleep(0.25)
                rcv = port.readlines()
                print(rcv)
                time.sleep(0.25)

                prevMsR = currentMillis
                print(currentMillis)

        # "1A9": ["stroke_rate", "S"],
        # "140": ["stroke_count", "D"],
        # "088": ["watts", "D"]

def sigint_handler(sig, frame):
    if sig == signal.SIGINT:
        closeConnection()
        exit()
    else:
        raise ValueError("Undefined handler for '{}' ".format(sig))

signal.signal(signal.SIGINT, sigint_handler) # is if I quit the loop or interupte that the system close the connection gracefully

if __name__ == '__main__':

    openConncetion()
    time.sleep(10)
    resetRower()
    time.sleep(2)
    loop()
    time.sleep(2)
    closeConnection()
