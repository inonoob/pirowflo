from PIL import ImageFont
from luma.core.render import canvas
from globalParameters import globalParameters

pirowflosettingid = 1

# Main menu (screenid: 1)
def draw(device):
    #faicons = ImageFont.truetype(globalParameters.font_icons, size=18)
    font = ImageFont.truetype(globalParameters.font_text, size=10)
    fontawesome = ImageFont.truetype(globalParameters.font_icons, size=15)
    counter = globalParameters.counter
    if counter != globalParameters.oldcounter and counter <= 5 and counter >= 0:
        globalParameters.oldcounter = counter
        with canvas(device) as draw:
            if counter == 0:
                x = 108
                y = 9
            elif counter == 1:
                x = 108
                y = 27
            elif counter == 2:
                x = 108
                y = 47
            #draw.text((x, y), text="X", font=font, fill="white")
            draw.rectangle((x, y, x + 16, y + 16), outline=255, fill=0)

            draw.text((0, 2), text="--------PiRowFlo--------", font=font, fill="white")
            draw.text((105, 10), text="|", font=font, fill="white")
            draw.text((105, 20), text="|", font=font, fill="white")
            draw.text((105, 30), text="|", font=font, fill="white")
            draw.text((105, 40), text="|", font=font, fill="white")
            draw.text((105, 50), text="|", font=font, fill="white")
            draw.text((105, 60), text="|", font=font, fill="white")
            draw.text((110, 10), text="\uf04b", font=fontawesome, fill="white")
            draw.text((110, 28), text="\uf1de", font=fontawesome, fill="white")
            draw.text((110, 48), text="\uf019", font=fontawesome, fill="white")
            draw.text((0, 14), text="Status: "+ globalParameters.status, font=font, fill="white")
            # draw.text((0, 26), text="BLE: Online", font=font, fill="white")
            # draw.text((0, 40), text="ANT+: Offline", font=font, fill="white")
            draw.text((0, 26), text="ip: "+globalParameters.ipaddr, font=font, fill="white")



    # Keep the cursor in the screen
    if counter > 2: globalParameters.counter = 0
    if counter < 0: globalParameters.counter = 2


def trigger():
    counter = globalParameters.counter
    if counter == 0:
        globalParameters.setScreen(2)
    elif counter == 1:
        globalParameters.setScreen(1)
    elif counter == 2:
        globalParameters.setScreen(3)