#!/Users/nagashima/anacaonda2/bin/python
import os,sys
from pyraf import iraf 

def main( fits ):
	fits_skysig	= fits[0:fits.rfind(".")] + "_skysig.fits" 
	sexpath	= "/Users/nagashima/astro/default/sextractor/object/default.sex" #set sextractor configure file path
	
	#make object mask image 
	fits_seg	= fits[0:fits.rfind(".")] + "_seg.fits" 
	cat_seg		= fits_seg[0:fits_seg.rfind(".")] + ".cat"
	dma		= 1.
	os.system("sex %s -c %s -DETECT_MINAREA %s -CHECKIMAGE_TYPE SEGMENTATION -CATALOG_NAME %s -CHECKIMAGE_NAME %s" % (fits,sexpath,dma,cat_seg,fits_seg)) 
	iraf.imreplace(images=fits_seg,value=1e06,lower=1.) 
	
	#use stack image  and only object image -> make skysigma image
	if os.path.exists(fits_skysig)  == True:
		os.system("rm %s" % fits_skysig)
	
	iraf.imarith(fits,"+",fits_seg,fits_skysig)
	
	print "ds9 %s &" % fits_skysig 
	return fits_skysig

if __name__ == "__main__":
	fits	= sys.argv[1] 	#stack image 
	main(fits)		#make skysigma image
