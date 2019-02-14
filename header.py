#!/Users/nagashima/anaconda2/bin/python
from astropy.io import fits as pyfits
import os,sys

def main( fits ):
	hd = pyfits.open(fits)[0].header
	i  = 0
	for key in hd.keys():
		if key == "COMMENT":
			print "%s %s" % (key,hd[key][i])
			i += 1
			continue
		elif key == "":
			continue
		
		else:
			print "%s = %s / %s" % (key,hd[key],hd.comments[key]) 

if __name__ == "__main__":
	fits	= sys.argv[1]
	main(fits)
