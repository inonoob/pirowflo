from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
from globalParameters import globalParameters


# Main menu (screenid: 1)
def draw(device):
    #faicons = ImageFont.truetype(globalParameters.font_icons, size=18)
    font = ImageFont.truetype(globalParameters.font_text, size=10)
    counter = globalParameters.counter
    if counter != globalParameters.oldcounter and counter <= 5 and counter >= 0:
        globalParameters.oldcounter = counter
        with canvas(device) as draw:
            if counter == 0:
                x = 9
                y = 2
            elif counter == 1:
                x = 9
                y = 12
            elif counter == 2:
                x = 9
                y = 22
            elif counter == 3:
                x = 9
                y = 32
            elif counter == 4:
                x = 9
                y = 42
            elif counter == 5:
                x = 9
                y = 52
            draw.text((x, y), text="X", font=font, fill="white")

            draw.text((5, 2), text="[ ] S4 Blue + Ant+", font=font, fill="white")  # back
            draw.text((5, 12), text="[ ] S4 Blue only", font=font, fill="white")  # radio (old icon: f145)
            draw.text((5, 22), text="[ ] S4 Ant+ only", font=font, fill="white")  # playlists
            draw.text((5, 32), text="[ ] SR Blue + Ant+", font=font, fill="white")  # shutdown
            draw.text((5, 42), text="[ ] SR Blue only", font=font, fill="white")  # shutdown
            draw.text((5, 52), text="[ ] SR Ant+ only", font=font, fill="white")  # shutdown
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