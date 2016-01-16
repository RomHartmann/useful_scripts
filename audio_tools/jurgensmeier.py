#Roman Hartmann
#example animal sounds from http://www.wavsource.com/animals/animals.htm
#required installs:
    #numpy
    #scipy
    #matplotlib
    #pyaudio        -sudo apt-get install python-pyaudio


def example():
    "example sounds and random inputs"
    sExampleSoundsDir = "/home/roman/All/Code/sound_files"
    sExampleFile1 = 'jaguar.wav'
    sExampleFile2 = 'frog.wav'
    oJ = Jurgenmeister(sExampleSoundsDir)

    #dSound1 = oJ.audio2array(sExampleFile1)
    dSound2 = oJ.audio2array(sExampleFile2)
    #oJ.plot_audio(dSound2)
    #oJ.play_wave(sExampleFile1)
    #oJ.play_wave(sExampleFile2)
    
    #first, resample both of them
    #dResSound1 = oJ.resample(dSound1)
    #dResSound2 = oJ.resample(dSound2)
    
    #oJ.array2audio(dResSound2)
    #oJ.plot_audio(dResSound2)
    #oJ.play_wave('OUTPUT.wav')
    
    #then join
    #oJ.join_sounds(dResSound1, dResSound2)
    
    oJ.play_array(dSound2)
    
    
    
    



class Jurgenmeister:
    """
    Methods to play as many sounds on command as necessary
    Named in honour of the guy who asked the question, and its as 
    good a name as I can come up with myself.
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
        
        stream = oPyaudio.open(
            format = oPyaudio.get_format_from_width(oWave.getsampwidth()),
            channels = oWave.getnchannels(),
            rate = oWave.getframerate(),
            output = True
        )
        
        sData = oWave.readframes(iChunk)
        while sData != '':
            stream.write(sData)
            sData = oWave.readframes(iChunk)
        
        stream.stop_stream()
        stream.close()
        oPyaudio.terminate()
    


    
    def audio2array(self, sFileName):
        """
        Returns monotone data for a wav audio file in form:  
            iSampleRate, aNumpySignalArray, aNumpyTimeArray
        """
        from scipy.io.wavfile import read
        import numpy as np
        
        sDir = "{}/{}".format(self.sSoundsDir, sFileName)
        iSampleRate, aSound = read(sDir)
        print "+++", aSound
        
        #make monotone if not already
        try:
            len(aSound[0])
            bLen = True
        except TypeError:
            bLen = False
        
        if bLen and len(aSound[0]) == 2:
            aSound = np.array([ int( ( float(l[0]) + float(l[1]) )/2 ) for l in aSound])
        else:
            aSound = np.array(aSound)
        
        aTime = np.array( [float(i)/iSampleRate for i in range(len(aSound))] )
        
        dRet = {
            'iSampleRate': iSampleRate, 
            'aTime': aTime, 
            'aSound': aSound
        }
        
        return dRet
    
    
    
    
    def resample(self, dSound, iResampleRate=11025):
            """resample audio arrays
            other comon audio sample rates are 44100, 22050
            """
            from scipy import interpolate
            import numpy as np
            aSound = dSound['aSound']
            iOldRate = dSound['iSampleRate']
            iLen = float(len(aSound))
            iEnd = iLen/iOldRate
            
            aX = np.arange(0, iEnd, 1.0/iOldRate)
            aX = aX[0:len(aSound)]
            oInterp = interpolate.interp1d(aX, aSound)
            
            aResTime = np.arange(0, iEnd, 1.0/iResampleRate)
            aResSound = oInterp(aResTime)
            
            dSound = {
                'iSampleRate': iResampleRate, 
                'aTime': aResTime, 
                'aSound': aResSound
            }
            
            return dSound
    
    
    
    def join_sounds(self, dSound1, dSound2):
        """join two sounds together and return new array"""
        pass
        
        
    
    def array2audio(self, dSound, sDir=None):
        """
        writes an .wav audio file to disk from an array
        """
        if sDir ==  None:
            sDir = "{}/{}".format(self.sSoundsDir, 'OUTPUT.wav')
        
        from scipy.io.wavfile import write
        import numpy as np
        
        aSound = np.int16([10*i for i in dSound['aSound'] ])
        print "---", aSound
        write(sDir, dSound['iSampleRate'], aSound)
        
    
    
    def play_array(self, dSound):
        "use pyaudio to play array"
        import struct
        import pyaudio
        aSound = dSound['aSound']
        sSound = struct.pack('h'*len(aSound), *aSound)
        
        
        
        #import wave
        #iChunk = 1024
        #sDir = "{}/{}".format(self.sSoundsDir, sFileName)
        #oWave = wave.open(sDir, 'rb')
        #oPyaudio = pyaudio.PyAudio()
        
        #stream = oPyaudio.open(
            #format = oPyaudio.get_format_from_width(oWave.getsampwidth()),
            #channels = oWave.getnchannels(),
            #rate = oWave.getframerate(),
            #output = True
        #)
        
        #sData = oWave.readframes(iChunk)
        #while sData != '':
            #stream.write(sData)
            #sData = oWave.readframes(iChunk)
        
        #stream.stop_stream()
        #stream.close()
        #oPyaudio.terminate()
        
        
        #import wave
        #w = wave.open("{}/OUTPUT.wav".format(self.sSoundsDir),"wb")
        #w.setparams(p)
        #w.writeframes(s)
        #w.close()
    
    
    
    
    def plot_audio(self, dSound):
        "just plots the audio array.  Nice to see plots when things are going wrong."
        import matplotlib.pyplot as plt
        plt.plot(dSound['aTime'], dSound['aSound'])
        plt.show()
    
    
    
    





    






if __name__ == "__main__":
    example()




#---------------------------
#get this error when I play pyaudio.  Still works, I just ignore.
#problem seems to be widespread:
#http://stackoverflow.com/questions/17137701/pyaudio-alsa-error-messages

#ALSA lib pcm_dsnoop.c:618:(snd_pcm_dsnoop_open) unable to open slave
#ALSA lib pcm_dmix.c:1022:(snd_pcm_dmix_open) unable to open slave
#ALSA lib pcm.c:2239:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
#ALSA lib pcm.c:2239:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.center_lfe
#ALSA lib pcm.c:2239:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.side
#bt_audio_service_open: connect() failed: Connection refused (111)
#bt_audio_service_open: connect() failed: Connection refused (111)
#bt_audio_service_open: connect() failed: Connection refused (111)
#bt_audio_service_open: connect() failed: Connection refused (111)
#ALSA lib pcm_dmix.c:1022:(snd_pcm_dmix_open) unable to open slave
#Cannot connect to server socket err = No such file or directory
#Cannot connect to server request channel
#jack server is not running or cannot be started


