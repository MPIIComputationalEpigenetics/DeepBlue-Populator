from collections import defaultdict

import itertools
import gzip
import threading

from settings import max_threads
from log import log
from multiprocessing import Pool

import xml.etree.ElementTree as ET

from epidb_interaction import PopulatorEpidbClient

from log import log

Owl = "http://www.w3.org/2002/07/owl#"
Rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
Rdfs = "http://www.w3.org/2000/01/rdf-schema#"
Obo = "http://purl.obolibrary.org/obo/"
OboInOwl = "http://www.geneontology.org/formats/oboInOwl#"

OboFormalDefinition = "{%s}IAO_0000115" % Obo

OwlClass = "{%s}Class" % Owl
OwlOntology = "{%s}Ontology" % Owl
OwlObjectProperty = "{%s}ObjectProperty" % Owl

RdfAbout = "{%s}about" % Rdf
RdfResource = "{%s}resource" % Rdf

RdfsSubClass = "{%s}subClassOf" % Rdfs
RdfsLabel = "{%s}label" % Rdfs

OboInOwlID = "{%s}id" % OboInOwl
OboInOwlHasOBONamespace = "{%s}hasOBONamespace" % OboInOwl


class GO_Term:

    def __init__(self, _label, _id, _description, _namespace, _superclass):
        self._label = _label
        self._id = _id
        self._description = _description
        self._namespace = _namespace
        self._superclass = _superclass

    def __str__(self):
        return self._label + " " + self._id + " " + self._namespace + " " + self.super_id()

    def super_id(self):
        if self._superclass is not None:
            _up = ":".join(self._superclass.split("/")[-1].split("_"))
            return _up
        return ""


def _load_go_owl(_file):
    terms = {}
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

     # Load the class and the RdfDescription, because the UBERON defines somes
     # classes inside RdfDescription
    for child in root.findall(OwlClass):
        _id = child.find(OboInOwlID)
        if _id is None:
            continue
        _id = _id.text.encode('utf-8').strip()

        _label = child.find(RdfsLabel)
        if _label is None:
            print 'label not found', _id
            return
        _label = _label.text.encode('utf-8').strip()

        _description = child.find(OboFormalDefinition)
        if _description is not None and _description.text is not None:
            _description = _description.text.encode('utf-8').strip()
        else:
            _description = ""

        _namespace = child.find(OboInOwlHasOBONamespace)
        if _namespace is None:
            print 'Namespace not found', _label
        _namespace = _namespace.text.encode('utf-8').strip()

        _superclass = child.find(RdfsSubClass)
        if _superclass is not None:
            _superclass = _superclass.get(RdfResource).encode('utf-8').strip()

        terms[_id] = GO_Term(_label, _id, _description,
                             _namespace, _superclass)

    return terms


def _load_id_mapping(_file):
    if _file.endswith("gz"):
        data = gzip.open(_file).read()
    else:
        data = open(_file).read()

    _map_kprto_ensb = defaultdict(list)
    _map_ensb_kprto = defaultdict(list)

    for line in data.split("\n"):
        ss = line.split("\t")
        if len(ss) == 3:
            (kprot_id, _type, _type_id) = ss
            if _type == "Ensembl":
                _map_kprto_ensb[kprot_id].append(_type_id)
                _map_ensb_kprto[_type_id].append(kprot_id)

    return _map_kprto_ensb, _map_ensb_kprto


# Protein (UniProtKB) to GO term
def _load_gaf(_file):
    if _file.endswith("gz"):
        data = gzip.open(_file).read()
    else:
        data = open(_file).read()

    _map = defaultdict(set)
    for line in data.split("\n"):
        columns = line.split("\t")
        if len(columns) == 15 or len(columns) == 16:
            _map[columns[1]].add(columns[4])

    return _map

def _load_gene_association(_file):
    if _file.endswith("gz"):
        data = gzip.open(_file).read()
    else:
        data = open(_file).read()

    _map = defaultdict(set)
    for line in data.split("\n"):
        columns = line.split("\t")
        if len(columns) == 17:
            _map[columns[4]].add(columns[1])

    return _map

def _load_gp2protein(_file):
    if _file.endswith("gz"):
        data = gzip.open(_file).read()
    else:
        data = open(_file).read()

    _map = defaultdict(set)
    for line in data.split("\n"):
        columns = line.split()
        if len(columns) != 2:
            continue
        mgi = ":".join(columns[0].split(":")[1:])
        other = columns[1]
        if other.startswith("UniProtKB:"):
            uniprot = other.split(":")[1]
            _map[mgi].add(uniprot)

    return _map

def _annotate_genes(uniprotkb_to_go, _map_kprto_ensb):
    gene_go = []
    for (uniprotkb, gos) in uniprotkb_to_go.iteritems():
        ensb = _map_kprto_ensb.get(uniprotkb)
        if ensb:
            gene_go.extend(list(itertools.product(ensb, gos)))
    return gene_go


def _insert_go_term(go_term):
    epidb = PopulatorEpidbClient()
    s, m = epidb.add_gene_ontology_term(
        go_term._id, go_term._label, go_term._description, go_term._namespace)
    if s == "error":
        log.error(str(m) + " : " + str(go_term))


def _set_parent_go_term(go_term):
    if not go_term.super_id():
        return

    epidb = PopulatorEpidbClient()
    s, m = epidb.set_gene_ontology_term_parent(go_term.super_id(), go_term._id)
    if s == "error":
        log.error(str(m) + " : " + str(go_term))


def _anotate_gene(v):
    epidb = PopulatorEpidbClient()
    s, m = epidb.annotate_gene(v[0], v[1])
    if s == "error":
        log.error(m + " : " + v[0] + " - " + v[1])


def add_gene_ontology_terms_and_annotate_genes():
    log.info("Loading go.owl")

    go_terms = _load_go_owl('../data/gene_ontology/go.owl.gz')
    p = Pool(16)
    p.map(_insert_go_term, go_terms.values())
    p.close()
    p.join()

    p = Pool(16)
    p.map(_set_parent_go_term, go_terms.values())
    p.close()
    p.join()

    log.info("Loading goa_human.gaf.gz")
    uniprotkb_to_go = _load_gaf("../data/gene_ontology/goa_human.gaf.gz")
    log.info("Loading HUMAN_9606_idmapping.dat.gz")
    _map_kprto_ensb, _map_ensb_kprto = _load_id_mapping(
        "../data/gene_ontology/HUMAN_9606_idmapping.dat.gz")

    log.info("Processing genes annotations")
    ann_gs = _annotate_genes(uniprotkb_to_go, _map_kprto_ensb)

    p = Pool(16)
    p.map(_anotate_gene, ann_gs)
    p.close()
    p.join()


def MOUSE_add_gene_ontology_terms_and_annotate_genes(has_go = True):
    log.info("Loading go.owl")

    if not has_go:
        go_terms = _load_go_owl('../data/gene_ontology/go.owl.gz')

        p = Pool(16)
        p.map(_insert_go_term, go_terms.values())
        p.close()
        p.join()

        p = Pool(16)
        p.map(_set_parent_go_term, go_terms.values())
        p.close()
        p.join()

    log.info("Loading gene_association.mgi.gz")
    go_to_mgi = _load_gene_association("../data/gene_ontology/gene_association.mgi.gz")

    gp2protein = _load_gp2protein("../data/gene_ontology/gp2protein.mgi.txt.gz")

    _map_kprto_ensb, _map_ensb_kprto = _load_id_mapping("../data/gene_ontology/MOUSE_10090_idmapping.dat.gz")

    kv = {}
    for gm in go_to_mgi:
        for gmi in go_to_mgi[gm]:
            for uniprotkb in gp2protein[gmi]:
                kv[gm] = _map_kprto_ensb[uniprotkb]

    gene_gos = []
    for k in kv:
        genes = kv[k]
        for gene in genes:
            gene_gos.append((gene, k))

    p = Pool(16)
    p.map(_anotate_gene, gene_gos)
    p.close()
    p.join()

#    log.info("Loading HUMAN_9606_idmapping.dat.gz")
#    _map_kprto_ensb, _map_ensb_kprto = _load_id_mapping(
#        "../data/gene_ontology/HUMAN_9606_idmapping.dat.gz")

#    log.info("Processing genes annotations")
#    ann_gs = _annotate_genes(uniprotkb_to_go, _map_kprto_ensb)

#    p = Pool(16)
#    p.map(_anotate_gene, ann_gs)
#    p.close()
#    p.join()

# 440000
#found = list(set(sum([_map_kprto_ensb.get(key) for key in uniprotkb_to_go.keys() if _map_kprto_ensb.has_key(key)], [])))
# print found
# print len(found)
# print len(_map_ensb_kprto.keys())
# print len(_map_kprto_ensb.keys())


#missing = {key: value for (key, value) in _map_kprto_ensb.iteritems() if not uniprotkb_to_go.has_key(key)}
# print len(missing)
# print len(_map_kprto_ensb.keys())

# print _map_ensb_kprto.keys()

# for uniprotk in uniprotkb_to_go.keys():
    # if not _map_kprto_ensb[uniprotk]


# for term in go_terms:
#    print term


"""
f = open("HUMAN_9606_idmapping.dat")

UniProtKB_to_Ensembl_ens = defaultdict(list)
Ensembl_to_UniProtKB_ens = defaultdict(list)

UniProtKB_to_Ensembl_nam = defaultdict(list)
Ensembl_to_UniProtKB_nam = defaultdict(list)


for l in f.readlines():
    columns = l.split("\t")
    if columns[1] == "Ensembl":
        UniProtKB_to_Ensembl_ens[columns[0]].append(columns[2].strip())
        Ensembl_to_UniProtKB_ens[columns[2]].append(columns[0].strip())

    if columns[1] == "Gene_Name":
        UniProtKB_to_Ensembl_nam[columns[0]].append(columns[2].strip())
        Ensembl_to_UniProtKB_nam[columns[2]].append(columns[0].strip())


##print(len(UniProtKB_to_Ensembl_ens))

#print UniProtKB_to_Ensembl_ens

#print len([(k,v) for (k,v) in UniProtKB_to_Ensembl_ens if len(v) > 1])

## print len({key: value for (key, value) in Ensembl_to_UniProtKB_ens.iteritems() if len(value) > 1})

## print(len(Ensembl_to_UniProtKB_ens))

print(len(UniProtKB_to_Ensembl_nam))
print(len(Ensembl_to_UniProtKB_nam))

"""
