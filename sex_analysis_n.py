#!/home/nagashima/anacaonda2/bin/python
import os,sys

#astropy
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import ascii
from astropy.vo import conf
from astropy.vo.client import conesearch
from astropy.vo.client import vos_catalog
from astropy.stats import sigma_clip

#useful anal
import numpy as np
import pylab
import pyfits
from pyraf import iraf

#calc Zmag class
class SubClass1:
	def __init__( self, fitspath, aperture ):
                self.fitspath       	= fitspath
		self.aperture		= aperture
		self.dir		= os.path.dirname(fitspath)
                self.hd         	= pyfits.open(self.fitspath)[0].header
                self.arm        	= self.hd["HN-ARM"]
                if self.arm == "opt":
                        self.band       = self.hd["WH_OPTF2"]
                elif self.arm   == "ira":
                        self.band       = self.hd["WH_IRAF2"]
                self.default_path   = "/mnt/data5/users/nagashima/default/default.sex"
		
	def clipper( self, clip_ls, clip_num ):
		clipper      = ~sigma_clip(clip_ls,sigma=clip_num).mask
		clip         = clip_ls[clipper]
		return clipper,clip

        def get_srccat( self ):
                srcZcat = os.path.join(self.dir,"srcZ.cat")
		if os.path.exists(srcZcat)==True:
			print "Pass1!!"
		else:
			print "Pass2!!"
                os.system("sex %s -c %s -CATALOG_NAME %s -PHOT_APERTURES %s -SEEING_FWHM %s" % (self.fitspath,self.default_path,srcZcat,self.aperture,self.fwhm) )
                self.srcZcat = ascii.read(srcZcat)

        def get_refcat( self ):
                ra      = float(self.hd["CRVAL1"])
                dec     = float(self.hd["CRVAL2"])
                center  = SkyCoord(ra,dec,unit="degree")
                good_db = vos_catalog.get_remote_catalog_db('conesearch_good')
                if self.arm == "opt":
			#opt catalog
			conf.conesearch_dbname = 'conesearch_warn'
			#my_catname = "SDSS DR8 - Sloan Digital Sky Survey Data Release 8 2"
			my_catname = "The USNO-B1.0 Catalog (Monet+ 2003) 1"

                elif self.arm == "ira":
			#ira catalog
                        conf.conesearch_dbname = 'conesearch_warn'
                        my_catname = '2MASS All-Sky Catalog of Point Sources (Cutri+ 2003) 1'
                radius  = 0.13 * u.degree #0.294*2048/3600

                result  = conesearch.conesearch(center=center, radius=radius, catalog_db=my_catname)
                self.refcat     =  result.to_table()

        def get_data( self  ):
                if self.arm     == "opt":
                        self.refcoord   = SkyCoord(self.refcat["RAJ2000"],self.refcat["DEJ2000"],unit="degree")
			if self.band in ["B","R"]:
                        	refmag          = self.refcat[self.band+"2mag"]
			elif self.band == "I":
				refmag		= self.refcat[self.band+"mag"]
                        self.derr       = 2.0
                        self.catalog    = "USNOB-1.0"
                elif self.arm   == "ira":
                        self.refcoord   = SkyCoord(self.refcat["RAJ2000"],self.refcat["DEJ2000"],unit="degree")
                        refmag          = self.refcat[self.band+"mag"]
                        self.derr       = 0.8
                        self.catalog    = "2MASS"
                self.srccoord   = SkyCoord(self.srcZcat["ALPHA_J2000"],self.srcZcat["DELTA_J2000"],unit="degree")

                self.idx, self.d2d, d3d = self.srccoord.match_to_catalog_sky(self.refcoord)
                self.srcmag     = self.srcZcat["MAG_APER"]
                self.refmag     = refmag[self.idx]
		#print self.srcmag,self.refmag	

	def judge_upper( self ):
                #opt
                if self.band    == "B":
                        self.upper      = 20.0
                elif self.band  == "R":
                        self.upper      = 19.5
		elif self.band	== "I":
			self.upper	= 19.8
                #ira
                elif self.band == "J":
                        self.upper = 16.5
                elif self.band == "H":
                        self.upper = 15.9
                elif self.band == "K":
                        self.upper = 15.1	

	def main( self ):
		self.get_srccat()
                self.get_refcat()
                self.get_data()
                d2d	= self.d2d.arcsec
                self.judge_upper()

                select  = np.where( ( d2d < self.derr ) & ( self.refmag < self.upper ) )

                Zmag                    = np.array((self.refmag - self.srcmag)[select])
                clipper,clip_Zmag  	= self.clipper(Zmag,3)

                self.Zmag    	= np.median(clip_Zmag)
                self.Zerr   	= np.std(clip_Zmag)
		self.star_N	= len(select[0])

class MainClass:
	def __init__( self, fitspath ):
		#basic parameter
		self.fitspath	= fitspath
		self.dir	= os.path.dirname(fitspath)
		self.default_path= "/mnt/data5/users/nagashima/default/default.sex"
		self.hd		= pyfits.open(self.fitspath)[0].header
		if "INSTRUME"in self.hd.keys():
			self.inst	= self.hd["INSTRUME"]
			if self.inst	== "HONIR":
				self.arm = self.hd["HN-ARM"]
				if self.arm 	== "ira":self.band	= self.hd["WH_OPTF2"]
				elif self.arm	== "opt":self.band	= self.hd["WH_IRAF2"]
			elif self.inst	== "HOWPol":
				self.arm	= "opt"
				self.band	= self.hd["FILTER2"]
		else:
			pass
	def set_aperture( self, cat ):
		#aperture set
		cat0	= os.path.join(self.dir,cat)
		os.system("sex %s -c %s -CATALOG_NAME %s >& /dev/null" % (self.fitspath,self.default_path,cat0))
	        cat0	 	= ascii.read(cat0)
		select		= np.where( (3 < cat0["FWHM_IMAGE"]) & (cat0["FWHM_IMAGE"]< 15) )
        	fwhm_ls         = cat0["FWHM_IMAGE"][select]
        	self.fwhm    	= np.average(fwhm_ls)
		if self.fwhm < 10:self.aperture		= self.fwhm*2.8
		elif 10 <= self.fwhm:self.aperture	= self.fwhm*3.2
		
		return self.fwhm,self.aperture

	def set_satur_val( self ):
		#set saturation level
		if self.inst == "HONIR":
			if self.arm == "opt"	:self.satur_val	= 30000.0
			elif self.arm == "ira"	:self.satur_val	= 8000.0

		elif self.hd["INSTRUME"] == "HOWPol":
			self.satur_val	= 40000.0

	def calc_Zmag( self ):
		#calc zero other functino
		sub1		= SubClass1(self.fitspath,self.aperture)
		sub1.main()
		self.star_N	= sub1.star_N
		self.Zmag	= sub1.Zmag
		self.Zerr	= sub1.Zerr
	"""
	def sex5( self ):
		fits_ls		= dict([(key,self.fitspath[0:self.fitspath.rfind(".")]+ext) for key,ext in zip(["src","ref","sub"],[".fits","_temp_remap.fits","_sub.fits"])])
		single_cat	= dict([(cat[0:cat.rfind(".")],os.path.join(self.dir,cat)) for cat in ["src.cat","ref.cat","sub.cat"]]) 
		fits_ls2	= dict([(key,self.fitspath[0:self.fitspath.rfind(".")]+ext) for key,ext in zip(["src2","ref2"],[".fits","_temp_remap.fits"])]) 
		double_cat	= dict([(cat[0:cat.rfind(".")],os.path.join(self.dir,cat)) for cat in ["src2.cat","ref2.cat"]]) 
				
		#single mode
		for key in ["src","ref","sub"]:
			os.system("sex %s -c %s -CATALOG_NAME %s -SATUR_LEVEL %s -PHOT_APERTURES %s -MAG_ZEROPOINT %s -SEEING_FWHM %s" % (fits_ls[key],self.default_path,single_cat[key],self.satur_val,self.aperture,self.Zmag,self.fwhm))
		#double mode
		for key in ["src2","ref2"]:
			os.system("sex %s,%s -c %s -CATALOG_NAME %s -SATUR_LEVEL %s -PHOT_APERTURES %s -MAG_ZEROPOINT %s -SEEING_FWHM %s" % (fits_ls2[key],fits_ls["sub"],self.default_path,double_cat[key],self.satur_val,self.aperture,self.Zmag,self.fwhm))
	"""

	def calc_upperlimit( self, skysigfits ):
		skysigpath	= os.path.join(self.dir,skysigfits)
		hd		= pyfits.open(skysigpath)[0].header

		#set region range
		one_side 		= round(0.5*self.aperture*np.sqrt(np.pi),0)
		iraf.imexam.ncstat 	= one_side
		iraf.imexam.nlstat 	= one_side
		area_unit          	= one_side*one_side

		#logical coord range
		log_xmin	= 1
		log_xmax	= float(hd["NAXIS1"])
		log_ymin	= 1
		log_ymax 	= float(hd["NAXIS2"])
		
		bias	= 65 #np.sqrt((maxfwhm=20*1.75)**2*np.pi)
		
		xmin	= log_xmin + bias
		xmax 	= log_xmax - bias
		ymin	= log_ymin + bias
		ymax	= log_ymax - bias
	
		length_x	= xmax - xmin
		length_y	= ymax - ymin
		print length_x,length_y
		
		sample_num = 1000 
		x = np.random.rand(sample_num)*length_x + bias
		y = np.random.rand(sample_num)*length_y + bias
		print len(x),len(y)
		
		coords = SkyCoord(x,y,0,representation="cartesian")
		print coords

		idx,d2d,d3d 	= coords.match_to_catalog_3d(coords,nthneighbor=2)
		required_d	= one_side*np.sqrt(2)
		print required_d
		select		= np.where(required_d < d3d)
		print d3d
		print select
		survived        = coords[select]
		points  	= np.c_[x,y][select][:len(survived)]
		
		ap_reg	= os.path.join(self.dir,"aperture.reg") #random apertures
		ap_tmp	= os.path.join(self.dir,"aperture.tmp") #imexam m  aperture template
		with open(ap_reg,"w") as f, open(ap_tmp,"w") as g:
			frame   = 1
			command = "m"
			for i,xy in enumerate(points):
				if i ==0:
					f.write("global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal roman\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nimage\n")
				x = round(xy[0],3)
				y = round(xy[1],3)
				tmp = "%s %s %s %s\n" % (x,y,frame,command)
				g.write(tmp)
				reg   = "circle(%s,%s,10)\n" % (x,y)
				f.write(reg)
	
		output		= os.path.join(self.dir,"aperture0.log")
		iraf.imexamine(input=skysigpath,imagecur=ap_tmp,use_display="no",keeplog="yes",logfile=output,Stdout=True,frame=1)
		log		= os.path.join(self.dir,"aperture.log")
		if os.path.exists(log):os.remove(log)
		else:pass

		os.system("sed -e \"1d\" %s > %s" % (output,log))
		os.remove(output)
		
		data	= ascii.read(log)
		print data.keys()
		select	= np.where(-200000. < data["MIN"])
		print select
		S	= (0.5*self.aperture)**2*np.pi

		mean_ls			= np.array(data["MEAN"][select]*S)

		clipper3	= ~sigma_clip(mean_ls,sigma=3).mask
		mean_clip	= mean_ls[clipper3]

		self.random_ap_num	= len(mean_clip)
		print mean_clip
		self.sigma	= np.std(mean_clip)
		print self.sigma
		self.upperlimit	= -2.5*np.log10(5*self.sigma) + self.Zmag
					
	def get_data( self, catalog ):
                cat     = ascii.read(catalog)
                
		num     = np.array(cat["NUMBER"])
                ra      = np.array(cat["ALPHA_J2000"])
                dec     = np.array(cat["DELTA_J2000"])
                mag     = np.array(cat["MAG_APER"])
                flux    = np.array(cat["FLUX_APER"])
		fluxM	= np.array(cat["FLUX_MAX"])
                fwhm    = np.array(cat["FWHM_IMAGE"])
		theta	= np.array(cat["THETA_IMAGE"])
                ellip   = np.array(cat["ELLIPTICITY"])
		sky	= np.array(cat["BACKGROUND"])
		thres	= np.array(cat["THRESHOLD"])
                Class   = np.array(cat["CLASS_STAR"])
                flags   = np.array(cat["FLAGS"])

                np_data         = np.array([num,ra,dec,mag,flux,fluxM,fwhm,theta,ellip,sky,thres,Class,flags])
                dict_data       = {"num":num,"ra":ra,"dec":dec,"mag":mag,"flux":flux,"fluxM":fluxM,"fwhm":fwhm,"theta":theta,"ellip":ellip,"sky":sky,"thres":thres,"class":Class,"flags":flags}
                return dict_data
	
	def get_target( self ,catalog, ra, dec ):
                self.wcs        = SkyCoord(ra,dec,unit="degree")
                cat             = ascii.read(catalog)
                coord           = SkyCoord(cat["ALPHA_J2000"],cat["DELTA_J2000"],unit="degree")
                dist            = self.wcs.separation(coord)
                target          = cat[np.argmin(dist)]

                num     = np.array(target["NUMBER"])
                ra      = np.array(target["ALPHA_J2000"])
                dec     = np.array(target["DELTA_J2000"])
                mag     = np.array(target["MAG_APER"])
                flux    = np.array(target["FLUX_APER"])
		fluxM	= np.array(target["FLUX_MAX"])
		fwhm    = np.array(target["FWHM_IMAGE"])
		theta	= np.array(target["THETA_IMAGE"])
                ellip   = np.array(target["ELLIPTICITY"])
		sky	= np.array(target["BACKGROUND"])
		thres	= np.array(target["THRESHOLD"])
                Class   = np.array(target["CLASS_STAR"])
                flags   = np.array(target["FLAGS"])

                np_data         = np.array([num,ra,dec,mag,flux,fluxM,fwhm,theta,ellip,sky,thres,Class,flags])
                dict_data       = {"num":num,"ra":ra,"dec":dec,"mag":mag,"flux":flux,"fluxM":fluxM,"fwhm":fwhm,"theta":theta,"ellip":ellip,"sky":sky,"thres":thres,"class":Class,"flags":flags}
                return dict_data

#to get skydata
def main( fitspath, skysigpath="skysig.fits" ):
	mycl	= MainClass(fitspath)
	mycl.set_aperture("src0.cat")
	mycl.set_satur_val()
	mycl.calc_Zmag()
	mycl.calc_upperlimit(skysigpath)

	#if os.path.exists("upperlimit.dat") == True:os.remove("upperlimit.dat")
	#with open("upperlimit","a") as f:
		#f.write("%1.2f %d %1.2f %1.2f %d %1.2f %1.2f\n" % (mycl.fwhm,mycl.star_N,mycl.Zmag,mycl.Zerr,mycl.aper_num,mycl.sigma,mycl.upperlimit))
	#mycl.sex5()

def make_skysigim( fitspath ):
	"""
	stdout	= iraf.imstat(images=fitspath,fields="npix,min,max,stddev,midpt,mode",Stdout=1)
	
	key_ls	= stdout[0].strip("#").split()
	val_ls	= map(float,stdout[1].split())
	data	= dict([(key,val) for key,val in zip(key_ls,val_ls)])
	if ( data["MIDPT"] < 1000 ) and ( data["MODE"] < 1000 ):
		fits_skypath	= fitspath
		print "Already substract sky!!"
	else:
		fits_skypath	= fitspath[0:fitspath.rfind(".")] + "_sk.fits"
		os.system("sex %s -c /mnt/data5/users/nagashima/default/default.sex -CHECKIMAGE_TYPE -BACKGROUND -CHECKIMAGE_NAME %s" % (fitspath,fits_skypath))
		print "Subtract sky!!"	
	"""
	objonlypath	= fitspath[0:fitspath.rfind("/")] + "/object_only.fits"
	skysigpath	= fitspath[0:fitspath.rfind("/")] + "/skysig.fits"
	if os.path.exists(objonlypath) == True	:os.remove(objonlypath)
	if os.path.exists(skysigpath)  == True	:os.remove(skysigpath)
	
	os.system("sex %s -c /mnt/data5/users/nagashima/default/default.sex -CHECKIMAGE_TYPE OBJECTS -CHECKIMAGE_NAME %s" % (fitspath,objonlypath))
	iraf.imreplace(images=objonlypath,value=-300000,lower=1)#not 0 not float so
	iraf.imarith(fitspath,"+",objonlypath,skysigpath)
	return skysigpath

if __name__ == "__main__":
	#make skysigfits
	"""
	f 	= open("source_new.lst","r")
	line	= f.read().split()
	f.close()
	for fitspath in line:
		skysigpath = make_skysigim(fitspath)
	"""

	#upperlimit
	f1	= open("source_new.lst","r")
	path_ls	= f1.read().split()
	f2 	= open("upperlimit.dat","w")
	for i,path in enumerate(path_ls):
		cl1	= MainClass(path)
		cl1.set_aperture()
		cl1.set_satur_val()
		cl1.calc_Zmag()
		cl1.calc_upperlimit("skysig.fits")
		if i == 0:f2.write("#path\tZmag\tZerr\tUpperlimit\n")
		f2.write("%s\t%1.2f\t%1.2f\t%1.2f\n" % (path, cl1.Zmag, cl1.Zerr, cl1.upperlimit))
	f1.close()
	f2.close()
	
		#main(fitspath,skysigpath)
		#srcpath	= os.path.join(mc1.dir,"src.cat")
		#mc1.main(srcpath,float(wcs[0],float(wcs[1])))
