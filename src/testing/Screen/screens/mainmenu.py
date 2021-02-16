from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
from globalParameters import globalParameters

pirowflosettingid = 1

# Main menu (screenid: 1)
def draw(device):
    #faicons = ImageFont.truetype(globalParameters.font_icons, size=18)
    font = ImageFont.truetype(globalParameters.font_text, size=10)
    fontawesome = ImageFont.truetype(globalParameters.font_icons, size=10)
    counter = globalParameters.counter
    if counter != globalParameters.oldcounter and counter <= 5 and counter >= 0:
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
    if counter > 3: globalParameters.counter = 0
    if counter < 0: globalParameters.counter = 3


def trigger():
    counter = globalParameters.counter
    if counter == 0:
        globalParameters.setScreen(0)
    elif counter == 1:
        globalParameters.setScreen(1)
    elif counter == 2:
        globalParameters.setScreen(2)