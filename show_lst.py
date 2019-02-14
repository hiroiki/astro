#!/Users/nagashima/anaconda2/bin/python
import os,sys

def main( lst ):
	f 	= open(lst,"r")
	r	= f.read()
	f.close()
	r	= r.replace("\n"," ")
	print "ds9 %s&" % r

if __name__ == "__main__":
	lst	= sys.argv[1]
	main(lst)
