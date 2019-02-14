#!/Users/nagashima/anaconda2/bin/python
from astropy.table import join
from astropy.io import ascii

def main( tbl_ls, output=False ):
	tbl	= tbl_ls[0] 
	for atbl in tbl_ls[1:]:
		tbl = join(tbl,atbl,join_type='outer')
	if output == False:pass
	else:
		ascii.write(tbl,output)
		print output 
	return tbl
