#!/Users/nagashima/anaconda2/bin/python
import os,sys
from matplotlib import pyplot as plt

def main0( x_arr, y_arr, label, line=False ):
	if line == False:plt.plot(x_arr,y_arr,".",label=label)	
	elif line == True:plt.plot(x_arr,y_arr,linewidth=0.5,label=label)
def main1( x_arr, y_arr, yerr, label ):
	plt.errorbar(x_arr,y_arr,yerr=yerr,fmt=".",label=label)
#def main():
#	pass

def setsave( xlabel, ylabel, title, output ):
	plt.legend()
	plt.grid(linestyle=":")
	#idx,idy = xlabel.rfind("["),ylabel.rfind("[")
	#plt.title("%s vs %s" % (xlabel[0:idx],ylabel[0:idy]))
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.savefig(output,dpi=350)

def clf():
	plt.clf()

if __name__ == "__main__":
	cat	= sys.argv[1]
	main(cat)
