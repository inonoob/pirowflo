from PIL import ImageFont # the pillow module to create the picture which are then drawn on the display by luma.core
from setupHandler import device # device defines the screen charateristics needed by luma.core to draw on it e.g sh1106 with spi connection
from globalParameters import globalParameters # those are the globalparameters e.g fonts
from subprocess import run # this is needed to run os commands from linux
from time import sleep
import threading
from luma.core.render import canvas # lib to draw on the screen

def drawMenu(draw, entries):
    counter = globalParameters.counter  # default is 0
    position = 0
    #Draw menu
    for i in range(len(entries)):
        x = 6
        y = 2+position*12
        #fontawesome = ImageFont.truetype(globalParameters.font_icons, size=10) # defines the font to use and the size create font object from file
        font = ImageFont.truetype(globalParameters.font_text, size=10) # defines the font to use and the size create font object from file
        draw.rectangle((x, y, x+120, y+12), outline=255, fill=0)
        if entries[i] == "Zurück":
            #draw.text((x+2, y+2), text="\uf053", font=fontawesome, fill="white")
            draw.text((x+12, y+1), "Zurück", font=font, fill="white")
        else:
            draw.text((x+2, y+1), entries[i], font=font, fill="white")
        position += 1

    #Draw entry selector
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")

def shutdownSystem():
    print("Shutting down system")
    device.cleanup()
    run(["sudo shutdown","-h","now"])
    exit()

# def playRadioStation(stationid):
#     print("Playing ID", stationid)
#     try:
#         client.play(stationid)
#     except:
#         print("Error playing the station!")
#         establishConnection()
#     globalParameters.setScreen(0)
#
# def playbackControl(command):
#     try:
#         if command == "pause": client.pause()
#         elif command == "previous": client.previous()
#         elif command == "next": client.next()
#         elif command == "play": client.play()
#         print("Playback:", command)
#     except:
#         print("Error changing the playback mode!")
#         establishConnection()
#     globalParameters.setScreen(0)
#
# def loadRadioStations():
#     try:
#         client.clear()
#         client.load("[Radio Streams]")
#         mediaVariables.loadedPlaylist = "[Radio Streams]"
#     except:
#         print("Error loading radio station playlist!")
#         establishConnection()
#
# def loadPlaylist(name):
#     try:
#         client.clear()
#         client.load(name)
#         client.shuffle()
#         mediaVariables.loadedPlaylist = name
#         print("Loaded and playing Playlist", name)
#         client.play()
#     except:
#         print("Error loading and playing Playlist", name)
#         establishConnection()
