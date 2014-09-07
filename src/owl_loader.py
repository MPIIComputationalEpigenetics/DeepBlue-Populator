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
OwlClass = "{%s}Class" % Owl
OwlIntersectionOf = "{%s}intersectionOf" % Owl
OwlUnionOf = "{%s}unionOf" % Owl
OwlRestriction = "{%s}Restriction" % Owl
OwlSomeValuesFrom = "{%s}someValuesFrom" % Owl

RdfAbout = "{%s}about" % Rdf
RdfRDF = "{%s}RDF" % Rdf
RdfResource = "{%s}resource" % Rdf
RdfDescription = "{%s}Description" % Rdf


RdfsLabel = "{%s}label" % Rdfs
RdfsComment = "{%s}comment" % Rdfs
RdfsSubClass = "{%s}subClassOf" % Rdfs

OboFormalDefinition = "{%s}IAO_0000115" % Obo

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
		self.about = about
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

def process_restriction(_class_retriction, label, about, superclasses):
	_owl_on_property = _class_retriction.find(OwlSomeValuesFrom)
	if _owl_on_property is not None:
		_on_property = _owl_on_property.get(RdfResource)
		if _on_property is not None:
			superclasses.append(_on_property)

	_owl_some_value_of = _class_retriction.find(OwlSomeValuesFrom)
	if _owl_some_value_of is not None:
		_restriction = _owl_some_value_of.get(RdfResource)
		if _restriction is not None:
			superclasses.append(_restriction)
		else:
			owl_class = _owl_some_value_of.find(OwlClass)
			_class_intersection_of = owl_class.find(OwlIntersectionOf)
			if _class_intersection_of is not None:
				process_intersection_or_union_of(_class_intersection_of, label, about, superclasses)


def process_intersection_or_union_of(_class_intersection_of, label, about, superclasses):
	found = False
	for _class_equivalent_description in _class_intersection_of.findall(RdfDescription):
		_class_equivalent_description_about = _class_equivalent_description.get(RdfAbout)
		if _class_equivalent_description_about is not None:
			superclasses.append(_class_equivalent_description_about.encode('utf-8').strip())
			found = True
		else:
			print 'FFFFF not found _class_equivalent_description_about', label, about

	for _class_retriction in _class_intersection_of.findall(OwlRestriction):
		process_restriction(_class_retriction, label, about, superclasses)
		found = True

	for owl_class in _class_intersection_of.findall(OwlClass):
		found = False
		for _class_intersection_of in owl_class.findall(OwlIntersectionOf):
			process_intersection_or_union_of(_class_intersection_of, label, about, superclasses)
			found = True

		for _class_union_of in owl_class.findall(OwlUnionOf):
			process_intersection_or_union_of(_class_union_of, label, about, superclasses)
			found = True

		if not found:
			print 'CCCCCC not found _class_retriction', label, about

	if not found:
		print 'Not found content for the insersection or union', label, about

def load_classes(ontology, _file):
	log.info("Loading ontology " + ontology + " from file " + _file)

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
		for superclass in child.findall(RdfsSubClass):
			ref = superclass.get(RdfResource)
			if ref is not None:
				superclasses.append(ref.encode('utf-8').strip())

		_comment = child.find(RdfsComment)
		if _comment is not None and _comment.text is not None:
			comment = _comment.text.encode('utf-8').strip()
		else:
			comment = ""

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

		_intersectionOf = child.find(OwlIntersectionOf)
		if _intersectionOf is not None:
			print _intersectionOf

		for _equivalentClass in child.findall(OwlEquivalentClass):
			found = False
			for _class_retriction in _equivalentClass.findall(OwlRestriction):
				found = True
				process_restriction(_class_retriction, label, about, superclasses)

			for _class_equivalent_class in _equivalentClass.findall(OwlClass):
				for _class_intersection_of in _class_equivalent_class.findall(OwlIntersectionOf):
					found = True


				for	_class_union_of in _class_equivalent_class.findall(OwlUnionOf):
					process_intersection_or_union_of(_class_intersection_of, label, about, superclasses)
					found = True

				if not found:
					print 'Not found: _class_intersection_of or _class_union_of', label, about

			if not found:
				_resource = _equivalentClass.get(RdfResource)
				if _resource is not None:
					print 'equivalent to ', _resource.encode('utf-8').strip(), label, about
				else:
					print 'AAAAAAA not found _class_equivalent_class', label, about


		syns = list(set(syns))

		_class = Class(namespace, ontology, about, label, superclasses, formalDefinition, syns, comment, deprecated)
		classes.append(_class)

	return Ontology(ontology, address, imports, classes )


def insert_class(_class):
	_epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)
	extra_metadata = {"url":_class.about, "namespace":_class.namespace, "ontology":_class.ontology, "comment": _class.comment}
	status, _id = _epidb.add_bio_source(_class.label, _class.formalDefinition, extra_metadata, _class.user_key)
	for syn in _class.syns:
		status = _epidb.set_bio_source_synonym(_class.label, syn, _class.user_key)

def set_scope(_class):
	_epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)
	for parent in _class.superclasses_names:
		status = _epidb.set_bio_source_scope(parent, _class.label, _class.user_key)

def load_owl(user_key) :
	log.info("Loading ontologies")

	cl_classes = load_classes("CL", "../data/ontologies/cl.owl.gz")
	efo_classes = load_classes("EFO", "../data/ontologies/efo.owl.gz")
	uberon_classes = load_classes("uberon", "../data/ontologies/uberon.owl.gz")

	log.info("Merging ontologies")
	all_classes = {}
	all_classes_names= {}
	all_ontologies = [i for i in cl_classes.classes if i.label] + [i for i in efo_classes.classes if i.label] + [i for i in uberon_classes.classes if i.label]
	for _class in all_ontologies:
		all_classes[_class.about] = _class.label
		all_classes_names[_class.label] = _class

	total = len(all_ontologies)
	count = 0

	log.info("Linking references")
	for _class in all_ontologies:
		# Workaround to pass the user_key value
		_class.user_key = user_key

		for ref in _class.superclasses:
			if all_classes.has_key(ref):
				_class.superclasses_names.append(all_classes[ref])
			else:
				print "refence %s for the class '%s' not found" %(ref, _class.label)

	no_parents = []

	for _class in all_ontologies:
		if not _class.label:
			continue
		if not _class.superclasses_names:
			no_parents.append(_class)
		else :
			for parent in _class.superclasses_names:
				parent_class = all_classes_names[parent]
				parent_class.sub.append(_class)



	obsoletes = []
	for _class in no_parents:
		if  _class.label.startswith('obsolete') or _class.deprecated:
			obsoletes.append(_class)
		elif not _class.sub and not _class.syns:
			print _class.label, _class.ontology, _class.about, _class.syns

	print 'total: ', len(all_classes)
	print 'no parent and no obsolete', len(no_parents) - len(obsoletes)

	return
	total = len(all_ontologies)
	count = 0
	p = Pool(12)
	log.info("Inserting bio sources. Total of " + str(total) + " classes.")
	p.map(insert_class, all_ontologies, 1000)
	p.close()
	p.join()

	p = Pool(12)
	total = len(all_ontologies)
	count = 0
	log.info("Setting bio source scope.")
	p.map(set_scope, all_ontologies, 1000)
	p.close()
	p.join()


load_owl("")