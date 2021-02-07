# 1.44inch LCD display (128x128) HAT for Raspberry Pi 

GPIO for the joystick and 3 buttons

|SYMBOL	|RASPBERRY PI PIN (BCM)	| DESCRIPTION
|:-------|:-------|:-------|
|KEY1 	|P21 	|Button 1/GPIO
|KEY2 	|P20 	|Button 2/GPIO
|KEY3 	|P16 	|Button 3/GPIO
|Joystick Up 	|P6 	|Joystick Up
|Joystick Down 	|P19 	|Joystick Down
|Joystick Left 	|P5 	|Joystick Left
|Joystick Right 	|P26 	|Joystick Right
|Joystick Press 	|P13 	|Joystick Press
|SCLK 	|P11/SCLK 	|SPI clock input
|MOSI 	|P10/MOSI 	|SPI data input
|DC 	|P25 	|Data/Command selection (high for data, low for command)
|CS 	|P8/CE0 	|Chip selection, low active
|RST 	|P27 	|Reset, low active
|BL 	|P24 	|Backlight


## example code to interace with the buttons 

    import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
    
    def button_callback(channel):
        print("Button was pushed!")
    
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BCM) # Use physical pin numbering
    GPIO.setup(21, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(20, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(16, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(6, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(19, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(5, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(26, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(13, GPIO.IN, GPIO.PUD_UP)
    
    
    GPIO.add_event_detect(21, GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge
    GPIO.add_event_detect(20, GPIO.RISING,callback=button_callback)
    GPIO.add_event_detect(16, GPIO.RISING,callback=button_callback)
    GPIO.add_event_detect(6, GPIO.RISING,callback=button_callback)
    GPIO.add_event_detect(19, GPIO.RISING,callback=button_callback)
    GPIO.add_event_detect(5, GPIO.RISING,callback=button_callback)
    GPIO.add_event_detect(26, GPIO.RISING,callback=button_callback)
    GPIO.add_event_detect(13, GPIO.RISING,callback=button_callback)
    message = input("Press enter to quit\n\n") # Run until someone presses enter
    
    GPIO.cleanup() # Clean up


## for the screen 

https://github.com/rm-hull/luma.oled 

