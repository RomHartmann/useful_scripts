

def run():
    import os
    sHerePath = os.getcwd()
    sExamplePath = "{}/news_sample2.txt".format(sHerePath)

    oS = Sirakis(sExamplePath)

    print(sExamplePath)
    print(oS.keywords())

    #lsEntKeywords = oS.get_keywords(3, 'entity')
    #lsSpKeywords = oS.get_keywords(3, 'speech')
    #print("-------", sExamplePath)
    #print('entity keywords:  ', lsEntKeywords)
    #print('parts of speech keywords', lsSpKeywords)


    
    
    





class Sirakis:
    """
    Roman Hartmann, romah@dotmodus.com
    Class for creating keywords and basic summary of input article text file
    methods based on spaCy algorithm
    required packages:
        pip install numpy
        SpaCy
            https://spacy.io/
            pip install spacy
            python -m spacy.en.download
            need newest version of numpy
    """
    
    #---helper functions
    def uniquify(self, l, bCount=False):
        "create ordered list of unique strings.  Count occurences if bCount is True and sort by highest"
        if bCount:
            dRet = {}
            for s in l:
                if s not in dRet.keys():
                    dRet[s] = 1
                else:
                    dRet[s] += 1
            
            lRet = [(dRet.keys()[i], dRet.values()[i]) for i in range(len(dRet.keys()))]
            lRet = sorted(lRet, key = lambda t: t[1], reverse=True)
            return lRet
        else:
            lRet = []
            for s in l:
                if s not in lRet:
                    lRet.append(s)
            return lRet
    
    
    
    def remove_similar(self, lsOrig):
        "take list input and return exact and subset excluded items and their counts"
        lsOrig.sort(key=len, reverse=True)
        
        #check if a similar already exists in the new list
        def similar_exists(sItem, l):
            for s in l:
                if sItem in s:
                    return s
            return False
        
        #only add new to list if it does not alredy exist
        dRet = {}
        for s in lsOrig:
            sInD = similar_exists(s, dRet.keys())
            if s not in dRet and not sInD:
                dRet[s] = 1
            else:
                dRet[sInD] += 1
        
        ltRet = [(dRet.keys()[i], dRet.values()[i]) for i in range(len(dRet.keys()))]
        ltRet = sorted(ltRet, key = lambda t: t[1], reverse=True)
        return ltRet
    
    
    
    
    def __init__(self, sPath):
        from spacy.en import English
        self.oNlp           = English()
        self.sText          = self.get_text(sPath)
        self.oDoc           = self.process_text(self.sText)
        self.loTokens       = [o for o in self.oDoc]
        self.loEntities     = [o for o in self.oDoc.ents]
        self.loSentences    = [o for o in self.oDoc.sents]
        self.loAllWords     = [w for w in self.oNlp.vocab if w.has_vector]
    
    
    #---initial processing functions
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
    
    
    #---base data functions
    def extract_subject(self):
        "extract the subject and objects from the text."
        from subject_object_extraction import findSVOs
        return findSVOs(self.oDoc)
    
    
    def get_similar_words(self, oToken, iMin=0, iMax=20):
        "get similar words by word vectors.  iMin/ iMax are indeces for the segment of most similar words"
        from numpy import dot
        from numpy.linalg import norm
        oCos  = lambda v1, v2: dot(v1, v2) / (norm(v1) * norm(v2))
        loAllWords = sorted(self.loAllWords, key=lambda w: oCos(w.vector, oToken.vector), reverse=True)
        loSimilar = [o for o in loAllWords[iMin:iMax]]
        lsSimilar = [w.lower_ for w in loAllWords[iMin:iMax]]
        
        lsUniqueSimilar = self.uniquify(lsSimilar)
        
        return lsUniqueSimilar
    
    
    #---processing functions
    def sequential_pos_elements(self, loTokens, sType):
        "get list of words speech tag elements of certain sType given list of annotated speech tags"
        lRet = []
        sEnt = ''
        for i in range(len(loTokens)-1):
            if loTokens[i].pos_ == sType:
                sEnt += u' {}'.format(loTokens[i].lemma_)
            elif loTokens[i].pos_ != sType and sEnt != '':
                lRet.append(sEnt.strip())
                sEnt = ''
        
        return lRet
    
    
    def keywords(self, iKeywords=3):
        """
        Returns list with most common noun entity supersets
        """
        #TODO where, who, what
        loTokensCleaned = [o for o in self.loTokens if u'\u2019' not in o.lemma_ and u'u\201d' not in o.lemma_]
        loTokens = [o for o in loTokensCleaned if o.pos_ != u'SPACE']
        
        #lsNouns = oS.sequential_pos_elements(loTokensCleaned, u'NOUN')
        #lsUniqNouns = self.uniquify(lsNouns, True)
        #lsSimilarNouns = self.remove_similar(lsNouns)
        lsEntities = [o.lemma_ for o in self.loEntities if o.root.pos_ == u'NOUN']
        
        #lsUniqEntities = self.uniquify(lsEntities, True)
        ltSimilarEntities = self.remove_similar(lsEntities)
        lsKeywords = [t[0] for t in ltSimilarEntities[0:iKeywords]]
        
        return lsKeywords
    




    
    
    #TODO necessary? -------
    #def get_sentence_lists(self, loSentences):
        #"""
        #list of sentences from self.sText
        #lsSentences:  List of sentences in string form
        #llSentences:  list of sentences comprised of list of entities
        #"""
        #lsSentences = []
        #llSentences = []
        #for oSpan in self.loSentences:
            #sSent = ''.join(self.oDoc[i].string for i in range(oSpan.start, oSpan.end)).strip()
            #lSent = [self.oDoc[i] for i in range(oSpan.start, oSpan.end)]
            #lsSentences.append(sSent)
            #llSentences.append(lSent)
        #return lsSentences, llSentences
    
    #def speech_tags(self, loTokens):
        #"returns list of speech tags (essentially words) given list of words"
        #llTags = []
        #for oToken in loTokens:
            #llTags.append([oToken.orth_, oToken.pos_])
        #return llTags
    
    

    #def get_entities(self, oText):
        #"""returns list of [entities + entity labels] for each word that is an entitiy.  
        #Returns type Span
        #oSpan.root = type(Token)"""
        #loEnts = list(oText.ents)
        #lsLabels = [o.label_ for o in loEnts]
        #llEnts = [[loEnts[i].orth_, lsLabels[i]] for i in range(len(lsLabels)) ]
        #return llEnts
    
    
    
    
    
    #def get_keywords(self, iKW, sType):
        #"""get keywords from the given labelled entities
        #sType is either 'speech' or 'entity'
        #"""
        ##get most common noun
        ##TODO totally refactor
        #llTags = self.speech_tags(self.loTokens)
        #lNouns = []
        #for i in range(len(llTags)):
            #if llTags[i][1] == 'NOUN':
                #lNouns.append(llTags[i][0].strip())
        #llUniqueNouns = sorted(self.remove_similar(lNouns), key = lambda t: t[1], reverse=True)
        #lsUniqueNouns = [l[0] for l in llUniqueNouns]
        
        #def get_top_phrases(lsPhrases, iKW):
            #"lsPhrases is nouns or entities, iKW number of keywords"
            #lsKeywords = []
            #for i in range(len(lsUniqueNouns)):
                ##prevent repetition of constituent nouns
                #for sKeyword in lsKeywords:
                    #if lsUniqueNouns[i] in sKeyword:
                        #i += 1
                #sNoun = lsUniqueNouns[i]
                #for sPhrase in lsPhrases:
                    #if sNoun in sPhrase and sPhrase not in lsKeywords:  #prevent repetition of keyword phrases
                        #lsKeywords.append(sPhrase)
                        #break
                
                #if len(lsKeywords) == iKW:
                    #break
            #return lsKeywords
                
                
        ##gets top of every type of speech noun
        #if sType == 'speech':
            ##get the top 3 noun phrases that contain the most common unique nouns
            #llNounPhrases = self.speech_tag_elements(llTags, 'NOUN')
            #lsNounPhrases = [l[0] for l in sorted(self.remove_similar(llNounPhrases), key = lambda t: t[1], reverse=True)]
            #lsKeywords = get_top_phrases(lsNounPhrases, iKW)
            
        ##gets top of every type of entity
        #elif sType == 'entity':
            #llEnts = self.get_entities(self.oDoc)
            #lsEnts = [l[0] for l in llEnts]
            #lsKeywords = get_top_phrases(lsEnts, iKW)
            
        #return lsKeywords

    





if __name__ == '__main__':
    
    run()
