#!/Users/nagashima/anaconda2/bin/python
from astropy.io import fits as pyfits 
import sys
import pstat_d

def main( fits, a=200. ):
	hd	= pyfits.open(fits)[0].header
	x_c,y_c	= hd["NAXIS1"]/2.,hd["NAXIS2"]/2.
	x0,x1	= x_c - a/2.,x_c + a/2.
	y0,y1	= y_c - a/2.,y_c + a/2.
	d = pstat_d.main(fits,x0,x1,y0,y1)
	
	return d

if __name__ == "__main__":
	fits	= sys.argv[1]
	main(fits)
