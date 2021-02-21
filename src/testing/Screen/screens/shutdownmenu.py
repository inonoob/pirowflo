from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
from globalParameters import globalParameters

#Shutdown menu (screenid: 3)
def draw(device):
    font = ImageFont.truetype(globalParameters.font_text, size=12)
    # faicons = ImageFont.truetype(globalParameters.font_icons, size=18)
    counter = globalParameters.counter
    if counter != globalParameters.oldcounter and counter <= 2 and counter >= 0:
        globalParameters.oldcounter = counter
        with canvas(device) as draw:
            draw.text((5, 2), text="Wirklich ausschalten?", font=font, fill="white")
            if counter == 0:
                x = 10
                y = 22
            elif counter == 1:
                x = 47
                y = 22
            else:
                x = 89
                y = 22
            draw.rectangle((x, y, x+30, y+40), outline=255, fill=0)

            draw.text((13, 25), text="Nein", font=font, fill="white")
            # draw.text((15, 40), text="\uf0a8", font=faicons, fill="white")

            draw.text((56, 25), text="Ja", font=font, fill="white")
            # draw.text((55, 40), text="\uf011", font=faicons, fill="white")

            draw.text((92, 25), text="DSP", font=font, fill="white")
            # draw.text((94, 40), text="\uf108", font=faicons, fill="white")

    if counter > 2: globalParameters.counter = 0
    if counter < 0: globalParameters.counter = 0

def trigger():
    counter = globalParameters.counter
    if counter == 0: globalParameters.setScreen(0)
    elif counter == 1: globalParameters.setScreen(0)
    elif counter == 2: globalParameters.setScreen(2)