

def run(sFile):
    import os
    from spacy.en import English
    oNlp = English()    #takes a lot of computaion; do once.

    sHerePath = os.getcwd()
    sPath = "{}/articles/{}".format(sHerePath, sFile)
    oS = Sirakis(sPath, oNlp)

    print(oS.keywords())
    
    print(oS.summary())






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
    """
    
    #---helper functions
    def uniquify(self, ls, bCount=False):
        "create ordered list of unique strings.  Count occurences if bCount is True and sort by highest"
        if bCount:
            dRet = {}
            for s in ls:
                if s not in dRet.keys():
                    dRet[s] = 1
                else:
                    dRet[s] += 1
            
            lRet = [(dRet.keys()[i], dRet.values()[i]) for i in range(len(dRet.keys()))]
            lRet = sorted(lRet, key = lambda t: t[1], reverse=True)
            return lRet
        else:
            lRet = []
            for s in ls:
                if s not in lRet:
                    lRet.append(s)
            return lRet
    
    
    
    
    def __init__(self, sPath, oNlp):
        self.oNlp = oNlp
        self.get_text(sPath)
        
        self.oDoc           = self.oNlp(self.sText)
        
        self.loTokens       = [o for o in self.oDoc]
        self.loEntities     = [o for o in self.oDoc.ents]
        self.loSentences    = [o for o in self.oDoc.sents]
        self.loAllWords     = [o for o in self.oNlp.vocab if o.has_vector]
        
        self.loTokensAscii  = [o for o in self.loTokens if o.is_ascii]
        self.loNouns        = [o for o in self.loTokensAscii if 'NN' in o.tag_]     #or o.pos_ == u'NOUN'
        
        self.dTokens        = dict(zip( [o.lemma_ for o in self.loTokens], self.loTokens ))
        self.dSentences     = dict(zip( [o.lemma_ for o in self.loSentences], self.loSentences ))
    
    
    #---initial processing functions
    def get_text(self, sPath):
        "unicode text from file"
        with open(sPath, 'r') as f:
            sText = f.read()
        sText = unicode(sText, "utf-8")
        
        #extract location from first elements of text if the dash exists in the first 50 characters.
        if u' - ' in sText[0:50]:
            sLocation = sText.split(u' - ')[0]
            sText = u' - '.join(sText.split(u' - ')[1::])
        else:
            sLocation = u''
        
        self.sText = sText
        self.sLocation = sLocation.lower().strip()
    
    
    #---base data functions
    def extract_subject(self):
        "extract the subject and objects from the text."
        from subject_object_extraction import findSVOs
        return findSVOs(self.oDoc)
    
    
    def get_similar_words(self, oToken, iMin=0, iMax=6, loDict=None):
        "get similar words by word vectors.  iMin/ iMax are indeces for the segment of most similar words"
        import numpy as np
        if type(oToken) == np.ndarray:
            aVect = oToken
        else:
            aVect = oToken.vector
        if loDict == None:
            loDict = self.loAllWords
            
        # token vectors already normalized, hence just dot product
        loAllWordsSorted = sorted(loDict, key=lambda oW: np.dot(oW.vector, aVect), reverse=True)
        #tokens have lemma, lexemes not
        try:
            lsSimilar = [o.lemma_ for o in loAllWordsSorted]
        except AttributeError:
            lsSimilar = [o.lower_ for o in loAllWordsSorted]
        
        lsUniqueSimilar = self.uniquify(lsSimilar)[iMin:iMax]
        
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
    
    
    
    def get_cluster_heads(self, loItems, bTokens=True, rCorr=0.6):
        "get the heads for clusters with correlation rCorr > cos(theta)   (between 0 and 1)"
        import numpy as np
        
        if bTokens:
            dToObjects = self.dTokens
        else:
            dToObjects = self.dSentences
        
        #create local clusters with correlation of more than 0.6
        dClusters = {}
        for oNoun in loItems:
            dClusters[oNoun.lemma_] = []
            for oNoun2 in loItems:
                if np.dot(oNoun.vector, oNoun2.vector) > rCorr:
                    dClusters[oNoun.lemma_].append(oNoun2.lemma_)
        
        
        ltAllClusters = sorted(zip(dClusters.keys(), dClusters.values()), key=lambda t: len(t[1]), reverse=True)
        
        
        #create global clusters
        def add_children(sCluster, lAdded, sMember):
            "recursive function to create the global clusters"
            if lAdded == []:
                dGlobalClusters[sCluster] = list(dClusters[sCluster])
                lAdded.append(sCluster)
            else:
                for s in dClusters[sMember]:
                    dGlobalClusters[sCluster].append(s)
                dGlobalClusters[sCluster] = list(set(dGlobalClusters[sCluster]))
                lAdded.append(sMember)
            
            for sMember in dGlobalClusters[sCluster]:
                if sMember not in lAdded:
                    add_children(sCluster, lAdded, sMember)
            
        
        dGlobalClusters = {}
        for sCluster in dClusters.keys():
            dGlobalClusters[sCluster] = []
            add_children(sCluster, [], None)
        
        
        #create unique global cluster sets
        llsGlobalClusters = []
        for lCluster in dGlobalClusters.values():
            lCluster = sorted(list(set(lCluster)))
            if lCluster not in llsGlobalClusters and len(lCluster)>1:
                llsGlobalClusters.append(lCluster)
        
        
        lloGlobalClusters = [ [dToObjects[s] for s in l] for l in llsGlobalClusters ]
        
        #calculate main component of global cluster set
        loMainTokens = []
        for loClusterSet in lloGlobalClusters:
            ltCorrelations = []
            for oComponent in loClusterSet:
                if bTokens and (oComponent.ent_type_ == u'DATE' or oComponent.ent_type_ == u'TIME'):
                    continue
                iSum = 0
                for o2 in loClusterSet:
                    iSum += np.dot(oComponent.vector, o2.vector)
                ltCorrelations.append((oComponent, iSum))
            
            if len(ltCorrelations) == 0:
                continue
            elif len(ltCorrelations) == 2:
                loMainTokens.append([t[0] for t in ltCorrelations])
            else:
                oMainToken = sorted(ltCorrelations, key=lambda t: t[1], reverse = True)[0][0]
                loMainTokens.append(oMainToken)
        
        return loMainTokens
    
    
    
    def keywords(self, iKW = 5):
        """
        Returns list with most common noun entity supersets
        """
        
        #unit vector of average of all noun tokens
        import numpy as np
        aAvg = np.zeros(np.shape(self.loNouns[0].vector))
        for oNoun in self.loNouns:
            aAvg += oNoun.vector
            aAvgVect = aAvg/np.linalg.norm(aAvg)
        
        lsAvgArticleNouns = self.get_similar_words(aAvgVect, loDict=self.loNouns, iMax=iKW)     #much more useful
        loAvgArticleNouns = [self.dTokens[s] for s in lsAvgArticleNouns]
        #---
        
        
        
        ltUniqueNouns = [(self.dTokens[t[0]], t[1]) for t in self.uniquify([o.lemma_ for o in self.loNouns], True)]
        ltProbNouns = []
        for t in ltUniqueNouns:
            ltProbNouns.append((t[0], (t[1]*t[0].prob)))
        
        ltProbNouns.sort(key=lambda t:t[1])
        loProbKeywords = [t[0] for t in ltProbNouns][0:iKW]
        
        
        return {
            'loAvgArticleNouns': loAvgArticleNouns,
            'loProbKeywords': loProbKeywords
        }
    
    
    def summary(self, iNrSentences = 5):
        "create a summary of the text"
        
        loAvgArticleNouns = self.keywords(iKW = iNrSentences)['loAvgArticleNouns']
        lsSents = []
        lUsed = []
        for oSent in self.loSentences:
            for oK in loAvgArticleNouns:
                if oK.lemma_ in [o.lemma_ for o in oSent] and oK.lemma_ not in lUsed and oSent.orth_ not in lsSents:
                    lsSents.append(oSent.orth_)
                    lUsed.append(oK.lemma_)
        
        
        return lsSents
    
    
    
    
    def other_possibly_useful_shit():
        "just some stuff that is cool, but not useful right now"
        
        
        #---create local and global clusters of token vectors
        
        lClusterTokens = self.get_cluster_heads(self.loNouns)
        
        #which keywords have the highest overall correlation
        loFlatClusterTokens = []
        for i in range(len(lClusterTokens)):
            if type(lClusterTokens[i]) == list:
                for oToken in lClusterTokens[i]:
                    loFlatClusterTokens.append(oToken)
            else:
                oToken = lClusterTokens[i]
                loFlatClusterTokens.append(oToken)
        
        
        #get keywords by looking for most cross correlating in iterations
        def most_corr(loTokens):
            "get sorted list of most mutually correlating token"
            ltKeywords = []
            for o1 in loTokens:
                iSum = 0
                for o2 in loTokens:
                    if o1.lemma_ != o2.lemma_:
                        iSum += np.dot(o1.vector, o2.vector)
                ltKeywords.append((o1, iSum))
            
            ltKeywords.sort(key=lambda t: t[1], reverse=True)
            return ltKeywords
        
        
        #remove most correlating token as keyword and look for new most correlating
        ltKeywords = most_corr(loFlatClusterTokens)
        loCorrKeywords = []
        for i in range(iKW):
            if len(ltKeywords)>0:
                loCorrKeywords.append(ltKeywords.pop(0)[0])
                loTokens = [t[0] for t in ltKeywords]
                ltKeywords = most_corr(loTokens)
        
        
        lsCorrKeywords = [o.lemma_ for o in loCorrKeywords]
        if self.sLocation.lower() not in lsCorrKeywords:
            lsCorrKeywords[-1] = self.sLocation
        
        #---
        
        lUsefulTokenThings = [lsCorrKeywords, ]
        
        
        
        loClusterSents = self.get_cluster_heads(self.loSentences, False, 0.3)
        
        #PCA
        from sklearn.decomposition import PCA
        import numpy as np
        iIntComponents = 100  #upper limit
        pca = PCA(n_components = iIntComponents)
        lAllArrays = [o.vector for o in self.loNouns]
        aAllArrays = np.array(lAllArrays)
        pca.fit(aAllArrays)
        
        #automatically find number of components by finding a sharp drop
        aVariance = pca.explained_variance_ratio_
        for i in range(len(aVariance)-1):
            if aVariance[i]/aVariance[i+1]>5:
                break
        
        iComponents = i+1
        pca = PCA(n_components = iComponents)
        lAllArrays = [o.vector for o in self.loNouns]
        aAllArrays = np.array(lAllArrays)
        pca.fit(aAllArrays)
        
        llsPcaComponents = []
        for i in range(iComponents):
            llsPcaComponents.append(self.get_similar_words(pca.components_[i], loDict=self.loNouns, iMax=3))
        
        #---
        
        
        
        #---get subjects
        ltSubjects = self.extract_subject()
        
        #---
        
        lMightBeUseful = [loClusterSents, llsPcaComponents, ltSubjects]
    
    






import os
from spacy.en import English
oNlp = English()

sHerePath = os.getcwd()

sPath = "{}/articles/{}".format(sHerePath, "economy.txt")
oS = Sirakis(sPath, oNlp)
self = oS



def test(sFile):
    sPath = "{}/articles/{}".format(sHerePath, sFile)
    oS = Sirakis(sPath, oNlp)
    dKW = oS.keywords()
    print "==="
    print(sPath)
    print 'loAvgArticleNouns:   ', dKW['loAvgArticleNouns']
    print 'loProbKeywords:   ', dKW['loProbKeywords']
    print "---"
    print(oS.summary())
    print("\n\n")


test("economy.txt")
test("economy2.txt")
test("economy3.txt")
test("fin.txt")
test("fin2.txt")
test("fin3.txt")
test("fin4.txt")
test("fin5.txt")
test("health.txt")
test("health2.txt")
test("health3.txt")
test("news.txt")
test("news2.txt")
test("news3.txt")
test("news4.txt")
test("news5.txt")
test("sport.txt")
test("sport2.txt")









if __name__ == '__main__':
    
    import argparse
    oParser = argparse.ArgumentParser()
    oParser.add_argument(
        '-f', '--file',
        type=str,
        help="enter file name of unicode text file"
    )
    oArgs = oParser.parse_args()
    sFile = oArgs.file
    
    
    run(sFile, bLoc)
