import sys
import time
from colors import colors

# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100, printEnd = True):
	"""
	Call in a loop to create terminal progress bar
	@params:
	iteration   - Required  : current iteration (Int)
	total       - Required  : total iterations (Int)
	prefix      - Optional  : prefix string (Str)
	suffix      - Optional  : suffix string (Str)
	decimals    - Optional  : number of decimals in percent complete (Int) 
	barLength   - Optional  : character length of bar (Int) 
	printEnd    - Optional  : whether to print '\n' at end of iterations
	"""
	filledLength = int(round(barLength * iteration / float(total)))
	percents = round(100.00 * (iteration / float(total)), decimals)
	bar = colors.bold + '[' + colors.endc\
		+ colors.green + '+' * filledLength + colors.endc\
		+ colors.blue + '-' * (barLength - filledLength) + colors.endc\
		+ colors.bold + ']' + colors.endc
	sys.stdout.write('%s %s %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
	sys.stdout.flush()

	if iteration == total:
		if printEnd:
			print ""
		else:
			sys.stdout.write('\r'),
			sys.stdout.flush()

def test ():
	n = 10000
	prefix = "progress: "
#	printProgress(0, n, prefix = prefix, barLength = 20)
	for j in xrange(n):
		printProgress(j+1, n, prefix = prefix, barLength = 20)
		time.sleep(0.000002) #only slowing down here to see changes for this trivial example

if __name__ == "__main__":
	test()

