#!/usr/bin/env python3
import datetime
import asyncio
import argparse
import sys

from bleak import BleakScanner
from bleak import BleakClient



class Smartrow():
    # Smartrow service
    SERVICE_UUID_SR = "00001234-0000-1000-8000-00805f9b34fb"

    # Smartrow charaterisitc which is Notifiy and read
    CHARACTERISTIC_UUID_SR_VALUE = "00001236-0000-1000-8000-00805f9b34fb"

    # Smartrow charateristic write no reply
    CHARACTERISTIC_UUID_SR_WRITE = "00001235-0000-1000-8000-00805f9b34fb"

    async def connect(self, loop):
        '''
        Connect to BLE server (light sensor)
        '''
        device = await self.select_server_device()
        print("Using device %s" % device.address)

        self.client = BleakClient(device.address, loop=loop)

        connected = await self.client.connect()

        self.light_status_handle = await self.get_light_status_handle()

        return connected

    async def run(self, loop):
        '''
        Start receiving notifications from BLE server
        '''
        self.running = True

        await self.client.start_notify(self.notification_handler)
        print("Notify started")
        self.notify_started=True

    async def get_light_status_handle(self):
        '''
        Get light status handle which is the only ID available in notification_handler
        '''
        svcs = await self.client.get_services()

        for service in svcs:
            for char in service.characteristics:
                if (char.uuid == self.LIGHTS_STATUS_UUID):
                    return char.handle

    async def stop(self):
        if (self.client is not None and await self.client.is_connected()):
            if (self.notify_started):
                await self.client.stop_notify(self.CHARACTERISTIC_UUID_SR_VALUE)
                print("Notify stopped")
                self.notify_started = False

            await self.client.disconnect()

        self.running = False

