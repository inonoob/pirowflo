from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
from globalParameters import globalParameters


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
                y = 0
            elif counter == 1:
                x = 0
                y = 10
            elif counter == 2:
                x = 0
                y = 20
            elif counter == 3:
                x = 0
                y = 30
            elif counter == 4:
                x = 0
                y = 40
            elif counter == 5:
                x = 0
                y = 50
            #draw.text((x, y), text="X", font=font, fill="white")
            draw.rectangle((x, y, x + 14, y + 10), outline=255, fill=0)

            draw.text((2, 0), text="\uf205", font=fontawesome, fill="white")
            draw.text((2, 10), text="\uf204", font=fontawesome, fill="white")
            draw.text((2, 20), text="\uf204", font=fontawesome, fill="white")
            draw.text((2, 30), text="\uf204", font=fontawesome, fill="white")
            draw.text((2, 40), text="\uf204", font=fontawesome, fill="white")
            draw.text((2, 50), text="\uf204", font=fontawesome, fill="white")

            draw.text((5, 2),  text="   S4 Blue + Ant+", font=font, fill="white")  # back
            draw.text((5, 12), text="   S4 Blue only", font=font, fill="white")  # radio (old icon: f145)
            draw.text((5, 22), text="   S4 Ant+ only", font=font, fill="white")  # playlists
            draw.text((5, 32), text="   SR Blue + Ant+", font=font, fill="white")  # shutdown
            draw.text((5, 42), text="   SR Blue only", font=font, fill="white")  # shutdown
            draw.text((5, 52), text="   SR Ant+ only", font=font, fill="white")  # shutdown
    # Keep the cursor in the screen
    if counter > 5: globalParameters.counter = 0
    if counter < 0: globalParameters.counter = 5


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