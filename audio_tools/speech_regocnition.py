

def speach_recog_mic():
    """
    speech to text
        https://github.com/Uberi/speech_recognition
    """
    
    import speech_recognition as sr
    oR = sr.Recognizer()
    with sr.Microphone() as source:                # use the default microphone as the audio source
        audio = oR.listen(source)                   # listen for the first phrase and extract it into audio data

    try:
        print("You said " + oR.recognize(audio))    # recognize speech using Google Speech Recognition
    except LookupError:                            # speech is unintelligible
        print("Could not understand audio")
    



def speach_recog_from_file(sDir):
    """
    audio file .wav to text
    """
    import speech_recognition as sr
    r = sr.Recognizer()
    
    with sr.WavFile(sDir) as source:                    # use sDir as the audio source
        audio = r.record(source)                        # extract audio data from the file

    try:
        list = r.recognize(audio,True)                  # generate a list of possible transcriptions
        print("Possible transcriptions:")
        for prediction in list:
            print(" " + prediction["text"] + " (" + str(prediction["confidence"]*100) + "%)")
    except LookupError:                                 # speech is unintelligible
        print("Could not understand audio")
    
