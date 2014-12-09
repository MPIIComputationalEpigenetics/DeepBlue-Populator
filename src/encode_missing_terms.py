import xmlrpclib
from encode_vocabulary import ControledVocabulary


# Get the data from the main server
"""
url = "http://deepblue.mpi-inf.mpg.de/xmlrpc"
user_key = "ZHvRWHtlmZdQXH1X"
server = xmlrpclib.Server(url, encoding='UTF-8', allow_none=True)
server.echo(user_key)


def get_encode_terms():
	(a, b) = server.list_experiments("hg19", None, None, None, "ENCODE", user_key)
	bss = []
	for bb in b:
		(s, i) = server.info(bb[0], user_key)
		bss.append(i[0]["sample_info"]["biosource_name"])
	return list(set(bss))

encode_bss = get_encode_terms()
"""
encode_bss = ['HepG2', 'BC_Left_Ventricle_N41', 'PanIslets', 'HUVEC', 'GM18507', 'GM04503', 'BJ', 'BC_Stomach_01-11002', 'Medullo', 'Huh-7', 'Fibrobl_GM03348', 'pHTE', 'Adult_CD4_Th0', 'Adult_CD4_Th1', 'AG09309', 'U2OS', 'HBVP', 'HRPEpiC', 'WI-38', 'GM19193', 'RPTEC', 'Urothelia', 'Huh-7.5', 'BC_Placenta_UHN00189', 'Dnd41', 'PanIsletD', 'HMVEC-LLy', 'ProgFib', 'CD34+_Mobilized', 'GM04504', 'Stellate', 'HRCEpiC', 'FibroP_AG20443', 'GM12801', 'Monocytes-CD14+_RO01746', 'GM18505', 'BC_Pancreas_H12817N', 'Jurkat', 'HRE', 'AG09319', 'GM12871', 'HMF', 'BC_Kidney_01-11002', 'NH-A', 'HSMM_emb', 'SH-SY5Y', 'BC_Leukocyte_UHN00204', 'HAc', 'HMVEC-dBl-Neo', 'Melano', 'Treg_Wb78495824', 'SK-N-MC', 'HPDE6-E6E7', 'HeLa-S3', 'HEK293-T-REx', 'HTR8svn', 'HMVEC-dLy-Ad', 'CD20+', 'CMK', 'iPS_NIHi11', 'HPAEC', 'AoAF', 'GM12873', 'PFSK-1', 'WERI-Rb-1', 'NHDF-neo', 'HFF-Myc', 'RWPE1', 'Th1_Wb33676984', 'BC_Skeletal_Muscle_01-11002', 'NT2-D1', 'K562', 'HCPEpiC', 'HMVEC-LBl', 'BC_Testis_N30', 'iPS_CWRU1', 'HNPCEpiC', 'Th1_Wb54553204', 'Ishikawa', 'HA-sp', 'PBDE', 'bone_marrow_MSC', 'HL-60', 'GM08714', 'UCH-1', 'BC_Lung_01-11002', 'HMVEC-dNeo', 'Heart_OC', 'MCF-7', 'BC_Brain_H11058N', 'AG10803', 'HCF', 'BC_Breast_02-03015', '8988T', 'HMVEC-dLy-Neo', 'HBMEC', 'CD20+_RO01778', 'RPMI-7951', 'Osteobl', 'GM10248', 'HMEC', 'Cerebellum_OC', 'HRGEC', 'HCT-116', 'GM18526', 'HEEpiC', 'HConF', 'H1-neurons', 'GM19238', 'GM19239', 'PANC-1', 'SKMC', 'CD20+_RO01794', 'HCFaa', 'BE2_C', 'HEK293', 'PBMC', 'LNCaP', 'Cerebrum_frontal_OC', 'HMVEC-dAd', 'GM13977', 'GM13976', 'AoSMC', 'HFF', 'egg chorion', 'H9ES', 'SK-N-SH', 'BC_Adrenal_Gland_H12803N', 'GC_B_cell', 'HPAEpiC', 'Fibrobl', 'Hepatocytes', 'SK-N-SH_RA', 'Psoas_muscle_OC', 'NHLF', 'CLL', 'Mel_2183', 'GM15510', 'BC_Skeletal_Muscle_H12817N', 'GM06990', 'GM12878-XiMat', 'HSMMtube_FSHD', 'NB4', 'HBVSMC', 'bone_marrow_HS27a', 'HPdLF', 'Naive_B_cell', 'BC_Skin_01-11002', 'PBDEFetal', 'GM19240', 'Raji', 'U87', 'H1-hESC', 'bone_marrow_HS5', 'HMVEC-dBl-Ad', 'Monocytes-CD14+', 'Colo829', 'GM10266', 'HSMMtube', 'GM18951', 'ECC-1', 'Treg_Wb83319432', 'A549', 'SAEC', 'BC_Liver_01-11002', 'AG04449', 'HPAF', 'MCF10A-Er-Src', 'Th2', 'Th1', 'FibroP_AG08395', 'iPS', 'FibroP_AG08396', 'GM12872', 'GM20000', 'HA-h', 'CD4+_Naive_Wb78495824', 'Frontal_cortex_OC', 'iPS_NIHi7', 'ovcar-3', 'NHBE', 'IMR90', 'GM10847', 'Caco-2', 'Myometr', 'GM12869', 'GM12878', 'HVMF', 'GM12875', 'GM12874', 'NHBE_RA', 'GM12870', 'Th2_Wb54553204', 'GM19099', 'HSMM_FSHD', 'hypertrophic cardiomyopathy', 'Medullo_D341', 'H7-hESC', 'BC_Uterus_BN0765', 'AG04450', 'HSMM', 'PrEC', 'NHDF-Ad', 'Th17', 'GM12892', 'GM12891', 'HGF', 'CD4+_Naive_Wb11970640', 'HIPEpiC', 'HPF', 'LHCN-M2', 'BC_Pericardium_H12529N', 'HEK293T', 'NHEK', 'T-47D', 'FibroP', 'Th2_Wb33676984', 'HAEpiC', 'GM12868', 'Gliobla', 'M059J', 'Olf_neurosphere', 'GM12866', 'GM12867', 'GM12864', 'GM12865']

# Get the data from the local server
user_key = "1PJLRaJvOx8Ut1ns"
url = "http://localhost:31415"
server = xmlrpclib.Server(url, encoding='UTF-8', allow_none=True)
server.echo(user_key)

cache = {}
def is_in_ontology(term):
	if cache.has_key(term):
		return cache[term]
	s, t = server.is_biosource(term, user_key)
	value = (s == "okay")
	cache[term] = value
	return value

voc = ControledVocabulary()

m_terms = []
m_tissues = []
m_lineages = []

for term in voc.biosources:
	#if term["term"] not in encode_bss:
	#	continue

	term_name = term['term']

	if not is_in_ontology(term_name):
		if term.has_key('tissue'):
			tissue = term['tissue']
			if is_in_ontology(tissue):
				m_terms.append((term_name, tissue, True))
			else:
				m_terms.append((term_name, tissue, False))
		else:
			m_terms.append((term_name, "-", False))

	if term.has_key('tissue'):
		tissue = term['tissue']
		if not is_in_ontology(tissue):
			if term.has_key('lineage'):
				lineage = term['lineage']
				if is_in_ontology(lineage):
					m_tissues.append((tissue, lineage, True))
				else:
					m_tissues.append((tissue, lineage, False))

	if term.has_key('lineage'):
		lineages = term['lineage'].split(",")
		for lineage in lineages:
			if not is_in_ontology(lineage):
					m_lineages.append(lineage)


m_terms = list(set(m_terms))
m_tissues = list(set(m_tissues))
m_lineages = list(set(m_lineages))

m_terms.sort()
m_tissues.sort()
m_lineages.sort()

print
print '**Missing terms**'
print "'Term Name'\t'Similar names'\t'Partials Found'\t'Tissue'\t'Tissue Exists'"

for t in m_terms:
	term_name = t[0]
	tissue_name = t[1]
	tissue_found = t[2]
	similar = [x[1] for x in server.list_similar_biosources(term_name, user_key)[1][:5]]

	print "'%s'"%(term_name),
	print "\t",
	if similar:
		print "'%s'"%(','.join(similar)),
	else:
		print "'-'",
	print "\t",

	is_partial = True
	for s in term_name.split():
		if not is_in_ontology(s):
			is_partial = False
			break
	print is_partial,

	print "\t",
	print "'%s'"%(tissue_name),
	print "\t",
	print tissue_found,
	print

print
print '**Missing tissues**'
print "'Tissue Name'\t'Similar names'\t'Partials Found'\t'Lineage'\t'Lineage Exists'"
for t in m_tissues:
	tissue_name = t[0]
	lineage_name = t[1]
	lineage_found = t[2]
	similar = [x[1] for x in server.list_similar_biosources(tissue_name, user_key)[1][:5]]
	print "'%s'"%tissue_name,
	print "\t",
	if similar:
		print "'%s'"%(','.join(similar)),
	else:
		print "'-'",

	is_partial = True
	for s in tissue_name.split():
		if not is_in_ontology(s):
			is_partial = False
			break
	print is_partial,

	print "\t",
	print "'%s'"%(lineage_name),
	print "\t",
	print lineage_found,
	print

print

print '**Missing lineages**'
for t in m_lineages:
	lineage_name = t
	similar = [x[1] for x in server.list_similar_biosources(lineage_name, user_key)[1][:5]]
	print "'%s'"%lineage_name,
	print "\t",
	if similar:
		print "'%s'"%(','.join(similar)),
	else:
		print "'-'",

	is_partial = True
	for s in lineage_name.split():
		if not is_in_ontology(s):
			is_partial = False
			break
	print is_partial,
	print
