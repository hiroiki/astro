#!/Users/nagashima/anaconda2/bin/python
from astropy.time import Time
import sys
import datetime

def main( date, utc="00:00:00" ):
	if "-" in date:
		date	= date.replace("-","")
	print date
	date	= datetime.datetime.strptime(date,"%Y%m%d")
	date	= datetime.datetime.strftime(date,"%Y-%m-%d")
	date	= Time("%sT%s"%(date,utc),format="isot",scale="utc")
	mjd	= date.mjd

	print mjd
	return mjd

if __name__ == "__main__":
	argc	= len(sys.argv)
	if argc	== 2:
		date	= sys.argv[1]
		main(date)
	elif argc == 3:
		date	= sys.argv[1]
		utc	= sys.argv[2]
		main(date,utc)
