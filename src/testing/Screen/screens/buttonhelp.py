from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
from globalParameters import globalParameters


# Main menu (screenid: 1)
def draw(device):
    #faicons = ImageFont.truetype(globalParameters.font_icons, size=18)
    font = ImageFont.truetype(globalParameters.font_text, size=10)
    fontawesome = ImageFont.truetype(globalParameters.font_icons, size=12)
    counter = globalParameters.counter
    if counter != globalParameters.oldcounter and counter <= 3 and counter >= 0:
        globalParameters.oldcounter = counter
        with canvas(device) as draw:
            # rectangle as selection marker
            # if counter < 3:  # currently 3 icons in one row
            #     x = 2
            #     y = 7 + counter * 35
            # else:
            #     x = 35
            #     y = 6 + (counter - 3) * 35
            # draw.rectangle((x, y, x + 25, y + 25), outline=255, fill=0)

            # icons as menu buttons
            draw.text((5, 2), text="Start PiRowFlo", font=font, fill="white")  # back
            #draw.text((110, 2), text="==>", font=font, fill="white")  # back

            draw.text((110, 0), text="\uf0a9", font=fontawesome, fill="white")

            #draw.text((5, 12), text=" ", font=font, fill="white")  # radio (old icon: f145)
            draw.text((5, 24), text="Stop PiRowFlo", font=font, fill="white")  # playlists
            #draw.text((110, 24), text="==>", font=font, fill="white")  # back
            draw.text((110, 20), text="\uf0a9", font=fontawesome, fill="white")
            #draw.text((5, 36), text=" ", font=font, fill="white")  # playlists
            draw.text((5, 48), text="Restart Pi", font=font, fill="white")  # playlists
            #draw.text((110, 48), text="==>", font=font, fill="white")  # back
            draw.text((110, 44), text="\uf0a9", font=fontawesome, fill="white")
            #draw.text((5, 30), text="this is ", font=font, fill="white")  # shutdown
            #draw.text((5, 40), text="a ", font=font, fill="white")  # shutdown
            #draw.text((5, 50), text="test", font=font, fill="white")  # shutdown
    # Keep the cursor in the screen
    if counter > 3: globalParameters.counter = 0
    if counter < 0: globalParameters.counter = 0


def trigger():
    counter = globalParameters.counter
    if counter == 0:
        globalParameters.setScreen(0)
    elif counter == 1:
        globalParameters.setScreen(1)
    elif counter == 2:
        globalParameters.setScreen(2)
    # elif counter == 3:
    #     globalParameters.setScreen(3)