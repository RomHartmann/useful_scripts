
def audio_to_phonemes(sDir, sType='phoneme', bClean = True):
    """
    turn a digital signal into a list of audio_to_phonemes
        sType ['phoneme' or 'word']:  return a list of phonemes or words
        bClean removes silences and other non phonemes
    """
    
    
    from os import environ, path
    
    from pocketsphinx.pocketsphinx import *
    from sphinxbase.sphinxbase import *
    
    MODELDIR = "pocketsphinx/model"
    DATADIR = "pocketsphinx/test/data"
    
    # Create a decoder with certain model
    oConfig = Decoder.default_config()
    oConfig.set_string('-logfn', '/dev/null')   #removes stdout logs
    oConfig.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
    
    if sType == 'phoneme':
        oConfig.set_string('-allphone', path.join(MODELDIR, 'en-us/en-us-phone.lm.dmp'))
        oConfig.set_float('-lw', 2.0)
        oConfig.set_float('-beam', 1e-10)
        oConfig.set_float('-pbeam', 1e-10)
    
    elif sType == 'word':
        oConfig.set_string('-lm', path.join(MODELDIR, 'en-us/en-us.lm.dmp'))
        oConfig.set_string('-dict', path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
    else:
        return 'ERROR:  Please chose sType between "phoneme" and "word"'
    
    
    
    # Decode streaming data.
    oDecoder = Decoder(oConfig)
    

    oDecoder.start_utt()
    stream = open(path.join(DATADIR, 'goforward.raw'), 'rb')
    stream = open(sDir, 'rb')
    while True:
        buf = stream.read(1024)
        if buf:
            oDecoder.process_raw(buf, False, False)
        else:
            break
    oDecoder.end_utt()

    lRet = [seg.word for seg in oDecoder.seg()]
    
    if bClean:
        if sType == 'phoneme':
            lRet = [s for s in lRet if s != 'SIL' and s!='+SPN+' and s!='+NSN+']
        elif sType == 'word':
            lRet = [s for s in lRet if s != '<s>' and s!= '</s>' and s!='<sil>' and s!='[SPEECH]']
    
    
    return lRet


