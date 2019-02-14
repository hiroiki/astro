import sys

def main( day ):
	print "day\t = %s\t[day]" % day
	hour	= day * 24.
	min	= hour * 60.
	sec	= min * 60.
	print "hour\t = %s\t[hour]" % hour
	print "min\t = %s\t[min]" % min
	print "sec\t = %s\t[sec]" % sec

if __name__ == "__main__":
	day = float(sys.argv[1])
	main(day)
