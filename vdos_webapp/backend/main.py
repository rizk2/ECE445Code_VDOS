import librosa
import numpy as np
import parselmouth
import math
import json
import io
import soundfile as sf

import asyncio
import bleak as ble

from pydantic import BaseModel
from audio_helpers import getPitch, getSPL, getCPP
from ble_helpers import router as bluetooth_router
from ble_helpers import subscribe_to_characteristic, unsubscribe_from_characteristic

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()
live_websocket = None

# Define the global variables for audio data and parameters
samplefreq = 7812
audio_data = np.random.uniform(-1, 1, samplefreq)

audio_data_p = audio_data.copy()

male = True
#It is important to distinguish possible MIN/MAX for male and female. Implement later
if (male):
    f0_min = 50
    f0_max = 300
else :
    f0_min = 100
    f0_max = 400

f0p = None 
CPPp_values = None 
chunk_size = 0.050 #Uniform throughout all of the measurements here
chunk_samples = int(chunk_size*samplefreq)
f0 = getPitch(audio_data, samplefreq)
timef0 = np.arange(len(f0))
spls = getSPL(audio_data, samplefreq)
timespl = np.arange(len(spls))
CPP_values = np.array([getCPP(audio_data, samplefreq, f0_min, f0_max, 2**15)])
timeCPP = np.arange(len(CPP_values))
calibration_constant = 30.0



# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Bluetooth router / BLE endpoints
app.include_router(bluetooth_router)

live_transmission = False
# Set up a POST endpoint to start/stop live data transmission
class LiveControlRequest(BaseModel):
    live: bool

@app.post("/control-live_transmission")
async def control_live_transmission(request: LiveControlRequest):
    global live_transmission
    live_transmission = request.live
    if live_transmission:
        return {"message": "Backend live data transmission started..."}
    else:
        return {"message": "Backend live data transmission stopped..."}

@app.post("/set-calibration-constant")
async def set_calibration_constant(request: dict):
    global calibration_constant
    try:
        calibration_constant = request['calibration_constant']
        return {"message": f"Calibration constant set to {calibration_constant}."}
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing 'calibration_constant' in request body")
    
    
@app.post("/reset-audio-data")
async def reset_audio_data():
    global audio_data, audio_data_p, f0, timef0, spls, timespl, CPP_values, timeCPP
    audio_data = np.array([])
    audio_data_p = np.array([])
    f0 = np.array([])
    timef0 = np.array([])
    spls = np.array([])
    timespl = np.array([])
    CPP_values = np.array([])
    timeCPP = np.array([])
    
    return {"message": "Audio data reset successfully."}

@app.post("/download-audio-file")
async def download_audio_file():
    global audio_data, samplefreq
    try:
        # Validate audio data
        if audio_data.size == 0:
            raise HTTPException(status_code=400, detail="Audio data is empty")

        # Create an in-memory buffer to store the .wav file
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, samplefreq, format="WAV")
        buffer.seek(0)  # Reset the buffer's position to the beginning

        # Return the .wav file as a downloadable response
        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=audio_file.wav"}
        )
    except Exception as e:
        print(f"Error in download_audio_file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio file: {str(e)}")


MAX_AUDIO_DATA_SIZE = 8000
# Define a notification handler to process incoming audio data
async def notification_handler(sender, data):
    global audio_data, audio_data_p
    try:
        # Convert the received bytes to a NumPy array
        new_audio_data = np.frombuffer(data, dtype="<i1")  # Adjust dtype as needed
        audio_data = np.append(audio_data, new_audio_data)

        # Limit the size of the audio_data array
        """ if len(audio_data) > MAX_AUDIO_DATA_SIZE:
            audio_data = audio_data[-MAX_AUDIO_DATA_SIZE:] """

        print(f"Received new audio data: {new_audio_data}")

    except Exception as e:
        print(f"Error in notification handler: {e}")


def notification_handler_wrapper(sender, data):
    asyncio.create_task(notification_handler(sender, data))

# Set up a websocket endpoint for live data streaming
@app.websocket("/live-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global f0, timef0, spls, timespl, CPP_values, timeCPP, audio_data, calibration_constant
    global audio_data_p, live_transmission
    global live_websocket
    
    live_websocket = websocket
    numBlocksDisplay = 1000
    
    data = { #to list 
        "f0": f0[:numBlocksDisplay].tolist(), 
        "timef0": timef0[:numBlocksDisplay].tolist(), 
        "spls": spls[:numBlocksDisplay].tolist(), 
        "timespl": timespl[:numBlocksDisplay].tolist(), 
        "CPP": CPP_values[:numBlocksDisplay].tolist(),  
        "timeCPP": timeCPP[:numBlocksDisplay].tolist(), 
    }
    await live_websocket.send_text(json.dumps(data))

    print("Subscribing to BLE characteristic for audio data...")
    await subscribe_to_characteristic(notification_handler_wrapper)

    while live_transmission:
        await asyncio.sleep(chunk_size)
        print("Waiting for new audio data...")
        
        try:
            # Perform asynchronous operations (e.g., sending data over WebSocket)
            if len(audio_data) - len(audio_data_p) > chunk_samples:
                new_audio = audio_data[len(audio_data_p):]
                audio_data_p = audio_data.copy()
                f0 = np.append(f0, getPitch(new_audio, samplefreq))
                spls = np.append(spls, getSPL(new_audio, samplefreq, calibration=calibration_constant))
                CPP_values = np.append(CPP_values, np.array([getCPP(new_audio, samplefreq, f0_min, f0_max, 2**15)]))
                """ audio_data_p = audio_data.copy()
                f0 = np.append(f0, audio_data_p)
                spls = np.append(spls, audio_data_p)
                CPP_values = np.append(CPP_values, audio_data_p) """

                timef0 = np.arange(len(f0))
                timespl = np.arange(len(spls))
                timeCPP = np.arange(len(CPP_values))

                data = {
                    "f0": f0[-1000:].tolist(),
                    "timef0": timef0[-1000:].tolist(),
                    "spls": spls[-1000:].tolist(),
                    "timespl": timespl[-1000:].tolist(),
                    "CPP": CPP_values[-1000:].tolist(),
                    "timeCPP": timeCPP[-1000:].tolist(),
                }
                await live_websocket.send_text(json.dumps(data))  # Async operation
        except Exception as e:
            print(f"Error sending data over WebSocket: {e}")
        
    
    """ while live_transmission:
        if (not np.array_equal(audio_data_p,audio_data)):
            # You only need to check if there is new audio data vs audio data p.
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
        
        #Simulated audio data
        await asyncio.sleep(chunk_size)
        sinefreq = np.random.uniform(100, 400)
        sinewave = np.sin(np.arange(chunk_samples*30)/samplefreq*sinefreq*2*np.pi)
        audio_data = np.append(audio_data, sinewave) """
    
    print("Disconnecting from BLE characteristic...")
    await unsubscribe_from_characteristic()
    await live_websocket.close()
    live_websocket = None