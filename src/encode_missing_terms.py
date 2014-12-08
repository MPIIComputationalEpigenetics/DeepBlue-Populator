import xmlrpclib

from encode_vocabulary import ControledVocabulary

user_key = "47n5PooxPJ5PxAMd"
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

"""
for t in m_terms:
	term_name = t[0]
	tissue_name = t[1]
	tissue_found = t[2]
	similar = [x[1] for x in server.list_similar_biosources(term_name, user_key)[1][:5]]

	print print "'%s'"%(term_name),
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
"""

print '**Missing lineages**'
for t in m_lineages:
    lineage_name = t
    similar = [x[1] for x in server.list_similar_biosources(lineage_name, user_key)[1][:5]]
    print "'%s'" % lineage_name,
    print "\t",
    if similar:
        print "'%s'" % (','.join(similar)),
    else:
        print "'-'",

    is_partial = True
    for s in lineage_name.split():
        if not is_in_ontology(s):
            is_partial = False
            break
    print is_partial,
    print