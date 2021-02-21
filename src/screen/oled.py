import threading
from time import sleep
import screens.mainmenu
import screens.pirowflosettings
import screens.buttonhelp
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


        #Send trigger event to active screen
        if globalParameters.trigger == True:
            globalParameters.trigger = False
            if globalParameters.activemenu == 0: screens.mainmenu.trigger()
            elif globalParameters.activemenu == 1: screens.pirowflosettings.trigger()
            elif globalParameters.activemenu == 2: screens.buttonhelp.trigger()


        sleep(0.2)
    except KeyboardInterrupt:
        print("Exiting...")
        break

updaterun.set() #Stop screen update procedure
shutdown()