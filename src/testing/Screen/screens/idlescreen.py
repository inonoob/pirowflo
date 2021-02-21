# from PIL import ImageFont
# from luma.core.render import canvas
# import helperFunctions
# import datetime
# from globalParameters import globalParameters
#
# # assign inital values to variables
# text_name = ""
# text_position = 0
# text_print = ""
# playbackState = ""
#
#
# # IDLE screen with clock and current playing song (screenid: 0)
# def draw(device):
#     global playbackState, playingInfo, text_name, text_position, text_print
#     clockfont = ImageFont.truetype(globalParameters.font_clock, size=30)
#     font = ImageFont.truetype(globalParameters.font_text, size=12)
#     text  = ImageFont.truetype(globalParameters.font_icons, size=12)
#     text big = ImageFont.truetype(globalParameters.font_icons, size=22)
#     counter = globalParameters.counter
#     now = datetime.datetime.now()
#     refresh_time = now.strftime("%H:%M:%S")
#
#     # runs every second (animations)
#     if refresh_time != globalParameters.today_last_time:
#         globalParameters.today_last_time = refresh_time
#         # Rolling text for currently playing song
#         if text_name != "":
#             text_print = text_name + "        " + text_name  # 8 spaces to create a nicer text flow
#             if text_position < len(text_name) + 8:
#                 text_position += 1
#             else:
#                 text_position = 0
#
#     # Show all the data on the screen
#     with canvas(device) as draw:
#         # Current time
#         draw.text((50, -10), now.strftime("%H:%M"), font=clockfont, fill="white")
#
#         # Currently playing song
#         if text_print != "":
#             draw.text((0, 27), text="\uf001", font=text , fill="white")  # music icon
#             draw.text((12, 29), text_print[text_position:], font=font, fill="white")
#
#         # Current music source and supported control buttons
#         if mediaVariables.loadedPlaylist == "[Radio Streams]":
#             controlElements = 1
#             draw.text((3, 0), text="\uf519", font=text big, fill="white")
#         elif mediaVariables.loadedPlaylist == "[AirPlay]":
#             controlElements = 0
#             draw.text((3, 0), text="\uf179", font=text big, fill="white")
#         else:
#             controlElements = 3
#             draw.text((3, 0), text="\uf1c7", font=text big, fill="white")
#
#         # Runs when rotary encoder is turned
#         if counter != globalParameters.oldcounter and counter <= controlElements and counter >= 0:
#             # Selection rectangle
#             if counter > 0:
#                 x = 34 + (counter - 1) * 20
#             else:
#                 x = 0
#             y = 48
#             draw.rectangle((x, y, x + 16, y + 15), outline=255, fill=0)
#             # Buttons
#             draw.text((2, y + 1), text="tes1", font=text , fill="white")  # menu
#             if controlElements >= 1:
#                 if playbackState == "play":
#                     draw.text((38, y), text="test2", font=text , fill="white")  # pause
#                 else:
#                     draw.text((38, y), text="test3", font=text , fill="white")  # play
#             if controlElements == 3:
#                 draw.text((57, y + 1), text="test4", font=text , fill="white")  # previous
#                 draw.text((78, y + 1), text="test5", font=text , fill="white")  # next
#         # Keep the cursor in the screen
#         if counter > controlElements: globalParameters.counter = 0
#         if counter < 0: globalParameters.counter = 0
#
#
# # Runs when button is pressed
# def trigger():
#     global playbackState
#     counter = globalParameters.counter
#     if counter == 0:
#         globalParameters.setScreen(1)
#     # elif counter == 1:
#     #     if playbackState == "play":
#     #         helperFunctions.playbackControl("pause")
#     #     else:
#     #         helperFunctions.playbackControl("play")
#     # elif counter == 2:
#     #     helperFunctions.playbackControl("previous")
#     # elif counter == 3:
#     #     helperFunctions.playbackControl("next")
#
#
# # Main data gathering, running in separate thread
# def update(stopEvent):
#     global text_name, text_position, text_print, text_position
#     global playbackState, playingInfo, text_name
#
#     while not stopEvent.is_set():
#         # if mediaVariables.loadedPlaylist != "[AirPlay]":
#         #     # Current playback state
#         #     try:
#         #         playbackInfo = helperFunctions.client.status()
#         #         playbackState = playbackInfo["state"]
#         #     except:
#         #         # connection lost -> restart
#         #         playbackInfo = {'state': 'play'}
#         #         establishConnection()
#         #
#         #     # Currently playing song name
#         #     try:
#         #         playingInfo = helperFunctions.client.currentsong()
#         #     except:
#         #         # connection lost -> restart
#         #         playingInfo = {'title': 'Could not load name!'}
#         #         establishConnection()
#         #     if playingInfo != {}:
#         #         currentSong = playingInfo["title"]
#         #         if currentSong != text_name:
#         #             text_name = currentSong
#         #             text_position = 0
#         # else:
#         #     # Get Airplay Info
#         #     info = mediaVariables.airplayinfo
#         #     if 'songartist' in info and 'itemname' in info:
#         #         text_name = info['songartist'] + " - " + info['itemname']
#         #     elif 'itemname' in info:
#         #         text_name = info['itemname']
#         #     else:
#         #         text_name = "AirPlay Streaming"
#
#         stopEvent.wait(20)