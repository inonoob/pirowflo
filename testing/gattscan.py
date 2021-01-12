import time
import asyncio
import bleak

async def run():

    devices = await bleak.discover() # search for bluetooth le devices
    for d in devices:
        if d.name == "S4 COMMS PI":
            print("Smartrow found ")
            print(d.address)
            return d.address


async def stop():
    print("test stop")
    # if (client is not None and await client.is_connected()):
    #     if (notify_started):
    #         await client.stop_notify(CHARACTERISTIC_UUID_SR_VALUE)
    #         print("Notify stopped")
    #         notify_started = False
    #
    #     await client.disconnect()
    #
    # running = False

loop = asyncio.get_event_loop()
dev = None
while dev is None:
    print("No device found")
    dev = loop.run_until_complete(run())

print("broke out of the while loop")
loop.run_until_complete(stop())
