#!/Users/nagashima/anaconda2/bin/python
import os,sys
from astropy.io import fits as pyfits
import numpy as np

def main( fits, x, y ):
	x	= int(np.round(x,0))
	y	= int(np.round(y,0))
	
	data 	= pyfits.open(fits)[0].data
	cnt 	= data[y-1,x-1]
	
	print "(%s,%s) => %s" % (x,y,cnt)
	return cnt

if __name__ == "__main__":
	fits 	= sys.argv[1]
	x	= float(sys.argv[2])
	y	= float(sys.argv[3])
	main(fits,x,y)
