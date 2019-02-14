#!/Users/nagashima/anaconda2/bin/python
from astropy.io import fits as pyfits 
import sys
import imstat_d

def main( fits, x_c, y_c, a=200. ):
	x0,x1	= x_c - a/2.,x_c + a/2.
	y0,y1	= y_c - a/2.,y_c + a/2.
	d	= imstat_d.main(fits,x0,x1,y0,y1)
	
	return d

if __name__ == "__main__":
	fits	= sys.argv[1]
	x_c	= float(sys.argv[2])
	y_c	= float(sys.argv[3])
	main(fits,x_c,y_c)
