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


app = FastAPI()
try:
    audio_file, samplefreq = sf.read("C:\\Users\\mrizk\\Downloads\\sentence.wav")
except:
    samplefreq = 8000
    audio_file = np.random.uniform(-1, 1, samplefreq)

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

start_time = time.time()
#Fundamental Frequency / Pitch Calculation 
sound = parselmouth.Sound(audio_file, samplefreq)
pitch = sound.to_pitch(chunk_size, 85, 255) # Autocorrelation, 50 ms time blocks
f0 = pitch.selected_array["frequency"]
end_time = time.time()

#print (start_time-end_time)

#SPL

start_time2 = time.time()
C = 50 #in dB. THis is what they used in Nudelman's code. Pretty sure this is just a calibration constant
time_length = len(audio_file) * (1/samplefreq)
chunk_number = math.floor(time_length/chunk_size)
chunk_num_datapoints = math.floor(len(audio_file)/chunk_number)
spls = np.empty(chunk_number)

def rms_spl(audio_bin, calibration):
    audio_rms = np.sqrt(np.mean(audio_bin**2))
    spl_bin = 20*np.log10(audio_rms/ (20 * 10**-5)) + calibration
    return spl_bin

for p in range(chunk_number):
    start = p * chunk_num_datapoints
    end = start + chunk_num_datapoints
    chunk_data_rms_spl = rms_spl(audio_file[start:end],30)
    spls[p] = chunk_data_rms_spl

end_time2 = time.time()

#print(start_time2-end_time2)
#print((start_time2-end_time2)/chunk_number)


#time F0 (in Blocks)
timef0 = np.zeros(len(f0))
timespl = timef0
for i in range (len(f0)):
    timef0[i] = i

plt.plot(f0)
plt.title('Frequency Plot')
plt.xlabel('Time')
plt.ylabel('Frequency')
#plt.show()

#Harmonic Spacing

#CPP Calculation 
 #Getting CPP for every 50 ms chunk
samples_per_cs = round(samplefreq*chunk_size)
number_chunks = len(audio_file) // samples_per_cs
CPP_values = np.empty(number_chunks)
for i in range (number_chunks):
    if (((i+1)* samples_per_cs + 1) <= len(audio_file)):
        start_time3 = time.time()
        start_point = i * samples_per_cs
        end_point = (i+1)* samples_per_cs 
        sample = audio_file[start_point:end_point]
        C = np.fft.fft(sample,2**13)
        C = abs(C)
        C = np.convolve(C, [0.5,1,0.5]) #Smoothing Filter
        for j in range (len(C)):
            if (C[j] == 0):
                C[j] = 1e-15
        C = np.log(C)
        C = np.fft.ifft(C)
        for j in range (len(C)):
            if (C[j] == 0):
                C[j] = 1e-15
        C = 20*np.log10(np.abs([x if x != 0 else 1e-15 for x in C]))
        tRange = [np.ceil(samplefreq/f0_max),np.floor(samplefreq/f0_min)+1]
        tRange = [int(tRange[0]),int(min(2**12,tRange[1]))]
        CRange = C[tRange[0]:tRange[1]]
        Cmax = max(CRange)
        CmaxIndex = np.argmax(CRange)
        R = np.column_stack((np.arange(len(CRange)), np.ones_like(CRange)))
        m, b = np.linalg.lstsq(R, CRange)[0]   
        Cbaseline = m*(CmaxIndex)+b
        P = Cmax - Cbaseline    
        CPP_values[i] = P
        end_time3 = time.time()
        print(end_time3-start_time3)
        #Nudelman
    else :
        start_point = i * samples_per_cs
        end_point = len(audio_file)
        sample = audio_file[start_point:end_point]
        C = np.fft.fft(sample,2**13)
        C = abs(C)
        C = np.convolve(C, [0.5,1,0.5]) #Smoothing Filter
        for j in range (len(C)):
            if (C[j] == 0):
                C[j] = 1e-15
        C = np.log(C)
        C = np.fft.ifft(C)
        for j in range (len(C)):
            if (C[j] == 0):
                C[j] = 1e-15
        C = 20*np.log10(np.abs([x if x != 0 else 1e-15 for x in C]))
        CPP_values[i] = np.max(C)
        tRange = [np.ceil(samplefreq/f0_max),np.floor(samplefreq/f0_min)+1]
        tRange = [int(tRange[0]),int(min(2**12,tRange[1]))]
        CRange = C[tRange[0]:tRange[1]]
        Cmax = max(CRange)
        CmaxIndex = np.argmax(CRange)       
        R = np.column_stack((np.arange(len(CRange)), np.ones_like(CRange)))
        m, b = np.linalg.lstsq(R, CRange)[0]    
        Cbaseline = m*(CmaxIndex)+b
        P = Cmax - Cbaseline   
        CPP_values[i] = P
timeCPP = np.zeros(len(CPP_values))
#print(start_time3-end_time3)
#print((start_time3-end_time3)/number_chunks)

for i in range (len(CPP_values)):
    timeCPP[i] = i
plt.plot(CPP_values)
plt.title('CPP_values')
plt.xlabel('TIme Chunk (50ms)')
plt.ylabel('Magnitude')
#plt.show()




@app.websocket("/ws") #protocol connect to
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = { #to list 
        "f0": f0.tolist(),  
        "timef0": timef0.tolist(),  
        "spls": spls.tolist(),
        "timespl": timespl.tolist(),
        "CPP": CPP_values.tolist(),   
        "timeCPP": timeCPP.tolist(),  
    }
    print("sent")
    await websocket.send_text(json.dumps(data))

    global f0p
    global CPPp_values 
'''
    while True: 
        if (not np.array_equal(f0,f0p) or not np.array_equal(CPP_values,CPPp_values)):
            f0p = f0.copy()
            CPPp_values = CPP_values.copy()
            data = { #to list 
                "f0": f0.tolist(),  
                "timef0": timef0.tolist(),  
                "CPP": CPP_values.tolist(),   
                "timeCPP": timeCPP.tolist(),  
            }
            await websocket.send_text(json.dumps(data))
            print("PLEASE PLEASE WORK ALREADY")
            
        await asyncio.sleep(1)
        await websocket.send_text(json.dumps(data))
        print("PLEASE PLEASE WORK ALREADY")
        await asyncio.sleep(1)
'''
    