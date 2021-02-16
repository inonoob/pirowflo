from PIL import ImageFont
from luma.core.render import canvas
from globalParameters import globalParameters

#Functions for startscreen
def draw(device):
    with canvas(device) as draw:
        font = ImageFont.truetype(globalParameters.font_text, size=12)
        # fontawesome = ImageFont.truetype(globalParameters.font_icons, size=35)

        draw.text((25, 3), text="Starting screen application...", font=font, fill="white")
        # draw.text((50, 25), text="\uf251", font=fontawesome, fill="white")