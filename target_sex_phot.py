#!/home/nagashima/anaconda2/bin/python
from astropy.io import ascii
from astropy.coordinates import SkyCoord
import numpy as np
import target_ira_zero
import pyfits
from astropy.time import Time
import os,sys
import glob
import upperlimit

def sex_phot(zero,error,stackcat):
	src 	  = ascii.read(stackcat)
	srccoords = SkyCoord(src["ALPHA_J2000"],src["DELTA_J2000"],unit="degree")

	target 	= SkyCoord(287.63114,7.8977429,unit="degree")
	sample1	= SkyCoord(287.62955,7.8983132,unit="degree")
	sample2	= SkyCoord(287.65794,7.8851428,unit="degree")
	sample3 = SkyCoord(287.61966,7.8913336,unit="degree")

	real_ra		= np.array([target.ra.degree,sample1.ra.degree,sample2.ra.degree,sample3.ra.degree])
	real_dec	= np.array([target.dec.degree,sample1.dec.degree,sample2.dec.degree,sample3.dec.degree])
	real_wcs	= np.array([real_ra,real_dec])
	

	dist  	= target.separation(srccoords)
	dist1	= sample1.separation(srccoords)
	dist2	= sample2.separation(srccoords)
	dist3	= sample3.separation(srccoords)
	
	target_idx	= src[np.argmin(dist)]
	sample1_idx	= src[np.argmin(dist1)]
	sample2_idx	= src[np.argmin(dist2)]
	sample3_idx	= src[np.argmin(dist3)]

	data	= [target_idx,sample1_idx,sample2_idx,sample3_idx]
	
	target_mag	= data[0]["MAG_AUTO"] + zero
	sample1_mag	= data[1]["MAG_AUTO"] + zero
	sample2_mag	= data[2]["MAG_AUTO"] + zero
	sample3_mag	= data[3]["MAG_AUTO"] + zero
	mag 		= np.round(np.array([target_mag,sample1_mag,sample2_mag,sample3_mag]),decimals=2)
	
	target_magerr 	= data[0]["MAGERR_AUTO"]
	sample1_magerr	= data[1]["MAGERR_AUTO"]
	sample2_magerr	= data[2]["MAGERR_AUTO"]
	sample3_magerr	= data[3]["MAGERR_AUTO"]
	magerr_ls = np.sqrt(np.array([target_magerr,sample1_magerr,sample2_magerr,sample3_magerr])**2 + error**2)
	magerr = np.round(magerr_ls,decimals=3)

	target_FWHM 	= data[0]["FWHM_WORLD"]*3600
	sample1_FWHM 	= data[1]["FWHM_WORLD"]*3600
	sample2_FWHM 	= data[2]["FWHM_WORLD"]*3600
	sample3_FWHM	= data[3]["FWHM_WORLD"]*3600

	FWHM_ls = np.array([target_FWHM,sample1_FWHM,sample2_FWHM,sample3_FWHM])
	FWHM	= np.round(FWHM_ls,2)
	
	sys_ra	= np.array([data[0]["ALPHA_J2000"],data[1]["ALPHA_J2000"],data[2]["ALPHA_J2000"],data[3]["ALPHA_J2000"]])
	sys_dec	= np.array([data[0]["DELTA_J2000"],data[1]["DELTA_J2000"],data[2]["DELTA_J2000"],data[3]["DELTA_J2000"]])
	sys_wcs = np.array([sys_ra,sys_dec])

	factor_name 	= ["object","real_ra","real_dec","sys_ra","sys_dec","mag","magerr","fwhm"] 
	sokko_object	= ["target","comp1","comp2","comp3"]

	ascii.write((sokko_object,real_wcs[0],real_wcs[1],sys_wcs[0],sys_wcs[1],mag,magerr,FWHM),"sample.dat",names=factor_name)


	g = pyfits.open("GL191032+075314_Hw.fits")
	date = g[0].header["DATE-OBS"]
	#astro_t = Time(date,format="isot",scale="utc")
	#mjd = astro_t.mjd
	mjd = np.array([Time(date,format="isot",scale="utc").mjd])
	
	ascii.write((mjd),"mjd.dat",names=["mjd"])

if __name__ == "__main__":
	from pyraf import iraf
	path_ls = glob.glob("/mnt/data4a/users/nagashima/target/GL191032+075315/ira2/2017????")
	path_ls.sort()
	for path in path_ls:
		os.chdir(path)
		iraf.chdir(path)
		zero_ls  = target_ira_zero.Xmatch("stack","GL191032+075314_Hw.fits","H")
		zero	 = zero_ls[0]
		error	 = zero_ls[1]
		stackcat = zero_ls[2]
		#sex_phot(zero,error,stackcat)
		upperlimit.limitmag("skysig.fits",stackcat,zero,error)

