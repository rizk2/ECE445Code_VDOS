from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import asyncio as aio
import bleak as ble

# Create a API router for BLE-related endpoints
router = APIRouter()

# Define a global variable to store the device client
connected_client = None
notification_uuid = "0000fe42-8e22-4541-9d4c-21edae82ed19"

# Create an endpoint for connecting to a Bluetooth device
class Device(BaseModel):
    address: str


# Create an endpoint for Bluetooth discovery
@router.get("/scan-bluetooth")
async def discover_devices():
    try:
        all_devices = await ble.BleakScanner.discover(timeout=5.0)
        devices = []
        for device in all_devices:
            if device.name is not None:
                devices.append({
                    "name": device.name,
                    "address": device.address
                })
        return {"devices": devices}
    except Exception as e:
        return {"error": str(e)}


# Create an endpoint for connecting to a Bluetooth device
@router.post("/connect-device")
async def connect_device(device: Device):
    print(f'Printing device address: {device.address}')
    global connected_client
    try:
        print(f"Connective to device with address: {device.address}")
        client = ble.BleakClient(device.address)
        try:
            # Attempt to connect to the device
            await client.connect()
            if client.is_connected:
                print(f"Successfully connected to {device.address}.")
                print("Listing available services and characteristics:")
                
                # Store the information about services and characteristics into an array
                services_info = []
                for service in client.services:
                    service_info = {
                        "service_uuid": str(service.uuid),
                        "characteristics": [
                            {
                                "uuid": str(characteristic.uuid),
                                "properties": characteristic.properties,
                            }
                            for characteristic in service.characteristics
                        ],
                    }
                    services_info.append(service_info)
                
                # Get the negotiated MTU size
                mtu = client.mtu_size
                print(f"Negotiated MTU size: {mtu}")
                
                # Store the client globally for further use
                connected_client = client
                
                # Return connection details to the frontend
                return {
                    "message": f"Successfully connected to {device.address}.",
                    "services": services_info,
                    "mtu_size": mtu,
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create an endpoint for disconnecting from a Bluetooth device
@router.post("/disconnect-device")
async def disconnect_device():
    global connected_client
    if connected_client is not None and connected_client.is_connected:
        try:
            await connected_client.disconnect()
            print("Successfully disconnected.")
            connected_client = None
            return {"message": "Successfully disconnected."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="No device is currently connected.")


async def subscribe_to_characteristic(notification_handler):
    global connected_client, notification_uuid
    try:
        if connected_client.is_connected():
            print(f"Subscribing to characteristic {notification_uuid}...")
            try:
                await connected_client.start_notify(notification_uuid, notification_handler)
                print(f"Subscribed to {notification_uuid}.")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to subscribe: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during subscription: {str(e)}")


async def unsubscribe_from_characteristic():
    global connected_client, notification_uuid
    try:
        if connected_client.is_connected():
            print(f"Unsubscribing from characteristic {notification_uuid}...")
            try:
                await connected_client.stop_notify(notification_uuid)
                print(f"Unsubscribed from {notification_uuid}.")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to unsubscribe: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during unsubscription: {str(e)}")