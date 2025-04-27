import librosa 
import numpy as np 
import parselmouth 
import soundfile as sf 
import math

chunk_size = 0.05
def getPitch(audio_data, samplefreq):
    sound = parselmouth.Sound(audio_data, samplefreq)
    pitch = sound.to_pitch(chunk_size, 50, 400) # Autocorrelation, 50 ms time blocks
    return pitch.selected_array["frequency"]

def rms_spl(audio_bin, calibration):
    audio_rms = np.sqrt(np.mean(audio_bin**2))
    spl_bin = 20*np.log10(audio_rms/ (20 * 10**-5)) + calibration
    return spl_bin

def getSPL(audio_data, samplefreq):
    C = 50 #in dB. THis is what they used in Nudelman's code. Pretty sure this is just a calibration constant
    C = 30
    time_length = len(audio_data) * (1/samplefreq)
    chunk_number = math.floor(time_length/chunk_size)
    chunk_num_datapoints = math.floor(len(audio_data)/chunk_number)
    spls = np.empty(chunk_number)

    for p in range(chunk_number):
        start = p * chunk_num_datapoints
        end = start + chunk_num_datapoints
        chunk_data_rms_spl = rms_spl(audio_data[start:end],C)
        spls[p] = chunk_data_rms_spl
    return spls

def getCPP(audio_data, samplefreq, f0_min, f0_max):
    samples_per_cs = round(samplefreq*chunk_size)
    number_chunks = len(audio_data) // samples_per_cs
    CPP_values = np.empty(number_chunks)
    for i in range (number_chunks):
        if (((i+1)* samples_per_cs + 1) <= len(audio_data)):
            start_point = i * samples_per_cs
            end_point = (i+1)* samples_per_cs 
            sample = audio_data[start_point:end_point]
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
            #Nudelman
        else :
            start_point = i * samples_per_cs
            end_point = len(audio_data)
            sample = audio_data[start_point:end_point]
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
    return CPP_values