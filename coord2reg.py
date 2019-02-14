#!/Users/nagashima/anaconda2/bin/python
import os,sys
from astropy.io import ascii

def main( cat, mode, key="ID" ):#mode => fk5/image
	reg		= cat[0:cat.rfind(".")] + ".reg"
	tbl 		= ascii.read(cat)
	with open(reg,"w") as f:
		template    = "global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal roman\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n%s\n" % mode
		f.write(template)
		for i,atbl in enumerate(tbl):
			if key	== "ID":mark	= i
			else:		mark	= atbl[key]

			if mode	== "fk5":
				x = atbl["RA"]
				y = atbl["DEC"]
				f.write("circle(%s,%s,1.5\") # text={%s}\n" % (x,y,mark))
			elif mode == "image":
				x = atbl["X"]
				y = atbl["Y"]
				f.write("circle(%s,%s,1.5) # text={%s}\n" % (x,y,mark))
if __name__ == "__main__":
	cat	= sys.argv[1]
	mode	= sys.argv[2]
	main(cat,mode)

