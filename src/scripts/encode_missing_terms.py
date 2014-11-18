import xmlrpclib
from encode_vocabulary import ControledVocabulary

user_key = "TzmSikRoYgEvYyz9"
url = "http://localhost:31415"
server = xmlrpclib.Server(url, encoding='UTF-8', allow_none=True)
server.echo(user_key)

def is_in_ontology(term):
	s, t = server.is_biosource(term, user_key)
	return s == "okay"

voc = ControledVocabulary()

m_terms = []
m_tissues = []
m_lineages = []
m_found_pieces = []

for term in voc.biosources:
	term_name = term['term']

	if not is_in_ontology(term_name):
		if term.has_key('tissue'):
			tissue = term['tissue']
			if is_in_ontology(tissue):
				m_terms.append((term_name, tissue, True))
			else:
				m_terms.append((term_name, tissue, False))

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
		lineages = term['lineage']
		for lineage in lineages:
			if not is_in_ontology(lineage):
					m_lineages.append(lineage)


m_terms = list(set(m_terms))
m_tissues = list(set(m_tissues))
m_lineages = list(set(m_lineages))
m_found_pieces = list(set(m_found_pieces))

m_terms.sort()
m_tissues.sort()
m_lineages.sort()
m_found_pieces.sort()

print
print '**Missing terms**'
print "Term Name\tSimilar names\tPartials Found\tTissue\tTissue Exists"

"""
for t in m_terms:
	term_name = t[0]
	tissue_name = t[1]
	tissue_found = t[2]
	similar = [x[1] for x in server.list_similar_biosources(term_name, user_key)[1][:5]]

	print term_name,
	print "\t",
	if similar:
		print ','.join(similar),
	else:
		print "-",
	print "\t",

	is_partial = True
	for s in term_name.split():
		if not is_in_ontology(s):
			is_partial = False
			break
	print is_partial,

	print "\t",
	print tissue_name,
	print "\t",
	print tissue_found,
	print
"""

print
print '**Missing tissues**'
print "Tissue Name\tSimilar names\tPartials Found\tLineage\tLineage Exists"
for t in m_tissues:
	tissue_name = t[0]
	lineage_name = t[1]
	lineage_found = t[2]
	similar = [x[1] for x in server.list_similar_biosources(tissue_name, user_key)[1][:5]]

	print tissue_name,
	print "\t",
	if similar:
		print ','.join(similar),
	else:
		print "-",

	is_partial = True
	for s in lineage_name.split():
		if not is_in_ontology(s):
			is_partial = False
			break
	print is_partial,

	print "\t",
	print lineage_name,
	print "\t",
	print lineage_found,
	print
"""
print
print '**Missing lineages**'
for t in m_lineages:
	print t

print '**Terms that were not found, but all its tokens were found**'
for t in m_found_pieces:
	print t
"""