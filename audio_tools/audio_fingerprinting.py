import warnings
import json
warnings.filterwarnings("ignore")

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer

dConfig = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "1qaz!QAZ", 
        "db": "dejavu"
    }
}

# create a Dejavu instance
oDjv = Dejavu(dConfig)




def fingerprint_dir(sDir, lsFormats):
    """Fingerprint all the mp3's in the directory we give it"""
    oDjv.fingerprint_directory(sDir, lsFormats)


def recognize_file(sFile):
    """Recognize audio from a file"""
    print "recognizing audio from file...."
    dSong = oDjv.recognize(FileRecognizer, sFile)
    print "From file we recognized: %s\n" % dSong
    
    #in bash: python dejavu.py --recognize file 'sFile'


def recognize_audio(iSecs):
    """Or recognize audio from your microphone for `iSecs` seconds"""
    print "recognizing audio from microphone for {0} seconds....".format(iSecs)
    
    dSong = oDjv.recognize(MicrophoneRecognizer, seconds=iSecs)
    
    if dSong is None:
        print "Nothing recognized -- did you play the song out loud so your mic could hear it?"
    else:
        print "From mic with %d seconds we recognized: %s\n" % (iSecs, dSong)
    
    
    #in bash: python dejavu.py --recognize mic 'iSecs'
    