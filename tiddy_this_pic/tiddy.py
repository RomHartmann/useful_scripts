class Tiddy:
    """takes input image and category, and recreates the image in terms of little images (mosaics) of said category"""

    def __init__(self, sImagePath, sDirectory):
        self.sImagePath = sImagePath
        self.sDirectory = sDirectory

        import os
        sCWD = os.getcwd()
        sInputFilename = sImagePath.split("/")[-1].split(".")[0]
        sFilename = "tiddied_{}.jpg".format(sInputFilename)
        self.sWritePath = os.path.join(sCWD, "tiddied", sFilename)


    def get_mosaics_from_online(self, sLocation, bSearch):
        """scrape images from url or google search(only top 20)"""
        from image_scraper import ImageScraper
        ImageScraper(sLocation, bSearch)


    def load_mosaics_from_file(self, sFolderName="mosaics"):
        """load images as objects"""
        import os
        from PIL import Image
        sPath = os.path.join(os.getcwd(), "mosaic_folders", sFolderName)
        loMosaics = []
        dMosaics = {}

        #get average colour of pic
        lImages = os.listdir(sPath)
        self.iNrMosaicFiles = len(lImages)
        for sFile in lImages:
            sMosaicPath = os.path.join(sPath, sFile)

            oImg = Image.open(sMosaicPath)

            # if self.bMonochrome:
            #     oImg = self.monochrome_image(oImg)
            oResized, aaResized = self.reshape_image(oImg)
            loMosaics.append(oResized)

            #assign average colour to pic, and store in dict
            iAvgColour = sum(sum(aaResized))/aaResized.size
            if iAvgColour in dMosaics:
                dMosaics[iAvgColour].append(aaResized)
            else:
                dMosaics[iAvgColour] = [aaResized]



        return loMosaics, dMosaics


    def monochrome_image(self, oImage):
        """make original image monochrome"""
        oMonoChrome = oImage.convert('LA')

        return oMonoChrome


    def reshape_image(self, oOrigImage, tResize=(50,50)):
        """downsample the image to create mosaic pixels"""
        import numpy as np
        oNew = oOrigImage.resize(tResize)
        aNew = np.array([t[0] for t in oNew.getdata()])
        # import pdb; pdb.set_trace()
        aNew = aNew.reshape(tResize)

        return oNew, aNew


    def create_image_from_array(self, aaImage):
        """create Image object from array again
        sType has to be "Mono" or "RGB"
        """
        import numpy as np

        aaImage = aaImage.astype(np.uint8)
        from PIL import Image
        oImage = Image.fromarray(aaImage)

        return oImage


    def assign_mosaics(self, aaImage, dMosaics):
        """assign mosaics to image as constituent pixels
        based on pixel colour and average mosaic colour
        """
        import numpy as np
        iOldShapeX = aaImage.shape[0]
        iOldShapeY = aaImage.shape[1]
        iMosaicShapeX = dMosaics[dMosaics.keys()[0]][0].shape[0]
        iMosaicShapeY = dMosaics[dMosaics.keys()[0]][0].shape[1]
        tNewShape = (iOldShapeX*iMosaicShapeX, iOldShapeY*iMosaicShapeY)
        aaMosaicedPic = np.zeros(tNewShape)

        aAvailable = np.array(dMosaics.keys())

        def nearest(iCol):
            """get the nearest available pic colour"""
            iNearestIndex = (np.abs(aAvailable-iCol)).argmin()
            return aAvailable[iNearestIndex]

        iPicNr = 0
        for iRow in range(len(aaImage)):
            for iCol in range(len(aaImage[iRow])):
                iPixel = aaImage[iRow, iCol]

                #there can be more than one picture with the right colour
                lAvailableMosaics = dMosaics[nearest(iPixel)]
                if iPicNr >= len(lAvailableMosaics):
                    iPicNr = 0
                aaNearest = lAvailableMosaics[iPicNr]
                iPicNr += 1

                iStartRow = iRow*iMosaicShapeX
                iEndRow = iStartRow + iMosaicShapeX
                iStartCol = iCol*iMosaicShapeY
                iEndCol = iStartCol + iMosaicShapeY
                aaMosaicedPic[iStartRow: iEndRow, iStartCol: iEndCol] = aaNearest

        return aaMosaicedPic






    def tiddy_this_thang(self, bMonochrome=False, tFinalResize=None):
        """assigns images instead of pixels and creates a new pictures, saves it"""
        self.bMonochrome = bMonochrome

        import datetime
        oBegin = datetime.datetime.now()

        #get image to tiddy
        from PIL import Image
        oInputImage = Image.open(self.sImagePath)
        # if self.bMonochrome:
        #     oInputImage = self.monochrome_image(oInputImage)

        oImage, aaImage = self.reshape_image(oInputImage, (50,50))

        #get all the mosaics
        loMosaics, dMosaics = self.load_mosaics_from_file(self.sDirectory)

        aaMosaicedPic = self.assign_mosaics(aaImage, dMosaics)
        oMosaicedPic = self.create_image_from_array(aaMosaicedPic)

        if tFinalResize and (oMosaicedPic.size > tFinalResize):
            oMosaicedPic = oMosaicedPic.resize(tFinalResize)
        oMosaicedPic.save(self.sWritePath)

        print("time taken:  {} from {} images".format(datetime.datetime.now() - oBegin, self.iNrMosaicFiles))

        import pdb; pdb.set_trace()

