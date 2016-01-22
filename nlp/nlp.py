

def run():
    sExamplePath = "/home/roman/code_projects/useful_scripts/entity_recognition/news_sample.txt"


    oS = Spacy_methods()

    oS.do_thing()







class Spacy_methods:
    "methods based on spaCy algorithm"
    import spacy
        #https://spacy.io/
        #pip install spacy
        #python -m spacy.en.download
        #need newest version of numpy
    
    def __init__(self):
        pass
    
    def get_text(self, sPath):
        with open(sPath, 'r') as f:
            sText = f.read()
    
    def do_thing(self):
        import os
        if os.environ.get('SPACY_DATA'):
            data_dir = os.environ.get('SPACY_DATA')
        else:
            data_dir = None
        print("Load EN from %s" % data_dir)

        from spacy.en import English
        nlp = English(data_dir=data_dir)
        doc = nlp('Hello, world. Here are two sentences.')







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
