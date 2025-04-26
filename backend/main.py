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


app = FastAPI()
try:
    audio_data, samplefreq = sf.read("C:\\Users\\mrizk\\Downloads\\sentence.wav")
except:
    samplefreq = 8000
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

start_time = time.time()
#Fundamental Frequency / Pitch Calculation 
f0 = getPitch(audio_data, samplefreq)
timef0 = np.arange(len(f0))
end_time = time.time()

#print (start_time-end_time)

#SPL
start_time2 = time.time()
spls = getSPL(audio_data, samplefreq)
timespl = np.arange(len(spls))
end_time2 = time.time()

#print(start_time2-end_time2)
#print((start_time2-end_time2)/chunk_number)

plt.plot(f0)
plt.title('Frequency Plot')
plt.xlabel('Time')
plt.ylabel('Frequency')
#plt.show()

#Harmonic Spacing

#CPP Calculation 
 #Getting CPP for every 50 ms chunk
CPP_values = getCPP(audio_data, samplefreq, f0_min, f0_max)
timeCPP = np.arange(len(CPP_values))
#print(start_time3-end_time3)
#print((start_time3-end_time3)/number_chunks)

plt.plot(CPP_values)
plt.title('CPP_values')
plt.xlabel('TIme Chunk (50ms)')
plt.ylabel('Magnitude')
#plt.show()

@app.websocket("/ws") #protocol connect to
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global f0, timef0, spls, timespl, CPP_values, timeCPP, audio_data
    global audio_data_p
    
    data = { #to list 
        "f0": f0.tolist(), 
        "timef0": timef0.tolist(), 
        "spls": spls.tolist(), 
        "timespl": timespl.tolist(), 
        "CPP": CPP_values.tolist(),  
        "timeCPP": timeCPP.tolist(), 
    }
    await websocket.send_text(json.dumps(data))

    numBlocksDisplay = 1000
    while True:
        if (not np.array_equal(audio_data_p,audio_data)):
            #You only need to check if there is new audio data vs audio data p.
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
        audio_data = np.append(audio_data, sinewave)