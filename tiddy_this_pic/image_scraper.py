
class ImageScraper:

    def __init__(self, sURL, iNrImages=400, bSearch=False):

        if bSearch:
            self.sURL = self.get_search_url(sURL)
        else:
            self.sURL = sURL

        self.iNrImages = iNrImages

        self.get_images()


    @staticmethod
    def get_search_url(sSearch):
        """return google search url"""
        sSearch = "https://www.google.co.za/search?q={}&client=ubuntu&hs=gT6&source=lnms&tbm=isch&sa=X&ved=0ahUKEwjEh-TI19TLAhVL5xoKHfczDf8Q_AUIBygB&biw=1309&bih=662".format(sSearch)
        sURL = sSearch.replace(" ", "+")
        return sURL


    def get_images(self):
        """get n amount of google images and save them under folder named sSearch"""
        import urllib2
        import subprocess

        sFileName = "mosaics"

        import os
        sCWD = os.getcwd()
        sDirName = sFileName
        sOutPath = os.path.join(sCWD, sDirName)

        if not os.path.isdir(sOutPath):
            os.mkdir(sOutPath)


        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

        headers={'User-Agent':user_agent,}

        request=urllib2.Request(self.sURL,None,headers) #The assembled request
        response = urllib2.urlopen(request)
        data = response.read() # The data u need

        lData = data.split('<img')

        i = 1
        for sText in lData[1::]:
            sURL = sText.split('src=')[1].split(' ')[0]

            sFileName = os.path.join(sOutPath, sURL.split('/')[-1]).strip('"')

            if not os.path.isfile(sFileName):
                sCommand = "{} {} {} {}".format('wget', sURL, '-P', sOutPath)
                subprocess.call(sCommand, shell=True)

            i+= 1
            if i > self.iNrImages:
                break





if __name__ == "__main__":

    import argparse
    oParser = argparse.ArgumentParser()
    oParser.add_argument('-gs', '--google_search', default=None, help="search string for google images")
    oParser.add_argument('-url', '--url_enter', default=None, help="search string for google images")

    oArgs = oParser.parse_args()
    sSearch = oArgs.google_search
    sURL = oArgs.url_enter

    if sURL is None:
        bSearch = True
    else:
        bSearch = False

    oI = ImageScraper(sURL, bSearch=bSearch)

    #http://www.bignudeboobs.com/ lots of scrapable boob pics (god, I can't believe I'm actually doing this)
