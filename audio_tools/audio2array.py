def audio2array(sDir):
    """
    Returns monotone data for a wav audio file in form:  
        iSampleRate, aNumpySignalArray, aNumpyTimeArray
    """
    from scipy.io.wavfile import read
    import numpy as np
    
    iSampleRate, aAudio = read(sDir)
    iSampleRate = float(iSampleRate)
    
    #make monotone
    try:
        len(aAudio[0])
        bLen = True
    except TypeError:
        bLen = False
    
    
    if bLen and len(aAudio[0]) == 2:
        aAudio = np.array([ int( ( float(l[0]) + float(l[1]) )/2 ) for l in aAudio])
    else:
        aAudio = np.array(aAudio)
    
    aTime = np.array( [float(i)/iSampleRate for i in range(len(aAudio))] )
    
    
    return iSampleRate, aTime, aAudio