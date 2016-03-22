class Tiddy():
    """takes input image and category, and recreates the image in terms of little images (mosaics) of said category"""

    def __init__(self, sImagePath, sCategory):
        self.sImagePath = sImagePath
        self.sCategory = sCategory

        import os
        sCWD = os.getcwd()
        sFilename = "mosaic.jpg"
        self.sWritePath = os.path.join(sCWD, sFilename)


    def get_image(self):
        from PIL import Image
        oImg = Image.open(self.sImagePath)

        return oImg


    def get_mosaics_from_online(self):
        """scrape images from url"""
        from image_scraper import ImageScraper
        ImageScraper(self.sCategory, bSearch=True)


    @staticmethod
    def load_mosaics_from_file():
        """load images as objects"""
        import os
        from PIL import Image
        sPath = os.path.join(os.getcwd(), 'mosaics')
        loMosaics = []

        lImages = os.listdir(sPath)
        for sFile in lImages:
            sMosaicPath = os.path.join(sPath, sFile)

            oImg = Image.open(sMosaicPath)
            loMosaics.append(oImg)

        return loMosaics



    def monochrome_image(self, oImage):
        """make original image monochrome"""
        oMonoChrome = oImage.convert('LA')

        return oMonoChrome


    def downsample_image(self, oOrigImage, iScaleFactor=20):
        """downsample the image to create mosaic pixels"""
        tSize = oOrigImage.size
        tNewSize = (tSize[0]/iScaleFactor, tSize[1]/iScaleFactor)

        import numpy as np
        oNew = oOrigImage.resize(tNewSize)
        aNew = np.array([t[0] for t in oNew.getdata()])
        aNew = aNew.reshape(tNewSize)

        import pdb; pdb.set_trace()

        return oNew, aNew




    def assign_mosaics(self):

        pass


    def tiddy_this_thang(self):

        oOrigImage = self.get_image()
        oMonoChrome = self.monochrome_image(oOrigImage)
        oDSImage, aDSImage = self.downsample_image(oMonoChrome)


        import pdb; pdb.set_trace()
