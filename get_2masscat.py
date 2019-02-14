#!/Users/nagashima/anaconda2/bin/python
from astropy.coordinates import SkyCoord
from astroquery.vo_conesearch import conesearch
from astroquery.vo_conesearch import conf
from astropy import units as u
import os,sys
import numpy as np
from astropy.io import ascii

def main( ra, dec, radius, output=False ):
	"""
	important params:
	'ra','dec','j_m','j_cmsig','j_msigcom','j_snr',h...,k....,'glon','glat'
	"""
	if output != False:
		if os.path.exists(output) == True:
			t	= ascii.read(output)
			return t

	conf.conesearch_dbname = 'conesearch_good'
	catalog 	= 'Two Micron All Sky Survey (2MASS) 1'
	c		= SkyCoord(ra=ra,dec=dec,unit="degree")
	t		= conesearch.conesearch(c, radius*u.degree, catalog_db=catalog).to_table()

	if len(t) == 0:
		print "No 2MASS Catalog (%s,%s,%s)" % (ra,dec,radius)
		return None

	t.rename_column('ra','RA')
	t.rename_column('dec','DEC')
	
	filt_ls	= ["J","H","K"]
	for filt in filt_ls:
		if filt in ["J","H"]:
			t.rename_column('%s_m'%filt.lower(),'%sMAG'%filt)
			t.rename_column('%s_cmsig'%filt.lower(),'%sMAGERR'%filt)

		elif filt == "K":
			t.rename_column('%s_m'%filt.lower(),'%ssMAG'%filt)
			t.rename_column('%s_cmsig'%filt.lower(),'%ssMAGERR'%filt)
		
	if output != False:
		ascii.write(t,output)

	#print t
	return t

if __name__ == "__main__":
	ra	= float(sys.argv[1])
	dec	= float(sys.argv[2])
	radius	= float(sys.argv[3])
	output	= sys.argv[4]
	tbl	= main(ra,dec,radius,output)
	#print tbl["JMAG"],tbl["HMAG"],tbl["KMAG"]
	#print tbl.columns
