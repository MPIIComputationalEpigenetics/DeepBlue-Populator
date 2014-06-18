import os
import urllib2

import settings

def download(genome, type, url) :
	file_name = url.split('/')[-1]
	u = urllib2.urlopen(url)

	directory = os.path.join(settings.DOWNLOAD_PATH, genome, type)
	print directory
	if not os.path.exists(directory):
		os.makedirs(directory)

	file_path = os.path.join(directory, file_name)

	f = open(file_path, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break

	    file_size_dl += len(buffer)
	    f.write(buffer)
	    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
	    status = status + chr(8)*(len(status)+1)
	    print status,
	f.close()


download("hg19", "annotation", "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/rmsk.txt.gz")