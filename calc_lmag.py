#!/Users/nagashima/anaconda2/bin/python
import os,sys
from astropy.io import fits as pyfits
from astropy.stats import sigma_clip
import numpy as np

#original
import hist
import calc_zmag
import mkskysig
import htconf as conf

def pphot( data, radius ):
	x_c,y_c	= radius,radius
	#print x_c, y_c

	cnt_ls	= []
	for y in range(len(data)):		
		for x in range(len(data[0])):
			if radius**2 < (x_c-x)**2 + (y_c-y)**2:continue
			cnt	= data[y,x]
			cnt_ls.append(cnt)
	
	cnt_arr	= np.array(cnt_ls)
	cnt_sum	= np.sum(cnt_arr)
	cnt_std	= np.std(cnt_arr,ddof=1)

	return cnt_sum

def main( fits ):
	zmag,zmag_err,aperture	= calc_zmag.main(fits)
	skysigfits		= mkskysig.main(fits)
	
	#get skysig image data, header 
	h	= pyfits.open(skysigfits)
	data	= h[0].data
	hd	= h[0].header
	h.close()

	if hd["INSTRUME"] == "HinOTORI": 
		#x_max	= hd["NAXIS1"]
		#y_max 	= hd["NAXIS2"]
		x_min	= 1
		x_max	= 2048
		y_min	= 1
		y_max	= 2048
	
	#get count(sum) of each random aperture 
	radius		= aperture/2.
	sigma_sky_ls	= []
	sky_cl_ls	= []

	reg	= skysigfits[0:skysigfits.rfind(".")] + ".reg"
	f0	= open(reg,"w")
	template	= "global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal roman\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nimage\n" 
	f0.write(template)
	
	#test
	#trial_num	= 3
	#sample_num	= 10
	#want
	trial_num	= 10
	sample_num	= 10000
	for i in range(trial_num):
		print i
		num 	= 100000
		x_arr	= np.random.randint(x_min,y_max+1,num)
		y_arr	= np.random.randint(y_min,y_max+1,num)
		sky_ls	= []
		n	= 0
		for x,y in zip(x_arr,y_arr):
			#print x,y
			#print i
			x_m	= int(np.floor(x - radius))
			y_m	= int(np.floor(y - radius))
			x_M	= int(np.ceil(x + radius))
			y_M	= int(np.ceil(y + radius)) 
				
			if (x_m < x_min) | (y_m < y_min):
				#print "kuso"
				continue
			if (x_max < x_M) | (y_max<y_M):
				#print "kuso"
				continue
			
			d	= data[y_m-1:y_M-1+1,x_m-1:x_M-1+1]
			if 1e06 < np.max(d):
				#print "kuso"
				continue
			
			sky	= pphot(d,radius)
			sky_ls.append(sky)
			n += 1
			#print n
			f0.write("circle(%s,%s,%s)\n" % (x,y,radius))
			if n == sample_num:
				#clipping aboutly
				sky_arr = np.array(sky_ls)
				clip	= ~sigma_clip(sky_arr,sigma=3,iters=5).mask
				sky_cl	= sky_arr[clip]
				
				#calculation
				sigma_sky		= np.std(sky_cl,ddof=1)

				if i == 0:
					png	= skysigfits[0:skysigfits.rfind(".")] + "_hist.png"
					hist.main0(sky_cl,"Star area sky count[cnt]",png)
				
				sigma_sky_ls.append(sigma_sky)
				sky_cl_ls.append(sky_cl)
				n	= 0
				break
	f0.close()
	#make all count data got histgram
	sky_all	= np.array([sky for sky in sky_cl for sky_cl in sky_cl_ls])

	png	= skysigfits[0:skysigfits.rfind(".")] + "_allhist.png"
	hist.main0(sky_all,"Star area sky count[cnt]",png)


	sky		= np.mean(sky_all)
	sky_err		= np.std(sky_all,ddof=1)/np.sqrt(len(sky_all))
	
	pscale		= conf.pscale
	sky2sky1	= 1/(np.pi*(radius*pscale)**2)
	sky1		= sky*sky2sky1
	sky1_err	= sky_err*sky2sky1
	
	if sky1 <= 0:
		mag_sky		= 0.0
		mag_sky_err	= 0.0
	else:
		mag_sky		= -2.5*np.log10(sky1) + zmag
		mag_sky_err	= np.sqrt((-2.5*sky1_err/(np.log(10)*sky1))**2 + zmag_err**2)

	sigma_sky	= np.mean(sigma_sky_ls)
	sigma_sky_err	= np.std(sigma_sky_ls,ddof=1)/np.sqrt(len(sigma_sky_ls))
	
	lmag		= -2.5*np.log10(3*sigma_sky) + zmag
	#lmag5		= -2.5*np.log10(5*sigma_sky) + zmag
	
	lmag_err		= np.sqrt((-2.5*sigma_sky_err/(np.log(10)*sigma_sky))**2 + zmag_err**2)
	
	dat	= fits[0:fits.rfind(".")] + ".dat"
	f1 = open(dat,"w")
	#f1.write("UL3\tUL5\tUL_ERR\tCSIG\tCSIG_ERR\tZMAG\tZMAG_ERR\tAPERTURE\n")
	#f1.write("%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (lmag,lmag5,lmag_err,sigma_sky,sigma_sky_err,zmag,zmag_err,aperture))
	f1.write("SKY\tSKY_ERR\tSKY1\tSKY1_ERR\tSIGMA_SKY\tSIGMA_SKY_ERR\tLMAG\tLMAG_ERR\tZMAG\tZMAG_ERR\n")
	f1.write("%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (sky,sky_err,sky1,sky1_err,sigma_sky,sigma_sky_err,lmag,lmag_err,zmag,zmag_err))
	f1.close()
	
	with pyfits.open(fits,'update') as h:
		hd	= h[0].header
		
		hd.set("SKY",sky,"sky mean count")
		hd.set("SKY_ERR",sky_err,"SKY error")
		hd.set("SKY1",sky1,"sky count/arcsec**2")
		hd.set("SKY1_ERR",sky1_err,"SKY1 error")
		hd.set("MAG_SKY",mag_sky,"sky bright magnitude")
		hd.set("MAG_SKY_ERR",mag_sky_err,"MAG_SKY error")			

		hd.set("SIGMA_SKY",sigma_sky,"star area sky sigma")
		hd.set("SIGMA_SKY_ERR",sigma_sky_err,"SIGMA_SKY error")
		hd.set("LMAG",lmag,"3sigma AB limit magnitude")
		hd.set("LMAG_ERR",lmag_err,"LMAG error")

		h.flush()

	print lmag,lmag_err
	return lmag,lmag_err
					
if __name__ == "__main__":
	fits			= sys.argv[1]#stack image
	main(fits)
