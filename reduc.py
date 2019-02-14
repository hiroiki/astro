#/Users/nagashima/anaconda2/bin/python
from astropy.io import fits as pyfits 
import htconf as conf 
import os,sys
from pyraf import iraf

def main( fits ):
	rfits = os.path.basename(fits)
	if os.path.exists(rfits) == False:
		os.system("cp %s %s" % (fits,rfits))
	
	hd = pyfits.open(rfits)[0].header
	
	filter 	= hd["FILTER"]
	exp 	= float(hd["EXPTIME"])
	
	if exp.is_integer():
		exp_str = str(int(exp))
	else:
		exp_str = str(exp).replace(".","p")

	bsfits	= "%s/%s/bias.fits" % (conf.bias_dir,filter)
	
	dkfits	= "%s/%s/dark%s.fits" % (conf.dark_dir,filter,exp_str)
	if os.path.exists(dkfits) == False:
		dk1fits = dkfits[0:dkfits.rfind(".")] + "1.fits"
		iraf.imarith(dk1fits,"*",exp,dkfits)
		with pyfits.open(dkfits,"update") as h:
			hd = h[0].header
			hd["EXPTIME"] = exp
			h.flush()

	flfits	= "%s/%s/flat.fits" % (conf.flat_dir,filter)

	rfits_bs = rfits[0:rfits.rfind(".")] + "_bs.fits"
	iraf.imarith(rfits,"-",bsfits,rfits_bs)
	
	rfits_dk = rfits_bs[0:rfits_bs.rfind(".")] + "_dk.fits"
	iraf.imarith(rfits_bs,"-",dkfits,rfits_dk)

	rfits_fl = rfits_dk[0:rfits_dk.rfind(".")] + "_fl.fits"
	iraf.imarith(rfits_dk,"/",flfits,rfits_fl)

	os.system("rm %s %s %s" % (rfits,rfits_bs,rfits_dk))

	return rfits_fl

if __name__ == "__main__":
	fits = sys.argv[1]
	main(fits)
