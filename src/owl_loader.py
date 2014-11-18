import sys
import gzip
import xml.etree.ElementTree as ET

from multiprocessing import Pool

from client import EpidbClient
from settings import max_threads, DEEPBLUE_HOST, DEEPBLUE_PORT
#from db import mdb
from log import log

Efo = "http://www.ebi.ac.uk/efo/"
Rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
Rdfs = "http://www.w3.org/2000/01/rdf-schema#"
Owl = "http://www.w3.org/2002/07/owl#"
Obo = "http://purl.obolibrary.org/obo/"
OboInOwl = "http://www.geneontology.org/formats/oboInOwl#"

OwlClass = "{%s}Class" % Owl
OwlOntology = "{%s}Ontology" % Owl
OwlImports = "{%s}imports" % Owl
OwlDeprecated = "{%s}deprecated" % Owl
OwlEquivalentClass = "{%s}equivalentClass" % Owl
OwlIntersectionOf = "{%s}intersectionOf" % Owl
OwlUnionOf = "{%s}unionOf" % Owl
OwlRestriction = "{%s}Restriction" % Owl
OwlSomeValuesFrom = "{%s}someValuesFrom" % Owl
OwlOnClass = "{%s}onClass" % Owl
OwlAllValuesFrom = "{%s}allValuesFrom" % Owl
OwlHasValue = "{%s}hasValue" % Owl
OwlOnProperty = "{%s}onProperty" % Owl

RdfAbout = "{%s}about" % Rdf
RdfRDF = "{%s}RDF" % Rdf
RdfResource = "{%s}resource" % Rdf
RdfDescription = "{%s}Description" % Rdf


RdfsLabel = "{%s}label" % Rdfs
RdfsComment = "{%s}comment" % Rdfs
RdfsSubClass = "{%s}subClassOf" % Rdfs

OboFormalDefinition = "{%s}IAO_0000115" % Obo
HasRelationalAdjective = "{%s}UBPROP_0000007" % Obo

OboInOwlHasExactSynonym = "{%s}hasExactSynonym" % OboInOwl
OboInOwlHasOBONamespace = "{%s}hasOBONamespace" % OboInOwl
OboInOwlHasRelatedSynonym = "{%s}hasRelatedSynonym" % OboInOwl

# Specific Ontologies Attributes
EfoAlternativeTerm  = "{%s}alternative_term" % Efo
EfoDefinition = "{%s}definition" % Efo


class Ontology:
	def __init__(self, name, address, imports, classes):
		self.name = name
		self.address = address
		self.imports = imports
		self.classes = classes

	def __str__(self):
		s = "%s\t%s\t%s" % (self.name, self.address, self.imports)
		for _class in self.classes:
			s += repr(_class)
			s += "\n-----\n"
		return s

	def __repr__(self):
		s = "%s\t%s\t%s" % (self.name, self.address, self.imports)
		for _class in classes:
			s += repr(_class)
			s += "\n-----\n"
		return s


class Class:
	def __init__(self, namespace, ontology, about, label, superclasses, formalDefinition, syns, comment, deprecated):
		self.namespace = namespace
		self.ontology = ontology
		self.ontology_merges = []
		self.about = about
		self.about_merges = []
		self.label = label
		self.superclasses = superclasses
		self.superclasses_names = []
		self.formalDefinition = formalDefinition
		self.syns = syns
		self.comment = comment
		self.sub = []
		self.deprecated = deprecated

	def __str__(self):
		return "namespace %s\tontology %s\tabout %s\tlabel %s\tsuperclasses %s\tformaldefinition %s\tsysns %s\tcomment %s" % (self.namespace, self.ontology, self.about, self.label, self.superclasses, self.formalDefinition, self.syns, self.comment)

	def __repr__(self):
		return "namespace %s\tontology %s\tabout %s\tlabel %s\tsuperclasses %s\tformaldefinition %s\tsysns %s\tcomment %s" % (self.namespace, self.ontology, self.about, self.label, self.superclasses, self.formalDefinition, self.syns, self.comment)

def process_owl_class(_owl_class, label, about, superclasses):
	found = False
	for _class_intersection_of in _owl_class.findall(OwlIntersectionOf):
		process_intersection_or_union_of(_class_intersection_of, label, about, superclasses)
		found = True

	for _class_union_of in _owl_class.findall(OwlUnionOf):
		# The Union informs sub classes. We are looking for super classes here.
		#	process_intersection_or_union_of(_class_union_of, label, about, superclasses)
		found = True

	if not found:
		print 'Nothing found at process_owl_class', label, about

def process_restriction_sub(_class_retriction_sub, label, about, superclasses):
	found = False
	_owl_all_values_from_value = _class_retriction_sub.get(RdfResource)
	if _owl_all_values_from_value is not None:
		superclasses.append(_owl_all_values_from_value.encode('utf-8').strip())
		found = True

	for owl_class in _class_retriction_sub.findall(OwlClass):
		process_owl_class(owl_class, label, about, superclasses)
		found = True

	for _in_restriction in _class_retriction_sub.findall(OwlRestriction):
		process_restriction(_in_restriction, label, about, superclasses)
		found = True

	if not found:
		print 'Nothing found at process_restriction_sub'

def process_restriction(_class_retriction, label, about, superclasses):
	found = False

	is_accepted_property = False
	for _on_property in _class_retriction.findall(OwlOnProperty):
		_property = _on_property.get(RdfResource).encode('utf-8')

		if _property in on_propery_whitelist:
			is_accepted_property = True
		elif _property in on_propery_blacklist:
			is_accepted_property = False
		else:
			print 'onProperty ', _property, ' is not know. Insert into on_propery_blacklist or on_propery_blacklist'
			is_accepted_property = False

	if not is_accepted_property:
		return

	for _on_class in _class_retriction.findall(OwlOnClass):
		_resource = _on_class.get(RdfResource)
		if _resource is not None:
			superclasses.append(_resource.encode('utf-8').strip())
			found = True

	for _owl_all_values_from in _class_retriction.findall(OwlAllValuesFrom):
		process_restriction_sub(_owl_all_values_from, label, about, superclasses)
		found = True

	for _owl_has_value in _class_retriction.findall(OwlHasValue):
		process_restriction_sub(_owl_has_value, label, about, superclasses)
		found = True

	for _owl_some_value_of in _class_retriction.findall(OwlSomeValuesFrom):
		process_restriction_sub(_owl_some_value_of, label, about, superclasses)
		found = True

	if not found:
		print 'Nothing found at process_restriction', label, about

def process_intersection_or_union_of(_class_intersection_of, label, about, superclasses):
	found = False
	for _class_equivalent_description in _class_intersection_of.findall(RdfDescription):
		_class_equivalent_description_about = _class_equivalent_description.get(RdfAbout)
		if _class_equivalent_description_about is not None:
			superclasses.append(_class_equivalent_description_about.encode('utf-8').strip())
			found = True

	for _class_retriction in _class_intersection_of.findall(OwlRestriction):
		process_restriction(_class_retriction, label, about, superclasses)
		found = True

	for owl_class in _class_intersection_of.findall(OwlClass):
		process_owl_class(owl_class, label, about, superclasses)
		found = True

	if not found:
		print 'Not found content for the insersection or union', label, about, _class_intersection_of

def load_classes(ontology, _file):
	#log.info("Loading ontology " + ontology + " from file " + _file)

	file_type = _file.split(".")[-1]
  	if file_type == "gz":
  		binary = gzip.open(_file).read()
  		root = ET.fromstring(binary)
	else:
		tree = ET.parse(_file)
		root = tree.getroot()

	_header = root.find(OwlOntology)
	if _header is not None:
		address = _header.get(RdfAbout).encode('utf-8').strip()
	else:
		address = ""

	imports = []
	for _import in _header.findall(OwlImports):
		imports.append(_import.get(RdfResource).encode('utf-8').strip())

	classes = []

	for child in root.findall(OwlClass):
		_namespace = child.find(OboInOwlHasOBONamespace)
		if _namespace is not None:
			namespace = _namespace.text.encode('utf-8').strip()
		else:
			namespace = ""


		_about = child.get(RdfAbout)
		if _about is not None:
			about = _about.encode('utf-8').strip()
		else:
			about = ""

		_label = child.find(RdfsLabel)
		if _label is not None:
			label = _label.text.encode('utf-8').strip()
		else:
			label = ""

		if not label:
			continue

		superclasses = []

		for _subclass in child.findall(RdfsSubClass):
			ref = _subclass.get(RdfResource)
			if ref is not None:
				sub_ref = ref.encode('utf-8').strip()
				if sub_ref == _about:
					print 'This class (', label, ontology,') is a sub class of... itself!'
					continue
				superclasses.append(sub_ref)

			for _owl_class in _subclass.findall(OwlClass):
				process_owl_class(_owl_class, label, about, superclasses)
				found = True

			for _owl_restriction in _subclass.findall(OwlRestriction):
				process_restriction(_owl_restriction, label, about, superclasses)

		_comment = child.find(RdfsComment)
		if _comment is not None and _comment.text is not None:
			comment = _comment.text.encode('utf-8').strip()
		else:
			comment = ""


		for _equivalentClass in child.findall(OwlEquivalentClass):
			found = False

			for _class_retriction in _equivalentClass.findall(OwlRestriction):
				found = True
				process_restriction(_class_retriction, label, about, superclasses)

			for _class_equivalent_class in _equivalentClass.findall(OwlClass):
				for _class_intersection_of in _class_equivalent_class.findall(OwlIntersectionOf):
					process_intersection_or_union_of(_class_intersection_of, label, about, superclasses)
					found = True

				for	_class_union_of in _class_equivalent_class.findall(OwlUnionOf):
					# The Union informs sub classes. We are looking for super classes here.
					found = True

				if not found:
					print 'Not found: _class_intersection_of or _class_union_of', label, about

			if not found:
				_resource = _equivalentClass.get(RdfResource)
				if _resource is not None:
					pass
					print 'equivalent to ', _resource.encode('utf-8').strip(), label, about
				else:
					pass
					print 'AAAAAAA not found _class_equivalent_class', label, about

		_deprecated = child.find(OwlDeprecated)
		if _deprecated is not None and _deprecated.text is not None:
			deprecated = True
		else:
			deprecated = False

		_formalDefinition = child.find(OboFormalDefinition)
		if _formalDefinition is not None and _formalDefinition.text is not None:
			formalDefinition = _formalDefinition.text.encode('utf-8').strip()
		else:
			formalDefinition = ""

		_formalDefinition = child.find(EfoDefinition)
		if _formalDefinition is not None and _formalDefinition.text is not None:
			formalDefinition = _formalDefinition.text.encode('utf-8').strip()
		else:
			formalDefinition = ""

		syns = []

		for syn in child.findall(OboInOwlHasRelatedSynonym):
			syns.append(syn.text.encode('utf-8').strip())

		for syn in child.findall(OboInOwlHasExactSynonym):
			syns.append(syn.text.encode('utf-8').strip())

		for syn in child.findall(EfoAlternativeTerm):
			syns.append(syn.text.encode('utf-8').strip())

		for syn in child.findall(HasRelationalAdjective):
			syns.append(syn.text.encode('utf-8').strip())

		# Remove duplicates
		syns = list(set(syns))
		superclasses = list(set(superclasses))

		_class = Class(namespace, ontology, about, label, superclasses, formalDefinition, syns, comment, deprecated)
		if not _class.label.startswith('obsolete') and not _class.deprecated:
			classes.append(_class)

	return Ontology(ontology, address, imports, classes )


def load_blacklist() :
	#print 'loading blacklist terms (terms that arent biosources) from ontologies_blacklist.txt'
	f = open("ontologies_blacklist.txt")
	blacklist = []

	for term in f.readlines():
		blacklist.append(term.strip())

	return blacklist

def load_on_propery_lists() :
	f = open("on_property_black_list.txt")
	blacklist = []

	for term in f.readlines():
		blacklist.append(term.strip())

	f = open("on_property_white_list.txt")
	whitelist = []

	for term in f.readlines():
		whitelist.append(term.strip())

	return blacklist, whitelist

def filter_classes(classes, blacklist, count = 0):
	result = []
	for _class in classes:
		if _class.label in blacklist:
			continue
		result.append(_class)
		sub_result = filter_classes(_class.sub, blacklist, count + 1)
		result += sub_result
		result = list(set(result))
	return result

def load_owl(user_key):
	#log.info("Loading ontologies")

	cl_classes = load_classes("CL", "../data/ontologies/cl.owl.gz")
	efo_classes = load_classes("EFO", "../data/ontologies/efo.owl.gz")
	uberon_classes = load_classes("uberon", "../data/ontologies/uberon.owl.gz")

	all_classes = {}
	all_classes_names= {}
	all_ontologies = [i for i in cl_classes.classes if i.label] + [i for i in efo_classes.classes if i.label] + [i for i in uberon_classes.classes if i.label]

	for _class in all_ontologies:
		all_classes[_class.about] = _class.label
		all_classes_names[_class.label] = _class
	count = 0

	# Linking references
	for _class in all_ontologies:
		# Workaround to pass the user_key value
		_class.user_key = user_key

		for ref in _class.superclasses:
			if all_classes.has_key(ref):
				_class.superclasses_names.append(all_classes[ref])
			#else:
			#	print "refence %s for the class '%s' not found" %(ref, _class.label)

	no_parents = []

	# Build the relationship
	for _class in all_ontologies:
		if not _class.label:
			continue
		if not _class.superclasses_names:
			no_parents.append(_class)
		else :
			for parent in _class.superclasses_names:
				parent_class = all_classes_names[parent]
				parent_class.sub.append(_class)

		if _class.label in _class.syns:
			_class.syns.remove(_class.label)

	# Remove weird relationships, if the class is sub and synonym, remove the synonym
	for _class in [_class for _class in all_ontologies if _class.sub and _class.syns]:
		def is_in_sub(x):
			for sub in _class.sub:
				if x == sub.label:
					return True
			return False

		_class.syns = [x for x in _class.syns if not is_in_sub(x)]

	# Remove classes that are synonyms of other classes

	_synonymn_classes = []

	#print 'finding synonyms defined as classes'
	#All ontologies
	for _class in all_ontologies:
		# That have synonyms
		to_merge_syns = []
		to_merge_superclasses = []
		to_merge_about = []
		to_merge_ontology = []

		for synonym in _class.syns:
			# if there is a class with the same name as the synonym
			if all_classes_names.has_key(synonym):

				# Class with the same name of the synonym
				found = all_classes_names[synonym]

				# Dont do anything if the synonym is the name of its own class (Thanks, ontologies)
				if _class.about == found.about:
					continue

				# merge the found synonyms with the class that has the synonyms
				for found_syn in found.syns:
					if not found in _class.syns:
						to_merge_syns.append(found_syn)

				for superclass in found.superclasses:
					if not superclass in _class.superclasses:
						to_merge_superclasses.append(superclass)

				if found.about is not _class.about:
					to_merge_about.append(found.about)

				if found.ontology is not _class.ontology:
					to_merge_ontology.append(found.ontology)

				_synonymn_classes.append(found)

		if to_merge_syns:
			_class.syns = list(set(_class.syns + to_merge_syns))

		if to_merge_superclasses:
			_class.superclasses = list(set(_class.syns + to_merge_superclasses))

		if to_merge_about:
			_class.about_merges = list(set(_class.about_merges + to_merge_about))

		if to_merge_ontology:
			_class.ontology_merges = list(set(_class.ontology_merges + to_merge_ontology))

	#print 'total: ', len(all_classes)
	#print 'no_parent: ', len(no_parents)
	#print 'duplicated (synonym and class): ', len(_synonymn_classes)

	#for no_parent in no_parents:
	#	print no_parent.label, no_parent.ontology

	blacklist_terms = load_blacklist()
	full_blacklist_terms = blacklist_terms + _synonymn_classes
	#print 'filtering.. '

	biosources = filter_classes(no_parents, full_blacklist_terms)

	#print 'total biosources:', len(biosources)

	more_embrancing_cache = {}
	alread_in = {}

	def print_biosources(no_parents, biosources, f, parent = None, deep = 0):
		first_1 = True

		f.write('[')
		for _class in no_parents:
			if _class not in biosources:
				continue

			if not first_1:
				f.write(',')
			first_1 = False
			f.write('\n')
			f.write(' ' * (deep))
			f.write('{')
			f.write(' ' * (deep+1))
			f.write('"label": "%s",' %(_class.label))
			f.write(' ' * (deep+1))
			f.write('"about": "%s",' %(_class.about))
			f.write(' ' * (deep+1))
			f.write('"synonyms": [')
			first_2 = True
			for syn in _class.syns:
				if not alread_in.has_key(syn):
					if not first_2:
						f.write(',')
					f.write('"%s"' %syn)
					first_2 = False

			f.write('],')

			f.write(' ' * (deep+1))
			f.write('"subs":')
			print_biosources(_class.sub, biosources, f, _class, deep + 1)

			f.write(' ' * (deep))
			f.write('}')
		f.write(']\n')

	def insert_biosources(no_parents, biosources, parent = None, deep = 0):
		_epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

		for _class in no_parents:
			if _class not in biosources:
				continue

			insert = False
			if not alread_in.has_key(_class.label):
				print '#' * deep, _class.label,
				extra_metadata = {"url":_class.about, "namespace":_class.namespace, "ontology":_class.ontology, "comment": _class.comment}
				status, _id = _epidb.add_biosource(_class.label, _class.formalDefinition, extra_metadata, _class.user_key)
				alread_in[_class.label] = True
				if status == 'error':
					print _id
				insert = True

			if insert and _class.syns:
				print '(',

			first = True
			for syn in _class.syns:
				if not alread_in.has_key(syn) :
					if not first:
						print ',',

					if insert:
						print syn,
					else:
						if first:
							print 'Synonymous for ',_class.label, ':', syn
						print ',',syn,
					status, _id = _epidb.set_biosource_synonym(_class.label, syn, _class.user_key)
					if status == 'error' and not _id.startswith('104400'):
						print _id
					alread_in[syn] = True
					first = False

			if insert and _class.syns:
				print ')'

			elif insert:
				print

			if parent:
				cache_key = parent.label + " " + _class.label
				if not more_embrancing_cache.has_key(cache_key):
					status, _id = _epidb.set_biosource_scope(parent.label, _class.label, _class.user_key)

					if status == 'okay':
						more_embrancing_cache[cache_key] = True

					elif status == 'error' and _id.startswith('104901'):
						more_embrancing_cache[cache_key] = True

					else:
						print _id

			insert_biosources(_class.sub, biosources, _class, deep + 1)

	#print '{ "data":'
	#print_biosources(no_parents, biosources)
	#print '}'

	print "Output json"
	f = open("imported_biosources.json", "w+")
	print_biosources(no_parents, biosources, f)
	#insert_biosources(no_parents, biosources)

on_propery_blacklist, on_propery_whitelist = load_on_propery_lists()


load_owl("")

