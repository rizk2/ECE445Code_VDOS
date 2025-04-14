import asyncio
from bleak import BleakScanner, BleakClient

tracker = False

async def main():
    global tracker
    devices = await BleakScanner.discover(3.0, return_adv=True)
    for d in devices:
        if(devices[d][1].local_name == 'TestBLE'):
            print("Found the Device")
            BLE_Device = d
            tracker = True 
    if (not tracker):
        print("Device Not found")
    else: 
        address = BLE_Device
        async with BleakClient(address) as client:
            svcs = client.services
            print("AValible services:")
            for service in svcs:
                print(service)
asyncio.run(main())
