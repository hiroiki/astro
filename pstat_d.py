#!/Users/nagashima/anaconda2/bin/python
from astropy.io import fits as pyfits 
import numpy as np
import os,sys
from astropy.io import ascii
from astropy.stats import sigma_clip
#from scipy import stats

def main( fits, x0, x1, y0, y1 ):
	x0	= int(np.round(x0,0))
	x1	= int(np.round(x1,0))
	y0	= int(np.round(y0,0))
	y1	= int(np.round(y1,0))

	#print x0,x1,y0,y1
	data 	= pyfits.open(fits)[0].data
	data	= data[y0-1:y1-1,x0-1:x1-1].flatten()

	image	= "%s[%d:%d,%d:%d]" % (fits,x0,x1-1,y0,y1-1)

	npix	= len(data)
	#print npix

	clip	= ~sigma_clip(data,sigma=3.,iters=5).mask
	data	= data[clip]

	npix	= len(data)
	#print npix2

	mean	= np.average(data)
	stddev	= np.std(data,ddof=1)
	
	midpt	= np.median(data)
		
	#mode	= stats.mode(np.round(data,2)).mode[0]
	
	max	= np.max(data)
	min	= np.min(data)

	d = {	
	     "IMAGE":image, 
	     "NPIX":npix, 
	     "MEAN":mean,
	     "STDDEV":stddev,
	     "MIDPT":midpt,
	     "MIN":min,
	     "MAX":max,
		} 
	print d
	return mean,midpt,stddev

if __name__ == "__main__":
	fits	= sys.argv[1]
	x0	= float(sys.argv[2])
	x1	= float(sys.argv[3])
	y0	= float(sys.argv[4])
	y1	= float(sys.argv[5])
	main(fits,x0,x1,y0,y1)
