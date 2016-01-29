

def run():
    import os
    sHerePath = os.getcwd()
    sExamplePath = "{}/news_sample.txt".format(sHerePath)


    oS = SpacyAnalasys(sExamplePath)
    
    #all sentences
    lsSents, llSents = oS.sentences()
    
    #speech tags
    lTags = oS.speech_tags(llSents[0])
    
    #---get keywords
    llEnts = oS.get_ents(oS.oDoc)
    
    print oS.get_keywords(llEnts)



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
    
    
    #Helper functions
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
        
        llUniq = zip(lUniq, lCount)
        return llUniq
    
    
    #Spacy functions
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
    
    
    def sentences(self):
        """
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
        lTags = []
        for oToken in lWords:
            lTags.append([oToken.orth_, oToken.pos_])
        return lTags
    
    
    def get_ents(self, oText):
        "returns list of [entities + entity labels] for each word that is an entitiy."
        loEnts = list(oText.ents)
        lsLabels = [o.label_ for o in loEnts]
        llEnts = [[loEnts[i].orth_, lsLabels[i]] for i in range(len(lsLabels)) ]
        return llEnts
    
    
    def get_keywords(self, llEnts):
        "get keywords from the given labelled entities"
        #all gpe, org, event, person
        lGpes = [l[0] for l in llAllEnts if l[1]=='GPE']
        lOrgs = [l[0] for l in llAllEnts if l[1]=='ORG']
        lEvents = [l[0] for l in llAllEnts if l[1]=='EVENT']
        lPersons = [l[0] for l in llAllEnts if l[1]=='PERSON']
        
        #remove duplicates and subsets and get most common
        sGpe = sorted(self.remove_similar(lGpes), key = lambda t: t[1], reverse=True)[0][0]
        sOrg = sorted(self.remove_similar(lOrgs), key = lambda t: t[1], reverse=True)[0][0]
        sEvent = sorted(self.remove_similar(lEvents), key = lambda t: t[1], reverse=True)[0][0]
        sPerson = sorted(self.remove_similar(lPersons), key = lambda t: t[1], reverse=True)[0][0]
        
        #TODO
        #check occurences of all NOUN tags (speech_tags(llSent)), especially sets of consecutive nouns
        
        return [sGpe, sOrg, sEvent, sPerson]
        






class Nltk_methods:
    "NLTK based methods"
    from textblob import TextBlob
        #https://textblob.readthedocs.org/en/latest/api_reference.html#textblob.blob.TextBlob.tags
    
    import nltk
        #http://www.nltk.org/
        
    
    def __init__(self):
        pass
    
    def get_text(self, sPath):
        with open(sPath, 'r') as f:
            sText = f.read()





if __name__ == '__main__':
    
    run()
