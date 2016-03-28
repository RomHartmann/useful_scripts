
def run(sImagePath, sDirectory):
    """run the function"""

    from tiddy import Tiddy

    oT = Tiddy(sImagePath, sDirectory)

    #oT.get_mosaics_from_online(dSearch)
    tResize = (75, 75)
    oT.tiddy_this_thang(tResize)






if __name__ == "__main__":

    # import argparse
    # oParser = argparse.ArgumentParser
    # oParser.add_argument('-p', '--picture', help="the name of the picture")
    # oParser.add_argument('-d', '--directory', help="name of directory of the mosaic pictures")

    # oArgs = oParser.parse_args()
    # sPicture = oArgs.picture
    # sDirectory = oArgs.directory

    # import os
    # sCWD = os.getcwd()
    # sImagePath = os.path.join(sCWD, sPicture)

    sImagePath = "/home/roman/work/useful_scripts/tiddy_this_pic/misha.jpg"

    sDirectory = "all_the_boobies"

    run(sImagePath, sDirectory)
