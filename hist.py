#!/Users/nagashima/anaconda2/bin/python
from matplotlib import pyplot as plt
import numpy as np
from astropy.stats import scott_bin_width,freedman_bin_width,knuth_bin_width
from pandas import DataFrame
import os,sys

def calc_bin( data, mode ):
	n = len(data)
	if mode == "sqrt":
		bins 	= np.sqrt(n)
	elif mode == "sturges":
		bins	= np.log2(n) + 1
	elif mode == "scott":
		width,bins	= scott_bin_width(data,return_bins=True)
		bins	= len(bins)
	elif mode == "freedman":
		width,bins	= freedman_bin_width(data,return_bins=True)
		bins	= len(bins)
	elif mode == "knuth":
		width,bins	= knuth_bin_width(data,return_bins=True)
		bins	= len(bins)
	return bins
	
def main0( data, xtitle, output, mode="freedman" ):
	#df	= DataFrame({'val':data})
	#print df.describe()
	
	count		= int(len(data))
	mean		= np.average(data)
	std		= np.std(data,ddof=1)
	min		= np.min(data)
	q25,q50,q75	= np.percentile(data, [25,50,75])
	max		= np.max(data)
	
	val		= np.round([count,mean,std,min,q25,q50,q75,max],3)
	index		= ["count","mean","std","min","25%","50%","75%","max"]
	dfds		= DataFrame({"val":val},index=index)
	print dfds

	bins	= calc_bin(data,mode)

	fig, ax = plt.subplots(1,1)	
	#print ax
	plt.hist(data,ec='black',bins=bins)
	plt.grid(linestyle=":")
	
	bsname	= os.path.basename(output)
	idx	= bsname.rfind(".")
	plt.title(bsname[0:idx])
	plt.xlabel(xtitle)
	plt.ylabel("count")
	plt.text( 0.01, 0.99, dfds, horizontalalignment='left', verticalalignment='top', family='monospace', transform=ax.transAxes)
	#plt.text( 0.01, 0.99, df.describe(),horizontalalignment='left', verticalalignment='top', family='monospace', transform=ax.transAxes)
	plt.savefig(output,dpi=350)
	#plt.show()
	plt.clf()
	#plt.close("all")

if __name__ == "__main__":
	main()
