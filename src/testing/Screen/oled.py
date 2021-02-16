import threading
from time import sleep
import helperFunctions
import screens.mainmenu
import screens.pirowflosettings
from globalParameters import globalParameters
from setupHandler import device, shutdown

updaterun = threading.Event()

while True:
    try:
        sleep(0.2)

        if globalParameters.activemenu == 0:
            screens.mainmenu.draw(device)

        elif globalParameters.activemenu == 1:
            screens.pirowflosettings.draw(device)

        elif globalParameters.activemenu == 2:
            screens.buttonhelp.draw(device)


        # # elif globalParameters.activemenu == 4: screens.playlistmenu.draw(device)
        # elif globalParameters.activemenu == 2:
        #     screens.emptyscreen.draw(device)
        #     print("third menu")

        # # elif globalParameters.activemenu == 4: screens.playlistmenu.draw(device)
        # elif globalParameters.activemenu == 3:
        #     screens.emptyscreen.draw(device)
        #     print("third menu")

        #Send trigger event to active screen
        if globalParameters.trigger == True:
            globalParameters.trigger = False
            #if globalParameters.activemenu == 0: screens.idlescreen.trigger()
            if globalParameters.activemenu ==
            elif globalParameters.activemenu == 1: screens.pirowflosettings.trigger()
            elif globalParameters.activemenu == 2: screens.buttonhelp.trigger()

            # elif globalParameters.activemenu == 4: screens.playlistmenu.trigger()
            #elif globalParameters.activemenu == 2: screens.emptyscreen.trigger(device) #Needs device to turn on screen

        # #Run update procedure in separate thread
        # if globalParameters.activemenu != globalParameters.oldactivemenu:
        #     globalParameters.oldactivemenu = globalParameters.activemenu
        #     updaterun.set()
        #     if globalParameters.activemenu == 0:
        #         updaterun.clear()
        #         updateThread = threading.Thread(target=screens.idlescreen.update, args=(updaterun,))
        #         updateThread.start()

        sleep(0.2)
    except KeyboardInterrupt:
        print("Exiting...")
        break

updaterun.set() #Stop screen update procedure
shutdown()