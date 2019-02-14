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
	'RAJ2000','DEJ2000','B1mag','R1mag','B2mag','R2mag','Imag'
	"""
	if output != False:
		if os.path.exists(output) == True:
			t	= ascii.read(output)
			return t

	conf.conesearch_dbname = 'conesearch_warn'
	catalog 	= 'The USNO-B1.0 Catalog (Monet+ 2003) 1'
	c		= SkyCoord(ra=ra,dec=dec,unit="degree")
	t		= conesearch.conesearch(c, radius*u.degree, catalog_db=catalog).to_table()

	if len(t) == 0:
		print "No USNO-B1.0 Catalog (%s,%s,%s)" % (ra,dec,radius)
		return None

	name_ls	= ["B1mag","B2mag","R1mag","R2mag","Imag"]
	for name in name_ls:
		select		= np.ma.getmask(t[name])
		t[name][select] = np.nan
	
	t.rename_column('RAJ2000','RA')
	t.rename_column('DEJ2000','DEC')
	
	filt_ls	= ["B","R","I"]
	for filt in filt_ls:
		if filt in ["B","R"]:
			name1	= "%s1mag"%filt
			n1	= len(t[name1][~np.isnan(t[name1])])

			name2	= "%s2mag"%filt
			n2	= len(t[name2][~np.isnan(t[name2])])
			
			if filt == "R":filt="Rc"
				
			if n1 <= n2:
				t.rename_column(name2,'%sMAG'%filt)
			elif n2 < n1:
				t.rename_column(name1,'%sMAG'%filt)
		
		if filt == "I":
			t.rename_column("%smag"%filt,'%scMAG'%filt)

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
	#print tbl["BMAG"],tbl["RcMAG"],tbl["IcMAG"]
	#print tbl["B1mag"],tbl["B2mag"],tbl["R1mag"],tbl["R2mag"],tbl["Imag"]
	#print tbl.columns
