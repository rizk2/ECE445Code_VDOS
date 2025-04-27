import bleak as ble
import numpy as np

async def discover_devices():
    print("Scanning for Bluetooth devices...")
    # discover devices
    devices = await ble.BleakScanner.discover()
    for device in devices:
        if device.name is not None:
            print(f"Device: {device.name} ({device.address})")

async def connect_device(device_address):
    print(f"Connecting to device at {device_address}...")
    client  = ble.BleakClient(device_address)
    try:
        await client.connect()
        if client.is_connected:
            print(f"Successfully connected to {device_address}.")
            print("Listing available services and characteristics:")
            
            # List all services and their characteristics
            for service in client.services:
                print(f"Service: {service.uuid}")
                for characteristic in service.characteristics:
                    print(f"  Characteristic: {characteristic.uuid} | Properties: {characteristic.properties}")
            return client  # Return the client pointer for further use
        else:
            print(f"Failed to connect to {device_address}.")
            return None
    except Exception as e:
        print(f"An error occurred while connecting: {e}")
        return None
    
async def disconnect_device(client):
    print(f"Attempting to disconnect from device at {client.address}...")
    try:
        if client.is_connected:
            await client.disconnect()
            print(f"Disconnected from {client.address}.")
        else:
            print(f"Device at {client.address} is not connected.")
    except Exception as e:
        print(f"An error occurred while disconnecting: {e}")