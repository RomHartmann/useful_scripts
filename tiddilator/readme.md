Tiddilator
Roman Hartmann
######################

This is the mighty tiddilator.  The tiddilator takes a source picture and replaces it with a black and white mosaic of the same picture and saves it.  The Mosaic database can be created from any picture set.  Included is an image scraper written for the purpose of creating such a database.


It has the following 2 specific functions:

a)  
It is an image scraper, and can be used to get the (google limited) top 20 image results from a google search
or it can just scrape all images if finds off any url you insert.
This code can be found in image_scraper.py, and can be used via command line or via import.
**Command Line:**
python image_scraper.py -gs puppies        #does a google search for puppies
python image_scraper.py -url https://www.facebook.com/    #grabs all images it can find on facebook home page

**import:**
from image_scraper import ImageScraper
ImageScraper(sURL, bSearch)   #if bSearch = True, sURL is a google search term.  If False, sURL is a normal url.

Thus this tool can be used to create the image database as a base for the mosaics, and creating the database first before tiddilating is easier.



b)
Secondly, the actual tiddilating.  Best used with square images, and only returns in black and white.  Best if the database has a wide collection of colours, bright and dark.  If there are a lot of colours in one spectrum, this tries to use all of them.  If there are none, the closest image is used.

This can also be called form command line or as package.

**Command Line:**
python run.py -p tom.png -d /home/roman/mosaics      #tiddilates Tom.png (situated in package dir) with the images in /home/roman/mosaics.  default size = (75,75)
python run.py -p tom.png -d /home/roman/mosaics -z "(100,200)"  #creates new image of size (100, 200) mosaics

**import:**
from tiddy import Tiddy
oT = Tiddy(sImagePath, sDirectory)  #sImagePath = full path to image, sDirectory is full path to mosaic directory
oT.tiddy_this_thang(tResize)

oT.get_mosaics_from_online(sURL, bSearch)  #same as ImageScraper above.





