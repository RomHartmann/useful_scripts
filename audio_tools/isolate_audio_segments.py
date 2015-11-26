def isolate_audio_segemnts(sDir, iResample = 8000, iSigmaSecs=0.05):
    """
    expected peak corrolation by convolution, then edge detection
    iResample = 8000 Hz resampling rate
        Hard coded variables obtained by trial:
            linerar smoothing coefficient:  iLinearSmooth = 20 frames
            minima threshhold factor:  iThreshFact = 10 times
            horozontal cluster threshhold:  iThreshCluster = 0.01 seconds * iSampleRate
            keep sections threshhold factor:  iThreshKeepFact = 5
    can save each cut to separate file 
    returns list of cuts, each cut is peak data (correlation with gaussian)
    """
    
    import numpy as np
    
    iLinearSmooth = 50
    
    (iSampleRate, 
        aTime, 
        aAudio, 
        aCorr,
        aOrigAudio) = process_dir(sDir, iSmooth=iLinearSmooth, iResample=iResample, iSigmaSecs=iSigmaSecs)
    
    
    iThreshFact = 5.0
    iThreshClusterSecs = 0.01
    iThreshCluster = iThreshClusterSecs * iSampleRate
    iThreshKeepFact = 4.0
    
    
    from scipy import ndimage
    aFirstDeriv = ndimage.sobel(aCorr)
    
    
    aFirstDeriv = smooth(aFirstDeriv, iLinearSmooth)
    aSecondDeriv = ndimage.sobel(aFirstDeriv)
    
    
    #---Get minima and filter
    #intersecion of derivative with zero line (get maxima and minima)
    aZero = np.zeros(np.shape(aSecondDeriv))
    iTolerance = 10.0        #tolerance to zero-intersect
    aZeroIntersect = np.argwhere(np.isclose(aZero, aFirstDeriv, atol=iTolerance)).reshape(-1)
    
    #positive second derivitave (get minima)
    aMinimaIndeces = np.array([ i for i in aZeroIntersect if aSecondDeriv[i] > 0 ])
    
    
    #apply threshold filter for minima (y axis filter)
    iMax = np.max(aCorr)
    iMin = np.min(aCorr)
    iAmplThresh = (iMax - iMin)/iThreshFact      #we only want to keep low minima
    aMinimaIndeces = np.array( [i for i in aMinimaIndeces if aCorr[i] < iAmplThresh] )
    
    
    #apply proximity filter to single out consecutive groups of minima
    lMinimaIndeces = []
    for i in range(len(aMinimaIndeces) - 1):
        if aMinimaIndeces[i+1] - aMinimaIndeces[i] > iThreshCluster:
            lMinimaIndeces.append(aMinimaIndeces[i])
    
    
    if len(aMinimaIndeces) >0:
        lMinimaIndeces.append(aMinimaIndeces[-1])
    
    
    lMinimaIndecesFilt = [int(i) for i in lMinimaIndeces]
    
    
    #add the beginning and end of the track
    lMinimaIndecesFilt.insert(0, 0)
    lMinimaIndecesFilt.insert(len(lMinimaIndecesFilt), int(len(aCorr)-1))
    
    
    #get time values from indeces
    aTimeIntersects = np.array(aTime)[lMinimaIndecesFilt]

    
    #cut up audio according to minima indeces
    iMin = 1
    iCut = 1
    
    laAudios = []
    laCorrs = []
    
    
    while iMin < len(lMinimaIndecesFilt):
        iStart = lMinimaIndecesFilt[iMin -1]
        iEnd = lMinimaIndecesFilt[iMin]
        

        aAudioCut = np.array(aAudio[iStart : iEnd])
        aCorrAudioCut = np.array(aCorr[iStart : iEnd])
        aOrigAudioCut = np.array(aOrigAudio[iStart : iEnd])
        
        if aCorrAudioCut.any():
            #keep only peaks with a minimum amplitude
            bKeep = (np.max(aCorrAudioCut) - np.min(aCorrAudioCut)) > np.max(aCorr)/iThreshKeepFact
        else:
            bKeep = False
        
        
        #throw away sections with max amplitude less than max/iThreshKeepFact
        if bKeep:
            laAudios.append(aAudioCut)
            laCorrs.append(aCorrAudioCut)
            
            iCut += 1
        
        iMin += 1
    
    
    
    return iSampleRate, laAudios, laCorrs

    


def process_dir(sDir, iResample=None, iSmooth = 50, iSigmaSecs=0.01):
    """
    take input dir and output smoothed, correlated array
    iSigmaSecs:  standard deviation of gaussian in seconds
    iSmooth = smoothing window size for linear smoother
    """
    from scipy import signal
    import numpy as np
    iSampleRate, aTime, aOrigAudio = audio2array(sDir, iResample)
    
    #only positive
    aAudio = [abs(i) for i in aOrigAudio]
    
    #audio files must be right format
    aOrigAudio = np.asarray(aOrigAudio, dtype=np.int16)
    
    if not iSmooth == None:
        #smooth
        aAudio = smooth(aAudio, iSmooth)
    
    #standard deviation for gaussian function
    iSigma = float(iSigmaSecs * iSampleRate)
    aGaussian = signal.gaussian(10*iSigma, iSigma)
    
    #gaussian correlated with audio signal
    aCorr = np.correlate(aAudio, aGaussian, 'same')
    
    
    return iSampleRate, aTime, aAudio, aCorr, aOrigAudio



def audio2array(sDir, iResample=None):
    """
    Returns monotone data for a wav audio file in form:  
        iSampleRate, aNumpySignalArray, aNumpyTimeArray
    iResample is the new resampling rate desired
    
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
    
    
    if iResample != None:
        aAudio = downsample(aAudio, iSampleRate, iResample)
        aTime = downsample(aTime, iSampleRate, iResample)
        iSampleRate = float(iResample)
    
    return iSampleRate, aTime, aAudio



def smooth(aSignal, iWindowSize):
    """
    smooth a signal by window size using kernel operator
    """
    import numpy as np
    aKernel = np.ones(int(iWindowSize))/float(iWindowSize)
    return np.convolve(aSignal, aKernel, 'same')







