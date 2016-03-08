from optparse import OptionParser

from populator import Populator
from log import log


def main(init=False, insert_annotations=False, insert_datasets=False,
         insert_ontology=False, insert_basic_data=False):
    # initialize populator and update populators local database
    pop = Populator()

    # setup user accounts and add vocabulary
    if init:
        s = pop.setup_epidb()
        if not s:
            log.info("Aborting populator.")
            return
        pop.insert_basic_data()
        pop.create_columns()

    if insert_basic_data:
        pop.insert_basic_data()
        pop.create_columns()

    if insert_ontology:
        pop.process_ontology()

    # insert all annotation to epidb
    if insert_annotations:
        pop.process_annotations()

    # insert all new found data to epidb
    if insert_datasets:
        pop.load_repositories()
        pop.check_repositories()
        pop.process_repositories()

    log.info("DeepBlue Populator finished successfully")


if __name__ == '__main__':
    parser = OptionParser(version="DeepBlue-Populator 0.9")

    parser.add_option("--init", action="store_true", dest="init",
                      default=False,
                      help="Initialize DeepBlue, creating default users")
    parser.add_option("--basic_data", action="store_true", dest="insert_basic_data",
                      default=False,
                      help="Insert DeepBlue Basic Data. Usefull when new genomes, columns, epigenetic marks, projects or samples were included into populator")
    parser.add_option("--ontology", action="store_true", dest="ontology",
                      default=False,
                      help="Insert Ontologies terms into the controlled vocabulary")
    parser.add_option("--annotations", action="store_true",
                      dest="insert_annotations", default=False,
                      help="Insert annotations")
    parser.add_option("--datasets", action="store_true",
                      dest="insert_datasets", default=False,
                      help="Insert datasets")
    parser.add_option("--full", action="store_true", dest="full",
                      default=False,
                      help="Init EpiDB, creating default users and vocabulary, insert annotations and datasets.")

    args = parser.parse_args()

    init = args[0].init
    insert_annotations = args[0].insert_annotations
    insert_datasets = args[0].insert_datasets
    insert_ontology = args[0].ontology
    insert_basic_data = args[0].insert_basic_data

    if args[0].insert_basic_data:
        insert_basic_data = True

    if args[0].full:
        init = True
        insert_annotations = True
        insert_ontology = True
        insert_datasets = True

    if init or insert_annotations or insert_datasets or insert_ontology or insert_basic_data:
      main(init, insert_annotations, insert_datasets, insert_ontology, insert_basic_data)
    else:
      parser.print_version()
      parser.print_help()

