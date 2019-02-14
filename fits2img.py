#!/Users/nagashima/anaconda2/bin/python
import pyds9 as pyd
import os,sys

def main( fits, ext="png" ):
	d	= pyd.DS9()
	#d.set("height 750")
	#d.set("width 1150")
	d.set("file %s" % fits)
	d.set("scale zscale")
	d.set("zoom to fit")

	img = fits[0:fits.rfind(".")] + ".%s"%ext
	d.set("saveimage %s %s" % (ext,img))
	
	d.set("exit")
if __name__ == "__main__":
	fits	= sys.argv[1]
	#ext	= sys.argv[2]
	main(fits)
