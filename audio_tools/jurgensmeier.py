#using python 2.7
#example animal sounds from http://www.wavsource.com/animals/animals.htm
    #note that those sounds have lots of different sampling rates and encoding types.  Causes problems.
#required installs:
    #numpy
    #scipy
    #matplotlib
    #pyaudio        -sudo apt-get install python-pyaudio
    #pydub:         -pip install pydub


def example():
    "example sounds and random inputs"
    sExampleSoundsDir = "/home/roman/All/Code/sound_files"
    sExampleFile1 = 'bird.wav'
    sExampleFile2 = 'frog.wav'
    oJ = Jurgenmeister(sExampleSoundsDir)
    
    #load audio into numpy array
    dSound1 = oJ.audio2array(sExampleFile1)
    dSound2 = oJ.audio2array(sExampleFile2)
    
    #Simply adding the arrays is noisy...
    dResSound1 = oJ.resample(dSound1)
    dResSound2 = oJ.resample(dSound2)
    dJoined = oJ.add_sounds(dResSound1, dResSound2)
    
    #pydub method
    oJ.overlay_sounds(sExampleFile1, sExampleFile2)
    
    #listen to the audio - mixed success with these sounds.
    oJ.play_array(dSound1)
    oJ.play_array(dSound2)
    oJ.play_array(dResSound1)
    oJ.play_array(dResSound2)
    oJ.play_array(dJoined)
    
    #see what the waveform looks like
    oJ.plot_audio(dJoined)




class Jurgenmeister:
    """
    Methods to play as many sounds on command as necessary
    Named in honour of op, and its as good a name as I can come up with myself.
    """
    
    def __init__(self, sSoundsDir):
        import os
        import random
        lAllSounds = os.listdir(sSoundsDir)
        self.sSoundsDir = sSoundsDir
        self.lAllSounds = lAllSounds
        self.sRandSoundName = lAllSounds[random.randint(0, len(lAllSounds)-1)]
    
    
    
    def play_wave(self, sFileName):
        """PyAudio play a wave file."""
        
        import pyaudio
        import wave
        iChunk = 1024
        sDir = "{}/{}".format(self.sSoundsDir, sFileName)
        oWave = wave.open(sDir, 'rb')
        oPyaudio = pyaudio.PyAudio()
        
        oStream = oPyaudio.open(
            format = oPyaudio.get_format_from_width(oWave.getsampwidth()),
            channels = oWave.getnchannels(),
            rate = oWave.getframerate(),
            output = True
        )
        
        sData = oWave.readframes(iChunk)
        while sData != '':
            oStream.write(sData)
            sData = oWave.readframes(iChunk)
        
        oStream.stop_stream()
        oStream.close()
        oPyaudio.terminate()
    

    
    def audio2array(self, sFileName):
        """
        Returns monotone data for a wav audio file in form:  
            iSampleRate, aNumpySignalArray, aNumpyTimeArray
            
            Should perhaps do this with scipy again, but I threw that code away because I wanted 
            to try the pyaudio package because of its streaming functions.  They defeated me.
        """
        import wave
        import numpy as np

        sDir = "{}/{}".format(self.sSoundsDir, sFileName)
        oWave = wave.open(sDir,"rb")
        tParams = oWave.getparams()
        iSampleRate = tParams[2]   #frames per second
        iLen = tParams[3]  # number of frames
        
        #depending on the type of encoding of the file.  Usually 16
        try:
            sSound = oWave.readframes(iLen)
            oWave.close()
            
            aSound = np.fromstring(sSound, np.int16)
        except ValueError:
            raise ValueError("""wave package seems to want all wav incodings to be in int16, else it throws a mysterious error.
                Short way around it:  find audio encoded in the right format.  Or use scipy.io.wavfile.
                """)
        
        aTime = np.array( [float(i)/iSampleRate for i in range(len(aSound))] )
        
        dRet = {
            'iSampleRate': iSampleRate, 
            'aTime': aTime, 
            'aSound': aSound,
            'tParams': tParams
        }
        
        return dRet
    
    
    
    def resample(self, dSound, iResampleRate=11025):
            """resample audio arrays
            common audio sample rates are 44100, 22050, 11025, 8000
            
            #creates very noisy results sometimes.
            """
            from scipy import interpolate
            import numpy as np
            aSound = np.array(dSound['aSound'])
            
            iOldRate = dSound['iSampleRate']
            iOldLen = len(aSound)
            rPeriod = float(iOldLen)/iOldRate
            iNewLen = int(rPeriod*iResampleRate)
            
            aTime = np.arange(0, rPeriod, 1.0/iOldRate)
            aTime = aTime[0:iOldLen]
            oInterp = interpolate.interp1d(aTime, aSound)
            
            aResTime = np.arange(0, aTime[-1], 1.0/iResampleRate)
            aTime = aTime[0:iNewLen]
            
            aResSound = oInterp(aResTime)
            aResSound = np.array(aResSound, np.int16)
            
            tParams = list(x for x in dSound['tParams'])
            tParams[2] = iResampleRate
            tParams[3] = iNewLen
            tParams = tuple(tParams)
            
            dResSound = {
                'iSampleRate': iResampleRate, 
                'aTime': aResTime, 
                'aSound': aResSound,
                'tParams': tParams
            }
            
            return dResSound
    
    
    
    def add_sounds(self, dSound1, dSound2):
        """join two sounds together and return new array
        This method creates a lot of clipping.  Not sure how to get around that.
        """
        if dSound1['iSampleRate'] != dSound2['iSampleRate']:
            raise ValueError('sample rates must be the same.  Please resample first.')
        
        import numpy as np
        
        aSound1 = dSound1['aSound']
        aSound2 = dSound2['aSound']
        
        if len(aSound1) < len(aSound2):
            aRet = aSound2.copy()
            aRet[:len(aSound1)] += aSound1
            aTime = dSound2['aTime']
            tParams = dSound2['tParams']
        else:
            aRet = aSound1.copy()
            aRet[:len(aSound2)] += aSound2
            aTime = dSound1['aTime']
            tParams = dSound1['tParams']
        
        
        aRet = np.array(aRet, np.int16)
        
        dRet = {
            'iSampleRate': dSound1['iSampleRate'], 
            'aTime': aTime,
            'aSound': aRet,
            'tParams': tParams
        }
        
        return dRet
    
    
    
    def overlay_sounds(self, sFileName1, sFileName2):
        "I think this method warrants a bit more exploration
        Also very noisy."
        from pydub import AudioSegment
        
        sDir1 = "{}/{}".format(self.sSoundsDir, sFileName1)
        sDir2 = "{}/{}".format(self.sSoundsDir, sFileName2)
        
        sound1 = AudioSegment.from_wav(sDir1)
        sound2 = AudioSegment.from_wav(sDir2)
        
        # mix sound2 with sound1, starting at 0ms into sound1)
        output = sound1.overlay(sound2, position=0)
        
        # save the result
        sDir = "{}/{}".format(self.sSoundsDir, 'OUTPUT.wav')
        output.export(sDir, format="wav")
    
    
    
    def array2audio(self, dSound, sDir=None):
        """
        writes an .wav audio file to disk from an array
        """
        import struct
        import wave
        if sDir ==  None:
            sDir = "{}/{}".format(self.sSoundsDir, 'OUTPUT.wav')
        
        aSound = dSound['aSound']
        tParams = dSound['tParams']
        sSound = struct.pack('h'*len(aSound), *aSound)
        
        oWave = wave.open(sDir,"wb")
        oWave.setparams(tParams)
        oWave.writeframes(sSound)
        oWave.close()
    
    
    
    def play_array(self, dSound):
        """Tried to use use pyaudio to play array by just streaming it.  It didn't behave, and I moved on.
        I'm just not getting the pyaudio stream to play without weird distortion 
        when not loading from file.  Perhaps you have more luck.
        """
        self.array2audio(dSound)
        self.play_wave('OUTPUT.wav')
    
    
    
    def plot_audio(self, dSound):
        "just plots the audio array.  Nice to see plots when things are going wrong."
        import matplotlib.pyplot as plt
        plt.plot(dSound['aTime'], dSound['aSound'])
        plt.show()
    
    
    

if __name__ == "__main__":
    example()
