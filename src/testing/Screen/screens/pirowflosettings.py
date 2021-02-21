from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
from globalParameters import globalParameters

pirowflosettingid = 1
maxcounter = 3
mincounter = 0
# Main menu (screenid: 1)
def draw(device):
    #faicons = ImageFont.truetype(globalParameters.font_icons, size=18)
    font = ImageFont.truetype(globalParameters.font_text, size=10)
    fontawesome = ImageFont.truetype(globalParameters.font_icons, size=10)
    counter = globalParameters.counter
    if counter != globalParameters.oldcounter and counter <= maxcounter and counter >= mincounter:
        globalParameters.oldcounter = counter
        with canvas(device) as draw:
            if counter == 0:
                x = 0
                y = 10
            elif counter == 1:
                x = 0
                y = 20
            elif counter == 2:
                x = 0
                y = 40
            elif counter == 3:
                x = 0
                y = 50
            #draw.text((x, y), text="X", font=font, fill="white")
            draw.rectangle((x, y, x + 14, y + 10), outline=255, fill=0)

            draw.text((5, 2), text="------Interfaces------", font=font, fill="white")
            if globalParameters.SmartRowOn == 1:
                draw.text((2, 10), text="\uf205", font=fontawesome, fill="white")
            else:
                draw.text((2, 10), text="\uf204", font=fontawesome, fill="white")
            draw.text((20, 12),  text="Use SmartRow", font=font, fill="white")  # back
            if globalParameters.S4MonitorOn == 1:
                draw.text((2, 20), text="\uf205", font=fontawesome, fill="white")
            else:
                draw.text((2, 20), text="\uf204", font=fontawesome, fill="white")
            draw.text((20, 22), text="Use S4 Monitor", font=font, fill="white")  # back

            draw.text((5, 32), text="------Broadcasts------", font=font, fill="white")
            if globalParameters.BluetoothOn == 1:
                draw.text((2, 40), text="\uf205", font=fontawesome, fill="white")
            else:
                draw.text((2, 40), text="\uf204", font=fontawesome, fill="white")
            draw.text((20, 42),  text="Use Bluetooth LE", font=font, fill="white")  # back
            if globalParameters.AntplusOn == 1:
                draw.text((2, 50), text="\uf205", font=fontawesome, fill="white")
            else:
                draw.text((2, 50), text="\uf204", font=fontawesome, fill="white")
            draw.text((20, 52), text="Use Ant+", font=font, fill="white")  # back


    # Keep the cursor in the screen
    if counter > maxcounter: globalParameters.counter = mincounter
    if counter < mincounter: globalParameters.counter = maxcounter

'''
if the joystick button is pushed at the position with the counter number then the following function are exectuded depeding on the 
case
'''
def trigger():
    counter = globalParameters.counter
    print(counter)
    if counter == 0:
        if globalParameters.SmartRowOn == 0:
            globalParameters.SmartRowOn = 1
            globalParameters.S4MonitorOn = 0
        elif globalParameters.SmartRowOn == 1:
            globalParameters.SmartRowOn = 0
            globalParameters.S4MonitorOn = 1
        globalParameters.safePiRowFlosettings()
        globalParameters.setScreen(pirowflosettingid,counter)
    elif counter == 1:
        if globalParameters.S4MonitorOn == 0:
            globalParameters.S4MonitorOn = 1
            globalParameters.SmartRowOn = 0
        elif globalParameters.S4MonitorOn == 1:
            globalParameters.S4MonitorOn = 0
            globalParameters.SmartRowOn = 1
        globalParameters.safePiRowFlosettings()
        globalParameters.setScreen(pirowflosettingid,counter)
    elif counter == 2:
        if globalParameters.BluetoothOn == 0:
            globalParameters.BluetoothOn = 1
        elif globalParameters.BluetoothOn == 1:
            globalParameters.BluetoothOn = 0
            globalParameters.AntplusOn = 1
        globalParameters.safePiRowFlosettings()
        globalParameters.setScreen(pirowflosettingid,counter)
    elif counter == 3:
        if globalParameters.AntplusOn == 0:
            globalParameters.AntplusOn = 1
        elif globalParameters.AntplusOn == 1:
            globalParameters.AntplusOn = 0
            globalParameters.BluetoothOn = 1
        globalParameters.safePiRowFlosettings()
        globalParameters.setScreen(pirowflosettingid,counter)
