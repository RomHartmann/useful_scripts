

def run():
    import os
    sHerePath = os.getcwd()
    sExamplePath = "{}/economy_sample2.txt".format(sHerePath)

    oS = SpacyAnalasys(sExamplePath)

    lsEntKeywords = oS.get_keywords(3, 'entity')
    lsSpKeywords = oS.get_keywords(3, 'speech')
    print("-------", sExamplePath)
    print('entity keywords:  ', lsEntKeywords)
    print('parts of speech keywords', lsSpKeywords)


    
    
    





class SpacyAnalasys:
    """methods based on spaCy algorithm
    required packages:
        pip install numpy
        SpaCy
            https://spacy.io/
            pip install spacy
            python -m spacy.en.download
            need newest version of numpy
        pip install unidecode
    """
    
    def __init__(self, sPath):
        from spacy.en import English
        self.oNlp = English()
        self.sText = self.get_text(sPath)
        self.oDoc = self.process_text(self.sText)
    
    
    #-----Helper functions
    def remove_similar(self, lOrig):
        "take list input and return exact and subset excluded items and their counts"
        lOrig = sorted(lOrig, key=len, reverse=True)
        
        #check if a similar already exists in the new list
        def similar_exists(sItem, l):
            bExists = False
            for s in l:
                if sItem in s:
                    bExists = True
            return bExists
        
        #only add new to list if it does not alredy exist
        lUniq = []
        for s in lOrig:
            if s not in lUniq and similar_exists(s, lUniq)==False:
                lUniq.append(s)
        
        #count how many times similar exists in original
        lCount = []
        for sUniq in lUniq:
            lCount.append(0)
            for sOrig in lOrig:
                if sOrig in sUniq:
                    lCount[-1] += 1
        
        llUniq = list(zip(lUniq, lCount))
        return llUniq
    
    
    #-----Spacy functions
    def get_text(self, sPath):
        "unicode text from file"
        with open(sPath, 'r') as f:
            sText = f.read()
        sText = unicode(sText, "utf-8")
        return sText
    
    
    def process_text(self, sText):
        "loads nlp packages and inserts text.  Returns nlp object"
        oDoc = self.oNlp(sText)
        return oDoc
    
    
    def get_sentences(self):
        """
        list of sentences from self.sText
        lsSentences:  List of sentences in string form
        llSentences:  list of sentences comprised of list of entities
        """
        lsSentences = []
        llSentences = []
        for oSpan in self.oDoc.sents:
            sSent = ''.join(self.oDoc[i].string for i in range(oSpan.start, oSpan.end)).strip()
            lSent = [self.oDoc[i] for i in range(oSpan.start, oSpan.end)]
            lsSentences.append(sSent)
            llSentences.append(lSent)
        return lsSentences, llSentences
    
    
    def speech_tags(self, loWords):
        "returns list of speech tags (essentially words) given list of words"
        llTags = []
        for oToken in loWords:
            llTags.append([oToken.orth_, oToken.pos_])
        return llTags
    
    
    def speech_tag_elements(self, llTags, sType):
        "get list of words speech tag elements of certain sType given list of annotated speech tags"
        lRet = []
        sEnt = ''
        for i in range(len(llTags)-1):
            if llTags[i][1] == sType:
                sEnt += u' {}'.format(llTags[i][0])
            elif llTags[i][1] != sType and sEnt != '':
                lRet.append(sEnt.strip())
                sEnt = ''
        
        return lRet
    
    
    def get_entities(self, oText):
        """returns list of [entities + entity labels] for each word that is an entitiy.  
        Returns type Span
        oSpan.root = type(Token)"""
        loEnts = list(oText.ents)
        lsLabels = [o.label_ for o in loEnts]
        llEnts = [[loEnts[i].orth_, lsLabels[i]] for i in range(len(lsLabels)) ]
        return llEnts
    
    
    def get_similar_words(self, oWord, iMin=0, iMax=10):
        "get similar words by word vectors.  iMin/ iMax are indeces for the segment of most similar words"
        from numpy import dot
        from numpy.linalg import norm
        oCos = lambda v1, v2: dot(v1, v2) / (norm(v1) * norm(v2))
        loAllWords = [w for w in self.oNlp.vocab if w.has_vector]
        loAllWords.sort(key=lambda w: oCos(w.vector, oWord.vector))
        loAllWords.reverse()
        loSimilar = [w.orth_ for w in loAllWords[iMin:iMax]]
        
        return loSimilar
    
    def extract_subject(self, oText):
        "extract the subject and objects from the text."
        from subject_object_extraction import findSVOs
        return findSVOs(oText)
    
    
    def get_keywords(self, iKW, sType):
        """get keywords from the given labelled entities
        sType is either 'speech' or 'entity'
        """
        #get most common noun
        loText = [oWord for oWord in self.oDoc]
        llTags = self.speech_tags(loText)
        lNouns = []
        for i in range(len(llTags)):
            if llTags[i][1] == 'NOUN':
                lNouns.append(llTags[i][0].strip())
        llUniqueNouns = sorted(self.remove_similar(lNouns), key = lambda t: t[1], reverse=True)
        lsUniqueNouns = [l[0] for l in llUniqueNouns]
        
        def get_top_phrases(lsPhrases, iKW):
            "lsPhrases is nouns or entities, iKW number of keywords"
            lsKeywords = []
            for i in range(len(lsUniqueNouns)):
                #prevent repetition of constituent nouns
                for sKeyword in lsKeywords:
                    if lsUniqueNouns[i] in sKeyword:
                        i += 1
                sNoun = lsUniqueNouns[i]
                for sPhrase in lsPhrases:
                    if sNoun in sPhrase and sPhrase not in lsKeywords:  #prevent repetition of keyword phrases
                        lsKeywords.append(sPhrase)
                        break
                
                if len(lsKeywords) == iKW:
                    break
            return lsKeywords
                
                
        #gets top of every type of speech noun
        if sType == 'speech':
            #get the top 3 noun phrases that contain the most common unique nouns
            llNounPhrases = self.speech_tag_elements(llTags, 'NOUN')
            lsNounPhrases = [l[0] for l in sorted(self.remove_similar(llNounPhrases), key = lambda t: t[1], reverse=True)]
            lsKeywords = get_top_phrases(lsNounPhrases, iKW)
            
        #gets top of every type of entity
        elif sType == 'entity':
            llEnts = self.get_entities(self.oDoc)
            lsEnts = [l[0] for l in llEnts]
            lsKeywords = get_top_phrases(lsEnts, iKW)
            
        return lsKeywords

    





if __name__ == '__main__':
    
    run()
