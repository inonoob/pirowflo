''''
the setupHandler is responsible to handle the user inputs via the buttons. This trigger changes or launch the
different scripts
'''


# Only avaiable on raspberry pi
try:
    from RPi import GPIO
except:
    pass
from globalParameters import globalParameters
import threading
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c, spi
from time import sleep
import helperFunctions
import screens.startscreen
import screens.mainmenu
import subprocess

def getipaddress():
    ipaddr = subprocess.run('ifconfig wlan0 | grep "inet 192" | cut -c 14-25',shell=True,capture_output=True)
    ipadd= str(ipaddr.stdout)
    ipadd = ipadd[2:-3].strip()
    print(ipadd)
    globalParameters.ipaddr = ipadd


# Setup OLED display
print("Connect to display")
serial = spi(device=0, port=0) # set the screen port
device = sh1106(serial, rotate=2) # give the screenport to the screen sh1106
device.contrast(245) # set the contrast of the display
screens.startscreen.draw(device)  # User should have something to look at during start

# Set up buttons and joystick
print("Set up rotary encoder")
button1 = int(globalParameters.config.get('Pins', 'button1'))
button2 = int(globalParameters.config.get('Pins', 'button2'))
button3 = int(globalParameters.config.get('Pins', 'button3'))
joystickUp = int(globalParameters.config.get('Pins', 'joystickUp'))
joystickDown = int(globalParameters.config.get('Pins', 'joystickDown'))
joystickLeft = int(globalParameters.config.get('Pins', 'joystickLeft'))
joystickright = int(globalParameters.config.get('Pins', 'joystickright'))
joystickbutton = int(globalParameters.config.get('Pins', 'joystickbutton'))


GPIO.setmode(GPIO.BCM)
GPIO.setup(button1, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(button3, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(joystickUp, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(joystickDown, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(joystickLeft, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(joystickright, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(joystickbutton, GPIO.IN, GPIO.PUD_UP)

Lockbutton = threading.Lock()  # create lock for rotary switch

def button_start_callback(channel):
    Lockbutton.acquire()
    globalParameters.createPiRowFlocmd()
    globalParameters.currentstarted = globalParameters.pirowflocmd
    globalParameters.activemenu = 0
    globalParameters.setScreen(0)
    result = subprocess.run(globalParameters.pirowflocmd,capture_output=True)
    status = str(result.stdout)
    status = status[2:-3].strip()
    status = status.split(' ')
    #print(status[1])
    globalParameters.status = status[1]
    globalParameters.activemenu = 0
    globalParameters.setScreen(0)
    #screens.mainmenu.draw(device)
    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)
    print("Start Script button was pushed!")
    Lockbutton.release()

def button_stop_callback(channel):
    Lockbutton.acquire()
    if globalParameters.currentstarted is not None:
        globalParameters.activemenu = 0
        globalParameters.setScreen(0)
        result = subprocess.run(['supervisorctl','stop',globalParameters.currentstarted[2]],capture_output=True)
        status = str(result.stdout)
        status = status[2:-3].strip()
        status = status.split(' ')
        globalParameters.status = str(status[1])
        globalParameters.activemenu = 0
        globalParameters.setScreen(0)
    else:
        globalParameters.activemenu = 0
        globalParameters.setScreen(0)
    print("Stop Script button was pushed!")
    Lockbutton.release()

def button_resetpi_callback(channel):
    Lockbutton.acquire()
    #subprocess.run(["sudo","reboot"])
    helperFunctions.updatePiRowFlo()
    print("Button was pushed!")
    Lockbutton.release()

def shutdown():
    # Cleanup GPIO connections
    GPIO.cleanup()
    exit()

# Interrupt handler for push button in rotary encoder
def JoyButtonmenuaction(channel):
    Lockbutton.acquire()
    globalParameters.trigger = True
    print("joystickbutton was pushed!")
    Lockbutton.release()

def menuback(channel):
    Lockbutton.acquire()
    if globalParameters.activemenu < 1:
         globalParameters.activemenu = 2# back the main menu
    else:
        globalParameters.activemenu -= 1
    print(globalParameters.activemenu)
    globalParameters.setScreen(globalParameters.activemenu)
    print("left was pushed!")
    Lockbutton.release()

def menuforward(channel):
    Lockbutton.acquire()
    if globalParameters.activemenu > 1:
        globalParameters.activemenu = 0
    else:
        globalParameters.activemenu += 1 # back the main menu
    print(globalParameters.activemenu)
    globalParameters.setScreen(globalParameters.activemenu)
    print("right was pushed!")
    Lockbutton.release()

def menuup(channel):
    Lockbutton.acquire()
    globalParameters.counter -= 1
    print("Up was pushed!")
    Lockbutton.release()

def menudown(channel):
    Lockbutton.acquire()
    globalParameters.counter += 1 # the menu's always start
    print("Down was pushed!")
    Lockbutton.release()

print("Attaching interrupts")
GPIO.add_event_detect(button1, GPIO.RISING, callback=button_start_callback, bouncetime=300)
GPIO.add_event_detect(button2, GPIO.RISING, callback=button_stop_callback, bouncetime=300)
GPIO.add_event_detect(button3, GPIO.RISING, callback=button_resetpi_callback, bouncetime=300)
GPIO.add_event_detect(joystickUp, GPIO.RISING, callback=menuup, bouncetime=300)
GPIO.add_event_detect(joystickDown, GPIO.RISING, callback=menudown, bouncetime=300)
GPIO.add_event_detect(joystickLeft, GPIO.RISING, callback=menuback, bouncetime=300)
GPIO.add_event_detect(joystickright, GPIO.RISING, callback=menuforward, bouncetime=300)
GPIO.add_event_detect(joystickbutton, GPIO.RISING, callback=JoyButtonmenuaction, bouncetime=300)
getipaddress()

print("Setup finished")
print()
