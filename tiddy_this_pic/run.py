
def run(sImagePath, sCategory):
    """run the function"""

    from tiddy import Tiddy

    oT = Tiddy(sImagePath, sCategory)

    #oT.get_mosaics_from_online()
    oT.tiddy_this_thang()

    # loMosaics = oT.load_mosaics_from_file()






if __name__ == "__main__":

    # import argparse
    # oParser = argparse.ArgumentParser
    # oParser.add_argument('-p', '--picture', help="the name of the picture")
    # oParser.add_argument('-c', '--category', help="the name of the google image search category")
    #
    # oArgs = oParser.parse_args()
    # sPicture = oArgs.picture
    # sCategory = oArgs.category

    # import os
    # sCWD = os.getcwd()
    # sImagePath = os.path.join(sCWD, sPicture)

    sImagePath = "/home/roman/work/useful_scripts/tiddy_this_pic/tom.png"
    sCategory = "puppies"

    run(sImagePath, sCategory)
