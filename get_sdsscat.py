#!/Users/nagashima/anaconda2/bin/python
from astroquery.sdss import SDSS 
from astropy.coordinates import SkyCoord
from astropy import units
import os,sys,re
import numpy as np
from astropy.io import ascii

def main( ra, dec, radius, output=False ):
	if output != False:
		if os.path.exists(output) == True:
			t	= ascii.read(output)
			return t
	
	c	= SkyCoord(ra=ra,dec=dec,unit="degree")
	t	= SDSS.query_region(coordinates=c,radius=radius*units.degree,\
			photoobj_fields=['objID','ra','dec','psfMag_u',\
			'psfMagErr_u','psfMag_g','psfMagErr_g','psfMag_r',\
			'psfMagErr_r','psfMag_i','psfMagErr_i','psfMag_z',\
			'psfMagErr_z'])

	filt_ls	= ['u','g','r','i','z']

	if t == None:
		print "No SDSS Catalog (%s,%s,%s)" % (ra,dec,radius)
		return None

	for name in t.columns:
		if re.match("\w*Mag_.$",name):
			select		= np.where(t[name]==-9999.0)
			t[name][select] = np.nan
	
	t.rename_column('ra','RA')
	t.rename_column('dec','DEC')
	
	for filt in filt_ls:
		t.rename_column('psfMag_%s'%filt, '%sMAG'%filt)
		t.rename_column('psfMagErr_%s'%filt, '%sMAGERR'%filt)
	
	#ugriz >> B,V,Rc,Ic(Lupton(2005))
	u	= t["uMAG"]
	g	= t["gMAG"]
	r	= t["rMAG"]
	i	= t["iMAG"]
	z	= t["zMAG"]
	#print u,g,r,i,z

	#B
	t["BMAG"] 	= None
	t["BMAGERR"] 	= None
	c0	= 0.8116
	c1	= 0.1313

	t["BMAG"]	= u - c0*(u-g) + c1
	
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

if __name__ == "__main__":
	ra	= float(sys.argv[1])
	dec	= float(sys.argv[2])
	radius	= float(sys.argv[3])
	output	= sys.argv[4]
	t	= main(ra,dec,radius,output)
	#print t["uMAG"],t["gMAG"],t["rMAG"],t["iMAG"],t["zMAG"]
	#print t["BMAG"],t["VMAG"],t["RcMAG"],t["IcMAG"]
	#print t.columns
