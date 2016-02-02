

def run():
    import os
    sHerePath = os.getcwd()
    sExamplePath = "{}/news_sample.txt".format(sHerePath)


    oS = SpacyAnalasys(sExamplePath)
    
    
    
    lsEntKeywords = oS.get_keywords('entity')
    lsSpKeywords = oS.get_keywords('speech')
    print(lsEntKeywords)
    print(lsSpKeywords)





class SpacyAnalasys:
    "methods based on spaCy algorithm"
    #import spacy
        #https://spacy.io/
        #pip install spacy
        #python -m spacy.en.download
        #need newest version of numpy
    
    def __init__(self, sPath):
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
        from spacy.en import English
        oNlp = English()
        oDoc = oNlp(sText)
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
    
    
    def speech_tags(self, lWords):
        "returns list of speech tags (essentially words) given list of words"
        llTags = []
        for oToken in lWords:
            llTags.append([oToken.orth_, oToken.pos_])
        return llTags
    
    
    def speech_tag_elements(self, llTags, sType):
        "get list of words speech tag elements of certain sType given list of annotated speech tags"
        lRet = []
        sEnt = ''
        for i in range(len(llTags)-1):
            if llTags[i][1] == sType:
                sEnt += " {}".format(llTags[i][0])
            elif llTags[i][1] != sType and sEnt != '':
                lRet.append(sEnt.strip())
                sEnt = ''
        
        return lRet
    
    
    def get_entities(self, oText):
        "returns list of [entities + entity labels] for each word that is an entitiy."
        loEnts = list(oText.ents)
        lsLabels = [o.label_ for o in loEnts]
        llEnts = [[loEnts[i].orth_, lsLabels[i]] for i in range(len(lsLabels)) ]
        return llEnts
    
    
    def get_keywords(self, iKW, sType):
        """get keywords from the given labelled entities
        sType is either 'speech' or 'entity'
        """
        
        #get most common noun
        lText = [oWord for oWord in self.oDoc]
        llTags = self.speech_tags(lText)
        lNouns = []
        for i in range(len(llTags)):
            if llTags[i][1] == 'NOUN':
                lNouns.append(llTags[i][0].strip())
        llUniqueNouns = sorted(self.remove_similar(lNouns), key = lambda t: t[1], reverse=True)
        lsUniqueNouns = [l[0] for l in llUniqueNouns]
        
        def get_top_phrases(lsPhrases, n):
            "lsPhrases is nouns or entities, n is top nr int"
            lsKeywords = []
            lsKeywords = []
            for i in range(len(lsUniqueNouns)):
                for sKeyword in lsKeywords:
                    if lsUniqueNouns[i] in sKeyword:
                        i += 1
                sNoun = lsUniqueNouns[i]
                for j in range(len(lsPhrases)):
                    sPhrase = lsPhrases[j]
                    if sNoun in sPhrase and sPhrase not in lsKeywords:
                        lsKeywords.append(sPhrase)
                        break
                
                #lsKeywords = list(set(lsKeywords))
                if len(lsKeywords) == 3:
                    break
            return lsKeywords
        
        
        #gets top of every type of speech noun
        if sType == 'speech':
            #get the top 3 noun phrases that contain the most common unique nouns
            llNounPhrases = self.speech_tag_elements(llTags, 'NOUN')
            lsNounPhrases = [l[0] for l in sorted(self.remove_similar(llNounPhrases), key = lambda t: t[1], reverse=True)]
            get_top_phrases(lsNounPhrases, iKW)
            
        #gets top of every type of entity
        elif sType == 'entity':
            llEnts = oS.get_entities(self.oDoc)
            lsEnts = [l[0] for l in llEnts]
            lsKeywords = get_top_phrases(lsEnts, iKW)
            
        return lsKeywords
        
            





if __name__ == '__main__':
    
    run()
