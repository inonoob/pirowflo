import time
import asyncio
import bleak

class smartrow():


    # Smartrow service
    SERVICE_UUID_SR = "00001234-0000-1000-8000-00805f9b34fb"

    # Smartrow charaterisitc which is Notifiy and read
    CHARACTERISTIC_UUID_SR_VALUE = "00001236-0000-1000-8000-00805f9b34fb"

    # Smartrow charateristic write no reply
    CHARACTERISTIC_UUID_SR_WRITE = "00001235-0000-1000-8000-00805f9b34fb"

    def __init__(self):
        self.smartrowdevice = None


    async def discover(self):

        devices = await bleak.discover() # search for bluetooth le devices
        for d in devices:
            if d.name == "S4 COMMS PI":
                print("Smartrow found ")
                print(d.address)
                self.smartrowdevice = d




    async def connect_to_device(self, loop):
        print("starting", self.smartrowdevice.address, "loop")
        async with bleak.BleakClient(self.smartrowdevice.address, timeout=5.0) as client:

            print("connect to", self.smartrowdevice.address)


    async def stop(self):
        print("test stop")
        # if (client is not None and await client.is_connected()):
        #     if (self.notify_started):
        #         await self.client.stop_notify(self.CHARACTERISTIC_UUID_SR_VALUE)
        #         print("Notify stopped")
        #         notify_started = False
        #
        #     await client.disconnect()

        running = False

def main():
    smartrower = smartrow()
    loop = asyncio.get_event_loop()
    smartrower.smartrowdevice = None
    while smartrower.smartrowdevice is None:
        print("No device found")
        dev = loop.run_until_complete(smartrower.discover())

    print("next step")
    loop.run_until_complete(smartrower.connect_to_device(loop))
    time.sleep(30)
    print("broke out of the while loop")
    loop.run_until_complete(smartrower.stop())


if __name__ == '__main__':
    main()
