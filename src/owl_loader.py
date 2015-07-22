import gzip
import threading
import xml.etree.ElementTree as ET

from epidb_interaction import PopulatorEpidbClient

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

#OboInOwlHasExactSynonym = "{%s}hasExactSynonym" % OboInOwl
OboInOwlHasOBONamespace = "{%s}hasOBONamespace" % OboInOwl
## OboInOwlHasRelatedSynonym = "{%s}hasRelatedSynonym" % OboInOwl

# Specific Ontologies Attributes
EfoAlternativeTerm = "{%s}alternative_term" % Efo
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
    def __init__(self, namespace, ontology, about, ontology_id, term_id, label, superclasses, formalDefinition,
                 syns, comment, deprecated):
        self.namespace = namespace
        self.ontology_merges = []
        self.ontology = ontology
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
        self.ontology_id = ontology_id
        self.term_id = term_id

    def __str__(self):
        subs_label = ",".join([s.label for s in self.sub])
        return "namespace %s\tontology %s\tabout %s\tlabel %s\tsuperclasses %s\tformaldefinition %s\tsysns %s\tcomment %s\tsubs %s" % (
        self.namespace, self.ontology, self.about, self.label, self.superclasses,
        self.formalDefinition, self.syns, self.comment, subs_label)

    def __repr__(self):
        subs_label = ",".join([s.label for s in self.sub])
        return "namespace %s\tontology %s\tabout %s\tlabel %s\tsuperclasses %s\tformaldefinition %s\tsysns %s\tcomment %s\tsubs %s" % (
        self.namespace, self.ontology, self.about, self.label, self.superclasses,
        self.formalDefinition, self.syns, self.comment, subs_label)


def process_owl_class(_owl_class, label, about, superclasses):
    found = False
    for _class_intersection_of in _owl_class.findall(OwlIntersectionOf):
        process_intersection_or_union_of(_class_intersection_of, label, about,
                                         superclasses)
        found = True

    for _class_union_of in _owl_class.findall(OwlUnionOf):
        # The Union informs sub classes. We are looking for super classes here.
        # process_intersection_or_union_of(_class_union_of, label, about, superclasses)
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
            superclasses.append(
                _class_equivalent_description_about.encode('utf-8').strip())
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
    # log.info("Loading ontology " + ontology + " from file " + _file)

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
        _label = child.find(RdfsLabel)
        if _label is not None:
            label = _label.text.encode('utf-8').strip()
        else:
            label = ""

        if not label:
            continue

        _about = child.get(RdfAbout)
        if _about is not None:
            about = _about.encode('utf-8').strip()
        else:
            about = ""

        term_id = about.split("/")[-1].replace("_",":")
        ontology_id = term_id.split(":")[0]

        if ontology_id != ontology:
            print "Term " + term_id + " (" + label + ") ignored because it is not part of the " + ontology
            continue

        _namespace = child.find(OboInOwlHasOBONamespace)
        if _namespace is not None and _namespace.text:
            namespace = _namespace.text.encode('utf-8').strip()
        else:
            namespace = ""

        superclasses = []

        for _subclass in child.findall(RdfsSubClass):
            ref = _subclass.get(RdfResource)
            if ref is not None:
                sub_ref = ref.encode('utf-8').strip()
                if sub_ref == _about:
                    print 'This class (', label, ontology, ') is a sub class of... itself!'
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
                for _class_intersection_of in _class_equivalent_class.findall(
                        OwlIntersectionOf):
                    process_intersection_or_union_of(_class_intersection_of, label, about,
                                                     superclasses)
                    found = True

                for _class_union_of in _class_equivalent_class.findall(OwlUnionOf):
                    # The Union informs sub classes. We are looking for super classes here.
                    found = True

                if not found:
                    print 'Not found: _class_intersection_of or _class_union_of', label, about

            if not found:
                _resource = _equivalentClass.get(RdfResource)
                if _resource is not None:
                    pass
                    print 'equivalent to ', _resource.encode(
                        'utf-8').strip(), label, about
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
            _formalDefinition = child.find(EfoDefinition)
            if _formalDefinition is not None and _formalDefinition.text is not None:
                formalDefinition = _formalDefinition.text.encode('utf-8').strip()
            else:
                formalDefinition = ""

        syns = []

        # Removed because: anatomical cluster is a entity and was being syn of multi organ part structure
        # I believe tat this property is used for **cross** ontology link and not for internal names
        # for syn in child.findall(OboInOwlHasRelatedSynonym):
        #    if syn.text:
        #        syns.append(syn.text.encode('utf-8').strip())
        #
        # for syn in child.findall(OboInOwlHasExactSynonym):
        #    if syn.text:
        #        syns.append(syn.text.encode('utf-8').strip())

        for syn in child.findall(EfoAlternativeTerm):
            if syn.text:
                syns.append(syn.text.encode('utf-8').strip())

        for syn in child.findall(HasRelationalAdjective):
            if syn.text:
                syns.append(syn.text.encode('utf-8').strip())

        # Remove duplicates
        syns = list(set(syns))
        superclasses = list(set(superclasses))

        _class = Class(namespace, ontology,  about, ontology_id, term_id, label, superclasses, formalDefinition,
                       syns, comment, deprecated)
        if not _class.label.startswith('obsolete') and not _class.deprecated:
            classes.append(_class)

    return Ontology(ontology, address, imports, classes)


def load_blacklist():
    # print 'loading blacklist terms (terms that arent biosources) from ontologies_blacklist.txt'
    f = open("ontologies_blacklist.txt")
    blacklist = []

    for term in f.readlines():
        blacklist.append(term.strip())

    return blacklist


def load_on_propery_lists():
    f = open("on_property_black_list.txt")
    blacklist = []

    for term in f.readlines():
        blacklist.append(term.strip())

    f = open("on_property_white_list.txt")
    whitelist = []

    for term in f.readlines():
        whitelist.append(term.strip())

    return blacklist, whitelist


already_filtered = {}


def filter_classes(classes, blacklist, count=0):
    result = []
    for _class in classes:
        print _class.label, _class.term_id,
        if _class.label in blacklist:
            print "blacklist"
            continue

        if already_filtered.has_key(_class.label):
            print "already_filtered"
            continue

        ignore = False
        for ignore_super in ["http://purl.obolibrary.org/obo/OBI_0000070", "http://purl.obolibrary.org/obo/UO_0000186", "http://www.ifomis.org/bfo/1.1/snap#Site", "http://purl.obolibrary.org/obo/UO_0000109", "http://purl.obolibrary.org/obo/GO_0007610", "http://purl.obolibrary.org/obo/PATO_0000051", "http://purl.obolibrary.org/obo/CHEBI_37577", "http://purl.obolibrary.org/obo/UO_0000051", "http://purl.obolibrary.org/obo/CHEBI_16113", "http://purl.obolibrary.org/obo/GO_0097327", "http://purl.obolibrary.org/obo/GO_0061476","http://purl.obolibrary.org/obo/CHEBI_36080", "http://purl.obolibrary.org/obo/UO_0000001", "http://purl.obolibrary.org/obo/GO_0036276",  "http://purl.obolibrary.org/obo/UO_0000055", "http://purl.obolibrary.org/obo/HP_0001871", "http://purl.obolibrary.org/obo/IAO_0000098", "http://purl.obolibrary.org/obo/CHEBI_36080", "http://purl.obolibrary.org/obo/CHEBI_24432", "http://purl.obolibrary.org/obo/OBI_0000272", "http://purl.obolibrary.org/obo/OBI_0200000", "http://purl.obolibrary.org/obo/UO_0000055", "http://www.ifomis.org/bfo/1.1/span#ProcessualEntity", "http://purl.obolibrary.org/obo/IAO_0000030", "http://mged.sourceforge.net/ontologies/MGEDOntology.owl#developmental_stage", "http://purl.obolibrary.org/obo/IAO_0000030", "http://purl.obolibrary.org/obo/OBI_0001620", "http://purl.obolibrary.org/obo/HP_0000153", "http://purl.obolibrary.org/obo/UO_0000187", "http://purl.obolibrary.org/obo/GO_0050896", "http://purl.obolibrary.org/obo/OBI_0000245", "http://purl.obolibrary.org/obo/UO_0000187", "http://purl.obolibrary.org/obo/UO_0000046", "http://purl.obolibrary.org/obo/IAO_0000030", "http://purl.obolibrary.org/obo/OBI_0100051", "http://www.ifomis.org/bfo/1.1/span#ProcessualEntity", "http://purl.obolibrary.org/obo/UO_0000007", "http://purl.obolibrary.org/obo/IAO_0000030", "http://www.ifomis.org/bfo/1.1/snap#Quality", "http://purl.obolibrary.org/obo/GO_0042592", "http://purl.obolibrary.org/obo/GO_0042493", "http://purl.obolibrary.org/obo/GO_0036277", "http://purl.obolibrary.org/obo/HP_0002715", "http://purl.obolibrary.org/obo/OBI_0000869", 'http://purl.obolibrary.org/obo/OBI_0001621', "http://purl.obolibrary.org/obo/GO_0000003", "http://purl.obolibrary.org/obo/HP_0001626", "http://purl.obolibrary.org/obo/OBI_1110122", "http://purl.obolibrary.org/obo/PO_0000025", 'http://purl.obolibrary.org/obo/HP_0004936', "http://purl.obolibrary.org/obo/CHEBI_17089", "http://purl.obolibrary.org/obo/CHEBI_17089", "http://purl.obolibrary.org/obo/HP_0011024", "http://purl.obolibrary.org/obo/DOID_10113", "http://purl.obolibrary.org/obo/CHEBI_33697", "http://purl.obolibrary.org/obo/GO_0007568", "http://purl.obolibrary.org/obo/HP_0002373", "http://purl.obolibrary.org/obo/GO_0097332", "http://purl.obolibrary.org/obo/HP_0001657", "http://purl.obolibrary.org/obo/OBI_0600002", "http://purl.obolibrary.org/obo/HP_0001679"]:
            if ignore_super in _class.superclasses:
                print "ignore " , _class.label, _class.superclasses
                ignore = True
                break

        if ignore:
            print "ignore_super"
            continue

        print "ok"
        result.append(_class)
        already_filtered[_class.label] = True
        sub_result = filter_classes(_class.sub, blacklist, count + 1)
        result += sub_result
        result = list(set(result))
    return result


def load_owl(user_key):
    log.info("Loading ontologies")

    cl_classes = load_classes("CL", "../data/ontologies/cl.owl.gz")
    efo_classes = load_classes("EFO", "../data/ontologies/efo.owl.gz")
    uberon_classes = load_classes("UBERON", "../data/ontologies/uberon.owl.gz")
    ncbitaxon = load_classes("NCBITaxon", "../data/ontologies/ncbi_taxon_selection2.owl.gz")

    all_classes = {}
    all_classes_names = {}
    all_ontologies = [i for i in cl_classes.classes if i.label] + \
                     [i for i in efo_classes.classes if i.label] + \
                     [i for i in uberon_classes.classes if i.label] + \
                     [i for i in ncbitaxon.classes if i.label]

    print "Before merge", len(all_ontologies)

    for _class in all_ontologies:
        if all_classes_names.has_key(_class.label):
            duplicated_class = all_classes_names[_class.label]
            duplicated_class.superclasses = list(
                set(duplicated_class.superclasses + _class.superclasses))
            duplicated_class.superclasses_names = list(
                set(duplicated_class.superclasses_names + _class.superclasses_names))
            duplicated_class.syns = list(set(duplicated_class.syns + _class.syns))
            duplicated_class.sub = list(set(duplicated_class.sub + _class.sub))
            all_classes_names[_class.label] = duplicated_class
            all_classes[_class.term_id] = _class.label
        else:
            all_classes[_class.term_id] = _class.label
            all_classes_names[_class.label] = _class

    all_ontologies = []
    for v in all_classes_names.itervalues():
        all_ontologies.append(v)
    print "After merge", len(all_ontologies)

    # Linking references
    print 'Linking'
    for _class in all_ontologies:
        _class.user_key = user_key
        for superclass in _class.superclasses:
            ref = superclass.split("/")[-1].replace("_",":")
            if all_classes.has_key(ref):
                _class.superclasses_names.append(all_classes[ref])
            else:
                print "refence %s for the class '%s' not found" % (ref, _class.label)

    no_parents = []

    # Build the relationship
    for _class in all_ontologies:
        if not _class.label:
            continue
        if not _class.superclasses_names:
            no_parents.append(_class)
        else:
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
    print 'searching  for synonyms that are also defined as classes'
    # All ontologies
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
                    if found not in _class.syns:
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

    print 'total: ', len(all_classes)
    print 'no_parent: ', len(no_parents)
    print 'duplicated (synonym and class): ', len(_synonymn_classes)

    blacklist_terms = load_blacklist()
    full_blacklist_terms = blacklist_terms + _synonymn_classes
    print 'filtering.. '
    biosources = filter_classes(no_parents, full_blacklist_terms)
    for bs in biosources:
        if bs.term_id == "UBERON:0000477":
            print "aaaaaaaaa"
            print bs
    print 'total biosources:', len(biosources)

    print "Roots:"
    r = 0
    for biosource in biosources:
        if not biosource.superclasses_names:
            r += 1
            print biosource.superclasses

    print "Total roots: " + str(r)

    alread_in = {}

    def print_biosources(no_parents, biosources, f, parent=None, deep=0):
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
            f.write('\n')
            f.write(' ' * (deep + 1))
            f.write('"label": "%s",' % (_class.label))
            f.write('\n')
            f.write(' ' * (deep + 1))
            f.write('"about": "%s",' % (_class.about))
            f.write('\n')
            f.write(' ' * (deep + 1))
            f.write('"synonyms": [')
            first_2 = True
            for syn in _class.syns:
                if not alread_in.has_key(syn):
                    if not first_2:
                        f.write(',')
                    f.write('"%s"' % syn)
                    first_2 = False

            f.write('],')
            f.write('\n')

            f.write(' ' * (deep + 1))
            f.write('"subs":')
            print_biosources(_class.sub, biosources, f, _class, deep + 1)
            f.write('\n')
            f.write(' ' * (deep))
            f.write('}')
        f.write(']\n')


    more_embrancing_cache = {}

    """ Laziness to write a better synchronizer """
    set_alread_in_semaphore = threading.BoundedSemaphore()

    def set_alread_in(label):
        set_alread_in_semaphore.acquire()
        alread_in[label] = True
        set_alread_in_semaphore.release()

    def insert_syns(_class):
        syns_epidb = PopulatorEpidbClient()
        for syn in _class.syns:
            if not alread_in.has_key(syn):
                log.info("setting syn " + syn + " to " + _class.label)
                status, _id = syns_epidb.set_biosource_synonym(_class.label, syn)
                if status == 'error' and not _id.startswith('104400'):
                    print _class, syn, _id
                    log.info(
                        "error on setting syn" + _class.label + " syn " + syn + " msg: " + _id)
                set_alread_in(syn)

    def set_parent(_class, sub):
        scope_epidb = PopulatorEpidbClient()
        log.info("setting parent " + _class.label + " sub " + sub.label)
        status, _id = scope_epidb.set_biosource_parent(_class.label, sub.label)
        cache_key = _class.label + " " + sub.label
        if status == 'okay':
            more_embrancing_cache[cache_key] = True
            log.info(
                "OKAY on setting parent " + _class.label + " sub " + sub.label + " msg: " + str(
                    _id))
        elif status == 'error' and _id.startswith('104901'):
            log.info(
                "error expected on setting parent " + _class.label + " sub " + sub.label + " msg: " + _id)
        else:
            log.info(
                "error on setting parent " + _class.label + " sub " + sub.label + " msg: " + str(
                    _id))

    def set_scope(_class):
        for sub in _class.sub:
            cache_key = _class.label + " " + sub.label
            if not more_embrancing_cache.has_key(cache_key):
                set_parent(_class, sub)

    threads = []

    def insert_biosources(no_parents, biosources, epidb):
        for _class in no_parents:
            if alread_in.has_key(_class.label):
                continue

            if _class not in biosources:
                continue


            extra_metadata = { "url": _class.about,
                               "ontology_id" : _class.term_id,
                               "comment": _class.comment
                             }

            if _class.namespace:
                extra_metadata["namespace"] = _class.namespace
            if _class.comment:
                extra_metadata["comment"] = _class.comment

            log.info(
                "add biosource " + _class.label + " - " + _class.formalDefinition + " - " + str(
                    extra_metadata))
            status, _id = epidb.add_biosource(_class.label, _class.formalDefinition,
                                              extra_metadata)
            if status == 'error':
                log.info("error on inserting biosource " + _class.label + " msg: " + _id)

            insert_syns(_class)

            set_alread_in(_class.label)
            insert_biosources(_class.sub, biosources, epidb)

            t = threading.Thread(target=set_scope, args=(_class,))
            t.start()
            threads.append(t)

    print 'Waiting for threads..',
    for t in threads:
        print '.',
        t.join()


    #print "Output json"
    #f = open("imported_biosources.json", "w+")
    #print f.write('{ "data":\n')
    #print_biosources(no_parents, biosources, f)
    #print f.write('}')

    epidb = PopulatorEpidbClient()
    insert_biosources(no_parents, biosources, epidb)


on_propery_blacklist, on_propery_whitelist = load_on_propery_lists()

#load_owl("")
