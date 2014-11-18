
import re
import os

from subprocess import call
from settings import DOWNLOAD_PATH, DEEPBLUE_HOST, DEEPBLUE_PORT, OS

uk = "9eMC40pPYBLTYU2b"

organs = {}
organs['Bl'] = 'Blood'
organs['Co'] = 'Colon'
organs['Il'] = 'Ileum'
organs['In'] = 'Intestine'
organs['LP'] = 'Lamina Propria'
organs['Li'] = 'Liver'
organs['SF'] = 'Synovial Fluid'
organs['WE'] = 'White Adipose Tissue (Epididymal)'
organs['WS'] = 'White Adipose Tissue (Subcutaneous)'
organs['WM'] = 'White Adipose Tissue (Mesenteric)'
organs['Br'] = 'Brown Adipose Tissue'
organs['Bm'] = 'Bone marrow'


cell_types = {}
cell_types['Ad'] = 'Adipocytes'
cell_types['CM'] = 'Central memory CD4+'
cell_types['Ec'] = 'Epithelial cells'
cell_types['EM'] = 'Effector memory CD4+'
cell_types['Fi'] = 'Fibroblasts'
cell_types['He'] = 'Hepatocytes'
cell_types['Ku'] = 'Kupffer cells'
cell_types['Ma'] = 'Macrophages'
cell_types['Mo'] = 'Monocytes'
cell_types['Mu'] = 'Mucosa'
cell_types['PM'] = 'Protective memory CD4+'
cell_types['Th'] = 'CD4+ T helper cells'

diseases = {}
diseases['CD'] = 'Crohn’s Disease'
diseases['Ct'] = 'normal Control'
diseases['C'] = 'Circadian Rhythm'
diseases['OA'] = 'Osteoarthritis'
diseases['OC'] = 'Stochastic Obesity (Control)'
diseases['OL'] = 'Stochastic Obesity (Lean)'
diseases['OO'] = 'Stochastic Obesity (Obese)'
diseases['RA'] = 'Rheumatoid Arthritis'
diseases['Sh'] = 'Steatohepatitis'
diseases['Si'] = 'Induced Steatosis'
diseases['SK'] = 'Steatohepatitis, Kupffer cell depleted'
diseases['St'] = 'Steatosis'
diseases['Tr'] = 'Treated'


subproject = "(?P<sample_id>\\d{2})"
specie = "(?P<specie>[a-zA-Z])"
sex = "(?P<sex>m|f)"
donor_numer = "(?P<donor_numer>\\d{2})"
orgam = "(?P<organ>[a-zA-Z]{2})"
cell_type = "(?P<cell_type>[a-zA-Z]{2})"
health_satus = "(?P<health_satus>[a-zA-Z0-9]{2,3})"
replicate = "(?P<replicate>\\d{2})"
library = "(?P<library>[a-zA-Z0-9]{4,8})"
sequencing_center = "(?P<sequencing_center>\w)"
tracking_process = "(?P<tracking_process>[a-zA-Z0-9]+)"
date = "(?P<date>[\d]{8})"
type = "(?P<type>bamcov\.seqDepthNorm|narrowPeak|broadPeak)"
format = "(?P<format>bb|bw)"

filename_re = subproject+"_"+specie+sex+donor_numer+"_"+orgam+cell_type+"_"+health_satus+"_"+library+"_"+sequencing_center + "\." + tracking_process + "\." + date + "\." + type + "\." + format

p = re.compile(filename_re)

d = "/Users/albrecht/mpi/DeepBlue-Populator/data/mouse/20140709/"
name = "44_Mm01_WEAd_C21_H3K27ac_F.THBv1.20140709.bamcov.seqDepthNorm.bw"

for filename in os.listdir(d):
	m = p.match(filename)
	print filename + " " + str(m)
	if not m:
		continue

	print m.group('sample_id')
	print m.group('specie')
	print m.group('sex')
	print m.group('donor_numer')
	organ = m.group('organ')
	cell_type = m.group('cell_type')
	print m.group('health_satus')
	print m.group('library')
	print m.group('sequencing_center')
	print m.group('tracking_process')
	print m.group('date')
	print m.group('type')
	format = m.group('format')
	print '-' * 20


	if format == "bw":
		print "../third_party/bigWigToWig."+OS + " " + d + filename + " " + d +  filename+".wig"
    	#call(["../third_party/bigWigToWig."+OS, d+filename, d+filename+".wig"])

    	server.set_biosource_scope('organ', 'cell_type', uk)
    	server.add_sample(cell_type, fields, user_key):
