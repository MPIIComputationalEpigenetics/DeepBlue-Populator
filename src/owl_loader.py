import sys
from multiprocessing import Pool
import xml.etree.ElementTree as ET

from client import EpidbClient

from settings import mdb, log, max_threads, DEEPBLUE_HOST, DEEPBLUE_PORT

Rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
Rdfs = "http://www.w3.org/2000/01/rdf-schema#"
Owl = "http://www.w3.org/2002/07/owl#"
Obo = "http://purl.obolibrary.org/obo/"
OboInOwl = "http://www.geneontology.org/formats/oboInOwl#"

OwlClass = "{%s}Class" % Owl
OwlOntology = "{%s}Ontology" % Owl
OwlImports = "{%s}imports" % Owl


RdfAbout = "{%s}about" % Rdf
RdfRDF = "{%s}RDF" % Rdf
RdfResource = "{%s}resource" % Rdf

RdfsLabel = "{%s}label" % Rdfs
RdfsComment = "{%s}comment" % Rdfs
RdfsSubClass = "{%s}subClassOf" % Rdfs

OboFormalDefinition = "{%s}IAO_0000115" % Obo

OboInOwlHasExactSynonym = "{%s}hasExactSynonym" % OboInOwl
OboInOwlHasOBONamespace = "{%s}hasOBONamespace" % OboInOwl

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
	def __init__(self, namespace, ontology, about, label, superclasses, formalDefinition, syns, comment):
		self.namespace = namespace
		self.ontology = ontology
		self.about = about
		self.label = label
		self.superclasses = superclasses
		self.superclasses_names = []
		self.formalDefinition = formalDefinition
		self.syns = syns
		self.comment = comment

	def __str__(self):
		return "namespace %s\tontology %s\tabout %s\tlabel %s\tsuperclasses %s\tformaldefinition %s\tsysns %s\tcomment %s" % (self.namespace, self.ontology, self.about, self.label, self.superclasses, self.formalDefinition, self.syns, self.comment)

	def __repr__(self):
		return "namespace %s\tontology %s\tabout %s\tlabel %s\tsuperclasses %s\tformaldefinition %s\tsysns %s\tcomment %s" % (self.namespace, self.ontology, self.about, self.label, self.superclasses, self.formalDefinition, self.syns, self.comment)


def load_classes(ontology, _file):
	log.info("Loading ontology " + ontology + " from file " + _file)
	tree = ET.parse(_file)
	root = tree.getroot()
	
	_header = root.find(OwlOntology)
	if _header is not None:
		address = _header.get(RdfAbout)
	else:
		address = ""

	imports = []
	for _import in _header.findall(OwlImports):
		imports.append(_import.get(RdfResource)) 

	classes = []

	for child in root.findall(OwlClass):
		_namespace = child.find(OboInOwlHasOBONamespace)	
		if _namespace is not None:
			namespace = _namespace.text.encode('utf-8')
		else:
			namespace = ""


		_about = child.get(RdfAbout)
		if _about is not None:
			about = _about.encode('utf-8')
		else:
			about = ""

		_label = child.find(RdfsLabel)
		if _label is not None:
			label = _label.text.encode('utf-8')
		else:
			label = ""

		superclasses = []
		for superclass in child.findall(RdfsSubClass):
			ref = superclass.get(RdfResource)
			if ref is not None:
				superclasses.append(ref.encode('utf-8'))

		_comment = child.find(RdfsComment)
		if _comment is not None and _comment.text is not None:
			comment = _comment.text.encode('utf-8')
		else:
			comment = ""

		_formalDefinition = child.find(OboFormalDefinition)
		if _formalDefinition is not None and _formalDefinition.text is not None:
			formalDefinition = _formalDefinition.text.encode('utf-8')
		else:
			formalDefinition = ""

		syns = []
		for syn in child.findall(OboInOwlHasExactSynonym):
			syns.append(syn.text.encode('utf-8'))

		_class = Class(namespace, ontology, about, label, superclasses, formalDefinition, syns, comment) 
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

	cl_classes = load_classes("CL", "../data/ontologies/cl.owl")
	efo_classes = load_classes("EFO", "../data/ontologies/efo.owl")
	uberon_classes = load_classes("uberon", "../data/ontologies/uberon.owl")

	log.info("Merging ontologies")
	all_classes = {}
	all_ontologies = [i for i in cl_classes.classes if i.label] + [i for i in efo_classes.classes if i.label] + [i for i in uberon_classes.classes if i.label]
	
	for _class in all_ontologies:
		all_classes[_class.about] = _class.label

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


	#count = count + 1
	#sys.stdout.write("\r%d%%" %(count * 100 / total))
	#sys.stdout.flush()
