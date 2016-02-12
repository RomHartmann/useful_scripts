

def run():
    import os
    sHerePath = os.getcwd()
    sPath = "{}/news_sample2.txt".format(sHerePath)
    
    from spacy.en import English
    oNlp = English()
    oS = Sirakis(sPath, oNlp)

    print(sPath)
    print(oS.keywords())

    #lsEntKeywords = oS.get_keywords(3, 'entity')
    #lsSpKeywords = oS.get_keywords(3, 'speech')
    #print("-------", sPath)
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
    sPath is the path to the text file containing the article
    bN24: True if follows News 24 format of having the location as the first element
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
    
    
    
    #def remove_similar(self, lsOrig):
        #"take list input and return exact and subset excluded items and their counts"
        #lsOrig.sort(key=len, reverse=True)
        
        ##check if a similar already exists in the new list
        #def similar_exists(sItem, l):
            #for s in l:
                #if sItem in s:
                    #return s
            #return False
        
        ##only add new to list if it does not alredy exist
        #dRet = {}
        #for s in lsOrig:
            #sInD = similar_exists(s, dRet.keys())
            #if s not in dRet and not sInD:
                #dRet[s] = 1
            #else:
                #dRet[sInD] += 1
        
        #ltRet = [(dRet.keys()[i], dRet.values()[i]) for i in range(len(dRet.keys()))]
        #ltRet = sorted(ltRet, key = lambda t: t[1], reverse=True)
        #return ltRet
    
    
    
    
    def __init__(self, sPath, oNlp, bN24=True):
        self.oNlp = oNlp
        self.get_text(sPath, bN24)
        self.process_text()
        
        self.loTokens       = [o for o in self.oDoc]
        self.loEntities     = [o for o in self.oDoc.ents]
        self.loSentences    = [o for o in self.oDoc.sents]
        self.loAllWords     = [o for o in self.oNlp.vocab if o.has_vector]
    
    
    #---initial processing functions
    def get_text(self, sPath, bN24):
        "unicode text from file"
        with open(sPath, 'r') as f:
            sText = f.read()
        sText = unicode(sText, "utf-8")
        
        #extract location from first elements of text
        if bN24:
            sLocation = sText.split(u' - ')[0]
            sText = u' - '.join(sText.split(u' - ')[1::])
        else:
            sLocation = u''
        
        self.sText = sText
        self.sLocation = sLocation.lower().strip()
    
    
    def process_text(self):
        "loads nlp packages and inserts text.  Returns nlp object"
        oDoc = self.oNlp(self.sText)
        self.oDoc = oDoc
    
    
    #---base data functions
    def extract_subject(self):
        "extract the subject and objects from the text."
        from subject_object_extraction import findSVOs
        return findSVOs(self.oDoc)
    
    
    def get_similar_words(self, oToken, iMin=0, iMax=20):
        "get similar words by word vectors.  iMin/ iMax are indeces for the segment of most similar words"
        from numpy import dot
        # token vectors already normalized, hence just dot product
        loAllWordsSorted = sorted(self.loAllWords, key=lambda oW: dot(oW.vector, oToken.vector), reverse=True)
        lsSimilar = [o.lower_ for o in loAllWordsSorted[iMin:iMax]]
        
        lsUniqueSimilar = self.uniquify(lsSimilar)
        
        return lsUniqueSimilar
    
    
    def get_vector(self, sWord):
        "return Lexeme class object form the almighty list of word objects loAllWords"
        sWord = sWord.lower()
        for oLex in self.loAllWords:
            if sWord == oLex.orth_.lower():
                return oLex.vector
        import numpy as np
        return (np.zeros(np.shape(self.loAllWords[1].vector))).astype('float32')
    
    
    
    #---processing functions
    def get_noun_phrases(self, loTokens):
        "get list of words speech tag elements of certain sType given list of annotated speech tags"
        lRet = []
        sEnt = ''
        for oToken in loTokens:
            if oToken.pos_ == u'NOUN':
                sEnt += u' {}'.format(oToken.lemma_)
            elif oToken.pos_ != u'NOUN' and sEnt != '':
                lRet.append(sEnt.strip())
                sEnt = ''
        
        return lRet
    
    
    
    def keywords(self, iKeywords=3):
        """
        Returns list with most common noun entity supersets
        """
        
        
#---get important noun phrases
dTokens = {}
for o in self.loTokens:
    dTokens[o.lemma_] = o

loTokensCleaned = [o for o in self.loTokens if u'\u2019' not in o.lemma_ and u'u\201d' not in o.lemma_]
loTokens = [o for o in loTokensCleaned if o.pos_ != u'SPACE']

lsNounPhrases = oS.get_noun_phrases(loTokensCleaned)

lsImportantNouns = []
for sNoun in lsNounPhrases:
    try:
        oNoun = dTokens[sNoun]
        if oNoun.ent_type_ == u'GPE' or oNoun.ent_type_ == u'PERSON' or oNoun.ent_type_ == u'ORG':
            lsImportantNouns.append(oNoun.lemma_)
    except KeyError:
        lsImportantNouns.append(sNoun)


lsUniqueNouns = self.uniquify(lsNounPhrases, True)
#lsSimilarNouns = self.remove_similar(lsNounPhrases)
loUniqueNouns = [dTokens[s[0]] for s in lsUniqueNouns if s[0] in dTokens.keys()]
#loSimilarNouns = [dTokens[s[0]] for s in lsSimilarNouns if s[0] in dTokens.keys()]
lsUniqueImportantNouns = self.uniquify(lsImportantNouns, True)
#lsSimilarImportantNouns = self.remove_similar(lsImportantNouns)
#---

#---get top entities of each relevant kind
dEnts = {}
for o in self.loEntities:
    dEnts[o.lemma_] = o

lsEntities = [o.lemma_ for o in self.loEntities if o.label_ == u'GPE' or o.label_ == u'PERSON' or o.label_ == u'ORG']

lsUniqueEntities = self.uniquify(lsEntities, True)
#ltSimilarEntities = self.remove_similar(lsEntities)
loSimilarEnts = [dEnts[s[0]] for s in lsUniqueEntities]

oTopPlaceEnt = None
for oEnt in loSimilarEnts:
    if oEnt.label_ == u'GPE':
        oTopPlaceEnt = oEnt
        break

oTopPersonEnt = None
for oEnt in loSimilarEnts:
    if oEnt.label_ == u'PERSON':
        oTopPersonEnt = oEnt
        break

oTopOrgEnt = None
for oEnt in loSimilarEnts:
    if oEnt.label_ == u'ORG':
        oTopOrgEnt = oEnt
        break

lsEntKeywords = [oTopPlaceEnt, oTopPersonEnt, oTopOrgEnt]
#-----


#unknown items
loUnknown = [o for o in loNouns if norm(o.vector)==0]
#---



#get nouns most similar/orthogonal to each other
loNouns = [o for o in loTokensCleaned if o.pos_ == u'NOUN']
dSimilar = {}
dDifferent = {}
dNounCorrelation = {}

for oNoun in loNouns:
    from numpy import dot
    loCorrelationWords = sorted(loNouns, key=lambda oW: dot(oW.vector, oNoun.vector), reverse=True)
    lsSimilar = [o.lower_ for o in loCorrelationWords[1:4]]
    lsDifferent = [o.lower_ for o in loCorrelationWords[-3::]]
    
    lsUniqueSimilar = self.uniquify(lsSimilar)
    lsUniqueDifferent = self.uniquify(lsDifferent)
    
    dSimilar[oNoun.lemma_] = lsUniqueSimilar
    dDifferent[oNoun.lemma_] = lsUniqueDifferent
    
    
    dNounCorrelation[oNoun.lemma_] = {}
    dNounCorrelation[oNoun.lemma_][u'similar'] = lsUniqueSimilar
    dNounCorrelation[oNoun.lemma_][u'different'] = lsUniqueDifferent

#---



#get highest dot product list
import numpy as np
dCorr = {}
for oNoun in loNouns:
    dCorr[oNoun.lemma_] = 0
    for oNoun2 in loNouns:
        dCorr[oNoun.lemma_] += np.dot(oNoun.vector, oNoun2.vector)

ltHighestCorr = sorted(zip(dCorr.keys(), dCorr.values()), key=lambda t: t[1], reverse=True)

#---


#get main element from cluster with cos(theta) > 0.5 (60 degrees)
import numpy as np
dClusters = {}
for oNoun in loNouns:
    dClusters[oNoun.lemma_] = []
    for oNoun2 in loNouns:
        if np.dot(oNoun.vector, oNoun2.vector) > 0.5:
            dClusters[oNoun.lemma_].append(oNoun2.lemma_)


ltAllClusters = sorted(zip(dClusters.keys(), dClusters.values()), key=lambda t: len(t[1]), reverse=True)

#TODO cluters are not supersets yet - do recursively

def add_children(sCluster, dGlobalClusters):
    try:
        dGlobalClusters[sCluster] += dClusters[sCluster]
    except KeyError:
        dGlobalClusters[sCluster] = dClusters[sCluster]
    
    for sKey in dClusters[sCluster]:
        add_children(sKey, dGlobalClusters)
    
    return dGlobalClusters

dGlobalClusters = {}
add_children(dClusters.keys()[0], dGlobalClusters)



#dGlobalClusters = {}
#for sKey in dClusters.keys():
    #dGlobalClusters[sKey] = []
    #for s in dClusters[sKey]:
        #dGlobalClusters[sKey] += dClusters[s]
    #dGlobalClusters[sKey] = list(set(dGlobalClusters[sKey]))

llGlobalClusters = []
for lCluster in dGlobalClusters.values():
    if lCluster not in llGlobalClusters and len(lCluster)>1:
        llGlobalClusters.append(lCluster)


#---






        
        return lsKeywords
    




    




if __name__ == '__main__':
    
    run()
