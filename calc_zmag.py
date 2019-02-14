#!/Users/nagashima/anaconda2/bin/python
import os,sys
from astropy.io import fits as pyfits
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import ascii
from astropy.stats import sigma_clip
import numpy as np
from matplotlib import pyplot as plt

#orignal module
import vega2ab 
import get_panscat
import get_sdsscat
import get_usnob1cat
import plot
import hist
import cat2reg
import coord2reg
import htconf as conf 

def main( fits ):
	sexpath	= "/Users/nagashima/astro/default/sextractor/object/default.sex"

	#set aperture by sextractor
	scat0	= fits[0:fits.rfind(".")] + "0.cat"
	
	with pyfits.open(fits) as h:
		hd = h[0].header
		
		if "NCOMBINE" in hd.keys()	:satur_cnt = conf.satur_cnt*hd["NCOMBINE"]
		else				:satur_cnt = conf.satur_cnt

	dma	= 50
	os.system("sex %s -c %s -DETECT_MINAREA %d -CATALOG_NAME %s" % (fits,sexpath,dma,scat0))
	st0	= ascii.read(scat0)
	st0 	= st0[
			(st0["FLAGS"]==0)		&
			(st0["X_IMAGE"] <= 2048) 	& 
			(0<st0["FLUX_APER"])		&
			(st0["FLUX_MAX"] < satur_cnt)
			]

	ascii.write(st0,scat0)
	
	fwhm_arr	= st0["FWHM_IMAGE"]
	fwhm		= np.mean(fwhm_arr)
	if len(fwhm_arr) == 1:fwhm_err	= 0.0
	elif 1 < len(fwhm_arr):fwhm_err	= np.std(fwhm_arr,ddof=1)/np.sqrt(len(fwhm_arr))

	if fwhm < 10.		:aperture	= fwhm*3.3
	elif 10. <= fwhm	:aperture	= fwhm*3.0

	##calculation
	#get source catalog
	pscale	= conf.pscale
	dma	= 5
	scat 		= fits[0:fits.rfind(".")] + ".cat"
	os.system("sex %s -c %s -DETECT_MINAREA %d -PHOT_APERTURES %s -SEEING_FWHM %s -PIXEL_SCALE %s -CATALOG_NAME %s" % (fits,sexpath,dma,aperture,fwhm*pscale,pscale,scat))
	st 	= ascii.read(scat)
	st 	= st[
			(st["FLAGS"]==0)		&
			(st["X_IMAGE"] <= 2048) 	&
			(0<st["FLUX_APER"])		&
			(st["FLUX_MAX"] < satur_cnt)
			]


	#get reference catalog
	hd	= pyfits.open(fits)[0].header	
	ra      = float(hd["CRVAL1"])
	dec     = float(hd["CRVAL2"])
	print ra,dec
	filt	= hd["FILTER"]

	x,y		= hd["NAXIS1"],hd["NAXIS2"]
	if x <= y:	a = y
	else:		a = x
	
	#1.1 => ra,dec about x,y accuracy [1/4:3/4,1/4:3/4] OK!
	radius  = pscale*a/3600 * 1.1 #degree
	print radius

	dir 	= os.path.dirname(os.path.abspath(fits))

	if filt in ["Ic","Rc"]	:catalog_ls	= ["PanSTARRS","SDSS","USNOB1"] #priority 1>2>3...
	elif filt == "u"	:catalog_ls	= ["SDSS","PanSTARRS"]		#priority 1>2>3...

	for i,catalog in enumerate(catalog_ls):
		rcat0	= "%s/%s.cat" % (dir,catalog.lower())
		if catalog == "PanSTARRS":
			rt 	= get_panscat.main(ra,dec,radius,rcat0)	
		elif catalog == "SDSS":
			rt	= get_sdsscat.main(ra,dec,radius,rcat0)
		elif catalog == "USNOB1":		
			rt	= get_usnob1.main(ra,dec,radius,rcat0)

		if rt is None	:continue
		rt	= rt[~np.isnan(rt["%sMAG"%filt])]	
		n	= len(rt)
		
		if n == 0	:continue
		
		m_ref	= rt["%sMAG"%filt]
		c_ref	= SkyCoord(ra=rt["RA"],dec=rt["DEC"],unit="degree")
		
		#src vs ref merge & get source catalog
		c_src	= SkyCoord(st["ALPHA_J2000"],st["DELTA_J2000"],unit="degree")
		idx, d2d, d3d = c_src.match_to_catalog_sky(c_ref)

		m_src     	= st["MAG_APER"]
		m_ref     	= m_ref[idx]

		#extraction
		derr		= pscale * 5
		d2d		= d2d.arcsec 
		upper	= 15.
		sel 	= np.where((d2d<derr) & (m_ref < upper))

		
		zmag_arr	= (m_ref - m_src)[sel]
		if len(zmag_arr) == 0	:
			if len(catalog) != i+1	:continue
			else			:return None
		elif len(zmag_arr) != 0:
			break
		

	rcat		= rcat0[0:rcat0.rfind(".")] + "_sel.cat"
	ascii.write(rt[idx][sel],rcat)
	coord2reg.main(rcat,'fk5')

	#clipping
	clip	= ~sigma_clip(zmag_arr,sigma=3).mask
	zmag_cl	= zmag_arr[clip]

	#calculation
	zmag		= np.mean(zmag_cl)
	if catalog == "USNOB1":
		zmag	= vega2ab.main(zmag,filt)
		
		filt_ls	= [filt for i in range(n)]
		m_src	= map(vega2ab.main,m_src,filt_ls)
		m_ref	= map(vega2ab.main,m_ref,filt_ls)

	n	= len(zmag_cl)
	if n == 1:zmag_err	= 0.0
	elif 1 < n:zmag_err	= np.std(zmag_cl,ddof=1)/np.sqrt(len(zmag_cl))

	#plot 
	if 2 <= n:
		pl	= plt.plot(m_src[sel][clip],m_ref[sel][clip],".",label="data")
		
		m_arr	= np.arange(np.min(m_src[sel][clip]),np.max(m_src[sel][clip])+0.1,0.1)
		plt.plot(m_arr,m_arr+zmag)
		
		png0	= fits[0:fits.rfind(".")] + "_zmag.png"
		plot.setsave("Instrument Mag","%s Mag"%catalog,"Zmag",png0)
		plt.clf()

	#hist# 4 = min bin sample num
	if 4 <= n:
		png1	= png0[0:png0.rfind(".")] + "d_hist.png"
		hist.main0(d2d[sel][clip],"d2d[arcsec]",png1)
		
	#magnitude calibration & save
	st["MAG_APER"]	= st["MAG_APER"] + zmag
	st["MAG_AUTO"]	= st["MAG_AUTO"] + zmag
	
	ascii.write(st,scat)
	cat2reg.main(scat,'fk5','NUMBER')

	#No.N magnitude 
	mag_aper	= np.sort(st["MAG_APER"])
	star_num	= len(mag_aper)
	N		= 10 #Number   
	
	#header update
	with pyfits.open(fits,'update') as h:
		hd = h[0].header
		
		hd.set("CATALOG",zmag,"ZMAG magnitude calculated cataloc")
		hd.set("ZMAG",zmag,"zero magnitude")
		hd.set("ZMAG_ERR",zmag_err,"ZMAG error")
		
		hd.set("STAR_NUM",star_num,"Number of star")
		hd.set("MAG_%d"%N,mag_aper[N-1],"No.%d magnitude"%N)

		hd.set("FWHM",fwhm,"brght and clear star FWHM (diameter)")
		hd.set("FWHM_ERR",fwhm_err,"FWHM error")
		hd.set("SEEING",fwhm,"equal to FWHM (diameter)")
		hd.set("APERTURE",aperture,"aperture (diameter)")
		
		h.flush()

	ascii.write(st,scat)
	cat2reg.main(scat,'fk5','NUMBER')
	
	print zmag,zmag_err,aperture
	return zmag,zmag_err,aperture

if __name__ == "__main__":
	fits	= sys.argv[1] #stack image
	main(fits)
