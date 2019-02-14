#!/Users/nagashima/anaconda2/bin/python
from pyraf import iraf
from astropy.io import fits as pyfits 
import sys

def main( fits, x0, x1, y0, y1 ):
	x0	= int(round(x0,0))
	x1	= int(round(x1,0))
	y0	= int(round(y0,0))
	y1	= int(round(y1,0))

	reg		= "[%d:%d,%d:%d]" % (x0,x1-1,y0,y1-1)
	key_ls		= ["IMAGE","NPIX","MEAN","STDDEV","MIDPT","MODE","MIN","MAX"]
	fields		= ",".join(key_ls).lower()
	result		= iraf.imstat(fits+reg,Stdout=1,nclip=5,lsigma=3.,usigma=3.,fields=fields,format="no")
	#result		= iraf.imstat(fits+reg,Stdout=1,fields=fields,format="no")
	val_ls	= [float(val) if str(val).replace(".","").isdigit() else str(val) for val in result[0].split()]
	d	= dict([(key,val) for key,val in zip(key_ls,val_ls)])
	
	print d
	return d

if __name__ == "__main__":
	fits	= sys.argv[1]
	x0	= float(sys.argv[2])
	x1	= float(sys.argv[3])
	y0	= float(sys.argv[4])
	y1	= float(sys.argv[5])
	main(fits,x0,x1,y0,y1)
