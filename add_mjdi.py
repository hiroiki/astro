#!/Users/nagashima/anaconda2/bin/python
from astropy.io import ascii
import os,sys
import trans2mjd
from matplotlib import pyplot as plt
import htconf as conf

def main( cat ):
	output	= cat[0:cat.rfind(".")] + "_new.cat"
	tbl	= ascii.read(cat)
	tbl["MJDI"] = tbl["MJD"].astype(int)
	ascii.write(tbl,output)

if __name__ == "__main__":
	cat	= sys.argv[1]
	main(cat)
