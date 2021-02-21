from PIL import ImageFont
from luma.core.render import canvas
from globalParameters import globalParameters

print(globalParameters.font_icons)
#Functions for startscreen
def draw(device):
    with canvas(device) as draw:
        font = ImageFont.truetype(globalParameters.font_text, size=12)
        # fontawesome = ImageFont.truetype(globalParameters.font_icons, size=35)

        draw.text((10, 3), text="Starting", font=font, fill="white")
        draw.text((10, 15), text="PiRowFlo Display", font=font, fill="white")
        draw.text((10, 25), text="please wait", font=font, fill="white")
        # draw.text((50, 25), text="\uf251", font=fontawesome, fill="white")