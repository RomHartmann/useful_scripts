
def run(sImagePath, sDirectory, tResize):
    """run the function"""

    from tiddy import Tiddy

    oT = Tiddy(sImagePath, sDirectory)

    oT.tiddy_this_thang(tResize)









if __name__ == "__main__":

    import argparse
    import ast
    oParser = argparse.ArgumentParser()
    oParser.add_argument('-p', '--picture', help="the name of the picture")
    oParser.add_argument('-d', '--directory', help="name of directory of the mosaic pictures")
    oParser.add_argument('-z', '--size', default=None, help="size of image")

    oArgs = oParser.parse_args()
    sPicture = oArgs.picture
    sDirectory = oArgs.directory

    tDefaultSize = (75,75)
    tSize = ast.literal_eval(oArgs.size) if oArgs.size is not None else tDefaultSize

    import os
    sCWD = os.getcwd()
    sImagePath = os.path.join(sCWD, sPicture)


    run(sImagePath, sDirectory, tSize)
