#!/Users/nagashima/anaconda2/bin/python
import os,sys
from matplotlib import pyplot as plt


def main0( tbl, x_key, y_key, label ):
	plt.plot(tbl[x_key],tbl[y_key],".",label=label)

#def main():
#	pass

def setsave( xlabel, ylabel, output ):
	plt.legend()
	plt.grid(linestyle=":")
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title("%s vs %s" % (x_label,y_label))
	plt.savefig(output,dpi=350)

if __name__ == "__main__":
	cat	= sys.argv[1]
	main(cat)
