#!/Users/nagashima/anaconda2/bin/python
from astropy.io import ascii
import os,sys
import date2mjd

def main( cat ):
	output	= cat[0:cat.rfind(".")] + "_new.cat"
	tbl	= ascii.read(cat)
	mjd_ls	= []
	for atbl in tbl:
		mjd	= date2mjd.main(atbl["DATE-OBS"],atbl["UT"])
		mjd_ls.append(mjd)
	tbl["MJD"] = mjd_ls
	ascii.write(tbl,output)

if __name__ == "__main__":
	cat	= sys.argv[1]
	main(cat)
