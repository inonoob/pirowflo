import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import subprocess


def button_start_callback(channel):
    subprocess.run(["python3","/home/pi/pirowflo/src/waterrowerthreads.py","-i","s4","-b"])
    print("Button was pushed!")

def button_stop_callback(channel):
    subprocess.run(["python3","/home/pi/pirowflo/src/waterrowerthreads.py","-i","s4","-b"])
    print("Button was pushed!")

def button_resetpi_callback(channel):
    subprocess.run(["sudo","reboot"])
    print("Button was pushed!")


GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
GPIO.setup(21, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, GPIO.PUD_UP)
# GPIO.setup(6, GPIO.IN, GPIO.PUD_UP)
# GPIO.setup(19, GPIO.IN, GPIO.PUD_UP)
# GPIO.setup(5, GPIO.IN, GPIO.PUD_UP)
# GPIO.setup(26, GPIO.IN, GPIO.PUD_UP)
# GPIO.setup(13, GPIO.IN, GPIO.PUD_UP)

GPIO.add_event_detect(21, GPIO.RISING, callback=button_start_callback)  # Setup event on pin 10 rising edge
GPIO.add_event_detect(20, GPIO.RISING, callback=button_stop_callback)
GPIO.add_event_detect(16, GPIO.RISING, callback=button_resetpi_callback)
# GPIO.add_event_detect(6, GPIO.RISING, callback=button_callback)
# GPIO.add_event_detect(19, GPIO.RISING, callback=button_callback)
# GPIO.add_event_detect(5, GPIO.RISING, callback=button_callback)
# GPIO.add_event_detect(26, GPIO.RISING, callback=button_callback)
# GPIO.add_event_detect(13, GPIO.RISING, callback=button_callback)
message = input("Press enter to quit\n\n")  # Run until someone presses enter

GPIO.cleanup()  # Clean up