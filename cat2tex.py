#!/Users/nagashima/anaconda2/bin/python
from astropy.io import ascii
import os,sys

def main( cat, label='label', caption='caption' ):
	t = ascii.read(cat)
	
	latexdict = ascii.latex.latexdicts["template"]
	
	latexdict.pop("caption")
	#latexdict["caption"] 	= caption + "\label{%s}" % label.replace("_","|")
	
	latexdict["tabletype"]		= "table"
	#latexdict["preamble"]		= "\centering"
	latexdict["preamble"]		= "\centering\n\setlength{\doublerulesep}{0.4pt}"
	latexdict["tablealign"] 	= "H"
	latexdict["col_align"] 	 	= "c"*len(t.columns)
	latexdict["header_start"] 	= "\hline"
	latexdict["header_end"] 	= "\hline"
	
	#latexdict["data_start"] 	= "\hline"
	latexdict.pop("data_start")
	latexdict["data_end"] 		= "\hline"
		
	#latexdict["tablefoot"] 	= "\hline"
	#latexdict.pop("tablefoot")
	latexdict["tablefoot"]		= "\caption{%s}\n\label{%s}" % (caption,label.replace("_","|"))

	latexdict.pop("units")


	tex = cat[0:cat.rfind(".")] + ".tex"
	ascii.write(t,tex,Writer=ascii.Latex,latexdict=latexdict)
	##template
	#ascii.write(t,tex,Writer=ascii.Latex,latexdict=ascii.latex.latexdicts["tempate"])

	f = open(tex,"r")
	r = f.read().replace("_","\_")
	r = r.replace("|","_")
	f.close()
	
	os.system("rm %s" % tex)
	
	print r

	"""
	f = open(tex,"w")
	f.write(r)
	f.close()
	"""

if __name__ == "__main__":
	cat	= sys.argv[1]
	label	= sys.argv[2]
	main(cat,label)
