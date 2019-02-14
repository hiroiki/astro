#!/Users/nagashima/anaconda2/bin/python
import os,sys
from astropy.io import ascii

def main( cat, mode="image", key="NUMBER" ):
	reg		= cat[0:cat.rfind(".")] + ".reg"
	
	tbl 		= ascii.read(cat)
	with open(reg,"w") as f:
		template    = "global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal roman\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n%s\n" % mode
		f.write(template)
		for atbl in tbl:
			mark	= atbl[key]
			if mode	== "fk5":
				ra,dec 	= atbl["ALPHA_J2000"],atbl["DELTA_J2000"]
				f.write("circle(%s,%s,1.5\") # text={%s}\n" % (ra,dec,mark))
			elif mode == "image":
				x,y 	= atbl["X_IMAGE"],atbl["Y_IMAGE"]
				f.write("circle(%s,%s,1.5) # text={%s}\n" % (x,y,mark))

if __name__ == "__main__":
	cat	= sys.argv[1]
	mode	= sys.argv[2] #mode => image/fk5
	key	= sys.argv[3] #marker str
	main(cat,mode,key)
