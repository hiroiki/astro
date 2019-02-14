#!/Users/nagashima/anaconda2/bin/python

#reference:
#https://michaelmommert.wordpress.com/2017/02/13/accessing-the-gaia-and-pan-starrs-catalogs-using-python/
import requests 
from astropy.io.votable import parse_single_table 
import numpy as np
import os,sys,re
from astropy.io import ascii

def main( ra, dec, radius, output=False ): 
	"""
	import params:
	'objName','objID','raMean','decMean','epochMean','l','b','gMeanPSFMag','gMeanPSFMagErr','gMeanKronMag','gMeanKronMagErr','gMeanApMag','gMeanApMagErr',r...,i...,z...,y...
	"""

	if output != False:
		if os.path.exists(output) == True:
			t	= ascii.read(output)
			return t

	url = "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr1/mean.csv"

	
	basic_cols = 	[
		 	 'objname',
		 	 'objID',
		 	 'raMean',
			 'decMean',
			 'l',
			 'b',
		 	 'epochMean'
			]

	
	filt_ls	= ['g','r','i','z','y']

##Decide Specify Output Columns
#API release 2019/01/0?
#maybe reference not exist ( https://catalogs.mast.stsci.edu/docs/index.html  )
#checked on 2019/01/08
	
	"""
	mag_ls 	= 	[
			 'MeanPSFMag',
			 'MeanPSFMagErr'
			]
	
	mag_cols = 	[
			 filt + mag
			 for filt in filt_ls
			 	for mag in mag_ls
			]
	

	columns	= basic_cols + mag_cols
	"""

	#mag threshold
	rl	= -998.	#rband lowerlimit
	ru	= 18.	#rband upperlimit

	params	=	{
			 'ra':ra,
			 'dec':dec,
			 'radius':radius,
			 'format':'CSV',
			 'rMeanPSFMag.min':rl,
			 'rMeanPSFMag.max':ru
			 }


	r = requests.get(url,params=params) 

	t = ascii.read(r.text)
	
	if len(t) == 0:
		print "No PanSTARRS Catalog (%s,%s,%s)" % (ra,dec,radius)
		return None
	
	#original
	for name in t.columns:
		if re.match("\w*Mag$",name):
			select		= np.where(t[name]==-999.0)
			t[name][select] = np.nan

	t.rename_column('raMean','RA')
	t.rename_column('decMean','DEC')
	
	for filt in filt_ls:
		t.rename_column('%sMeanPSFMag'%filt, '%sMAG'%filt)
		t.rename_column('%sMeanPSFMagErr'%filt, '%sMAGERR'%filt)
	

	#grizy >> u,B,V,Rc,Ic(Lupton(2005))
	g	= t["gMAG"]
	r	= t["rMAG"]
	i	= t["iMAG"]
	z	= t["zMAG"]
	y	= t["yMAG"]

	#u
	t["uMAG"] 	= None
	t["uMAGERR"] 	= None
	c0	= 0.8116
	c1	= 0.1313
	c2	= 0.3130
	c3	= 0.2271
	
	A 	= 1/(c0-1)
	t["uMAG"] = ((c0-c2-1)*g+c2*r+c1-c3) * A

	#B
	t["BMAG"] 	= None
	t["BMAGERR"] 	= None
	c0	= 0.3130
	c1	= 0.2271

	t["BMAG"]	= g + c0*(g-r) + c1
	
	#V
	t["VMAG"] 	= None
	t["VMAGERR"] 	= None
	c0	= 0.5784
	c1	= 0.0038
	
	t["VMAG"]	= g - c0*(g-r) - c1

	#Rc
	t["RcMAG"] 	= None
	t["RcMAGERR"] 	= None
	c0	= 0.2936
	c1	= 0.1439

	t["RcMAG"]	= r - c0*(r-i) - c1
	
	#Ic
	t["IcMAG"] 	= None
	t["IcMAGERR"] 	= None
	c0	= 0.3780
	c1	= 0.3974
	
	t["IcMAG"]	= i - c0*(i-z) - c1
		
	if output != False:
		ascii.write(t,output)

	#print t
	return t

# Example query
if __name__ == "__main__":
	ra	= float(sys.argv[1])
	dec	= float(sys.argv[2])
	radius	= float(sys.argv[3])
	output	= sys.argv[4]
	t	= main(ra,dec,radius,output)
	#print t["gMAG"],t["rMAG"],t["iMAG"],t["zMAG"],t["yMAG"]
	#print t["uMAG"],t["BMAG"],t["VMAG"],t["RcMAG"],t["IcMAG"]
	#print t.columns
