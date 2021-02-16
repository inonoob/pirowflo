from luma.core.render import canvas
from globalParameters import globalParameters


# display off (screenid: 5)
def draw(device):
    if globalParameters.blackscreen == False:
        globalParameters.blackscreen = True
        device.clear()

        # can be different depending on the type of display, look at the luma.oled api documentation
        device.hide()


def trigger(device):
    globalParameters.blackscreen = False
    device.show()
    globalParameters.setScreen(0)