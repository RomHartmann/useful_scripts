
def record_wav(sFilename, iSecs):
    """PyAudio example: Record a few seconds of audio and save to a WAVE file."""
    
    import pyaudio
    import wave
    
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = iSecs
    WAVE_OUTPUT_FILENAME = "{0}".format(sFilename)
    
    p = pyaudio.PyAudio()
    
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    print("* recording")
    
    frames = []
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("* done recording")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()



def playback_wav(sFilename):
    import playback
    playback.play_wav(sFilename)
    

def play_wav(sFileName):
    """PyAudio Example: Play a WAVE file."""
    
    import pyaudio
    import wave
    
    
    CHUNK = 1024
    
    wf = wave.open(sFileName, 'rb')
    
    p = pyaudio.PyAudio()
    
    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )
    
    data = wf.readframes(CHUNK)
    
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)
    
    stream.stop_stream()
    stream.close()
    
    p.terminate()



def audio2array(sDir):
    """
    Returns monotone data for a wav audio file in form:  
        iSampleRate, aNumpySignalArray, aNumpyTimeArray
    
    """
    from scipy.io.wavfile import read
    import numpy as np
    
    lAudio = read(sDir)
    iSampleRate, aAudio = lAudio
    iSampleRate = float(iSampleRate)
    
    try:
        len(aAudio[0])
        bLen = True
    except TypeError:
        bLen = False
    
    #make monotone
    if bLen and len(aAudio[0]) == 2:
        aAudio = np.array([ (l[0]+l[1])/2 for l in aAudio])
    else:
        aAudio = np.array(aAudio)
    
    aTime = np.array( [float(i)/iSampleRate for i in range(len(aAudio))] )
    
    return iSampleRate, aAudio, aTime


def array2audio(sDir, iRate, aData):
    """
    writes an .wav audio file to disk from an array
    """
    from scipy.io.wavfile import write
    
    write(sDir, iRate, aData)
    


def play_array(aSignal):
    import playback
    iSampleRate = 44100
    sTestDir = '/home/roman/Critical_ID/aufi/recorded_samples/play_array.wav'
    array2audio(sTestDir, iSampleRate, aSignal)
    
    playback.play_wav(sTestDir)
    



