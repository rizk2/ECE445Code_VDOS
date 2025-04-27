import librosa 
import numpy as np 
import parselmouth 
import soundfile as sf 
import math
import matplotlib.pyplot as plt 
from fastapi import FastAPI, WebSocket 
import asyncio
import json
import time 
from audiohelpers import getPitch, rms_spl, getSPL, getCPP
from BLEhelpers import connect_device, disconnect_device
import bleak as ble
from contextlib import asynccontextmanager

samplefreq = 2e6/256.0 #This is the exact sample rate. 7812.5 Hz
chunk_size = 0.050 #Uniform throughout all of the measurements here
chunk_samples = int(chunk_size*samplefreq)

audio_data = np.array([])
audio_data_p = np.array([])
f0 = np.array([])
timef0 = np.array([])
spls = np.array([])
timespl = np.array([])
CPP_values = np.array([])
timeCPP = np.array([])

def notification_handler(sender, data):
    global audio_data
    new_data = np.frombuffer(data, dtype="<i1")
    audio_data = np.append(audio_data, new_data)

async def subscribe_to_notifications(client, characteristic_uuid):
    if client.is_connected:
        print(f"Subscribing to notifications for characteristic {characteristic_uuid}...")
        try:
            # Start notifications
            await client.start_notify(characteristic_uuid, notification_handler)
        except Exception as e:
            print(f"Failed to subscribe to notifications: {e}")
    else:
        print("Client is not connected.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    device_address = "15CA291A-FF53-3033-4BC8-5375134A3843"
    client = await connect_device(device_address)
    if client:
        # Perform operations with the connected client
        print("Client is ready for further operations.")
        
        # Example: List services
        for service in client.services:
            print(f"Service: {service.uuid}")
    else:
        print("Could not connect to the device.")
    characteristic_uuid = "0000fe42-8e22-4541-9d4c-21edae82ed19"  # Replace with the notification characteristic UUID
    await subscribe_to_notifications(client, characteristic_uuid)
    yield
    await disconnect_device(client) #Disconnect at end of lifespan

app = FastAPI(lifespan=lifespan)

male = True
#It is important to distinguish possible MIN/MAX for male and female. Implement later
if (male):
    f0_min = 50
    f0_max = 300
else :
    f0_min = 100
    f0_max = 400

@app.websocket("/ws") #protocol connect to
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global f0, timef0, spls, timespl, CPP_values, timeCPP, audio_data
    global audio_data_p

    numBlocksDisplay = 1000
    while True:
        if (len(audio_data) - len(audio_data_p) > chunk_samples):
            #You only need to check if there is more than one chunk of new audio data vs audio data p.
            # Analyze new audio data and append those to f0, CPP, and spl. 
            new_audio = audio_data[len(audio_data_p):]
            audio_data_p = audio_data.copy()
            f0 = np.append(f0, getPitch(new_audio, samplefreq))
            spls = np.append(spls, getSPL(new_audio, samplefreq))
            CPP_values = np.append(CPP_values, getCPP(new_audio, samplefreq, f0_min, f0_max))

            timef0 = np.arange(len(f0))
            timespl = np.arange(len(spls))
            timeCPP = np.arange(len(CPP_values))
            
            data = { #to list 
                "f0": f0[-numBlocksDisplay:].tolist(), 
                "timef0": timef0[-numBlocksDisplay:].tolist(),  
                "spls": spls[-numBlocksDisplay:].tolist(),
                "timespl": timespl[-numBlocksDisplay:].tolist(),
                "CPP": CPP_values[-numBlocksDisplay:].tolist(),   
                "timeCPP": timeCPP[-numBlocksDisplay:].tolist(),  
            }
            await websocket.send_text(json.dumps(data))
        #Wait one chunk
        await asyncio.sleep(chunk_size)