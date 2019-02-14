#!/Users/nagashima/anaconda2/bin/python
import pyds9 as pyd

def view( fits ):
	d	= pyd.DS9()
	d.set("height 600")
	d.set("width 600")
	d.set("file %s" % fits)
	d.set("scale zscale")
	d.set("zoom to fit")
	#d.set("crosshair")
	#d.set("cursor 10 10")
	a = d.get("imexam coordinate image")
	#a = d.get("imexam coordinate physical")
	#a = d.get("imexam coordinate fk5")
	print type(a)
	#rint a.split()
	#d.set("exit")

if __name__ == "__main__":
	fits	= "/Users/nagashima/astro/sample/PSN2016bau_J.fits"
	view(fits)
