import librosa 
import numpy as np 
import parselmouth 
import soundfile as sf 
import math

chunk_size = 0.05
def getPitch(audio_data, samplefreq):
    sound = parselmouth.Sound(audio_data, samplefreq)
    pitch = sound.to_pitch(chunk_size, 85, 255) # Autocorrelation, 50 ms time blocks
    return pitch.selected_array["frequency"]

def rms_spl(audio_bin, calibration):
    audio_rms = np.sqrt(np.mean(audio_bin**2))
    spl_bin = 20*np.log10(audio_rms/ (20 * 10**-5)) + calibration
    return spl_bin

def getSPL(audio_data, samplefreq):
    C = 50 #in dB. THis is what they used in Nudelman's code. Pretty sure this is just a calibration constant
    time_length = len(audio_data) * (1/samplefreq)
    chunk_number = math.floor(time_length/chunk_size)
    chunk_num_datapoints = math.floor(len(audio_data)/chunk_number)
    spls = np.empty(chunk_number)

    for p in range(chunk_number):
        start = p * chunk_num_datapoints
        end = start + chunk_num_datapoints
        chunk_data_rms_spl = rms_spl(audio_data[start:end],30)
        spls[p] = chunk_data_rms_spl
    return spls

def getCPP(x, Fs, f0min, f0max, fft_size):
    '''
    *Credits to Mark Skowronski for developing the original function in matlab.
    This function calculates cepstral peak prominence (CPP) according to Hillenbrand et al. (1994).
    
    Parameters:
        x : np.ndarray
            Input audio signal
        Fs : int
            Sampling rate of x
        f0min : int
            Minimum frequency to search for cepstral peak
        f0max : int
            Maximum frequency to search for cepstral peak
    Returns:
        P : float
            Cepstral peak prominence value in dB

    Reference:
    Hillenbrand, Cleveland, and Erickson, "Acoustic Correlates of Breathy Vocal Quality," JSHR, vol.
    37, pp. 769-778, Aug. 1994    
    '''
    Xabs = np.abs(np.fft.fft(x, fft_size))  # spectrum magnitude
    
    Hsmooth = [0.5, 1, 0.5]
    Xabs = np.convolve(Xabs, Hsmooth, 'same')   # smooth spectrum

    X = np.log(Xabs)    # log spectrum

    X = X-X.mean()  # zero mean

    c = np.fft.ifft(X)  # real cepstrum

    C = 20*np.log10(np.abs([x if x != 0 else 1e-15 for x in c]))

    # Determine limits over which to search for peak in C and to perform cepstral baseline regression
    tRange = [np.ceil(Fs/f0max),np.floor(Fs/f0min)+1]
    tRange = [int(tRange[0]),int(min(fft_size/2,tRange[1]))]

    CRange = C[tRange[0]:tRange[1]]

    Cmax = max(CRange)
    CmaxIndex = np.argmax(CRange)
    
    # Find regression of C in tRange
    R = np.column_stack((np.arange(len(CRange)), np.ones_like(CRange)))
    m, b = np.linalg.lstsq(R, CRange)[0]    # m = slope, b = y-intercept
    
    Cbaseline = m*(CmaxIndex)+b
    P = Cmax - Cbaseline    # normalize with baseline value
 
    return P


""" def getCPP(audio_data, samplefreq, f0_min, f0_max):
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
    return CPP_values """