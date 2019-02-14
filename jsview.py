#!/Users/nagashima/anaconda2/bin/python
from astropy.io import ascii
import sys

def main( cat ):
	tbl	= ascii.read(cat)
	tbl.show_in_browser(jsviewer=True)

	return tbl

if __name__ == "__main__":
	cat	= sys.argv[1]
	main(cat)
