from optparse import OptionParser

from populator import Populator
from settings import log

def main(init=False, insert_annotations=False, insert_datasets=False, insert_cv= False, insert_ontology=False):
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

  if insert_cv:
    pop.process_vocabulary()

  if insert_ontology:
    pop.process_ontology()

  # insert all annotation to epidb
  if insert_annotations:
    pop.process_annotations()

  # insert all new found data to epidb
  if insert_datasets:
    pop.load_repositories()
    pop.check_repositories()
    pop.save_repositories()
    pop.process_repositories()


  log.info("DeepBlue Populator finished successfully")

if __name__ == '__main__':
  parser = OptionParser()

  parser.add_option("--init", action="store_true", dest="init", default=False,
      help="Init EpiDB, creating default users")
  parser.add_option("--cv", action="store_true", dest="cv", default=False,
      help="Insert ENCODE controlled vocabulary")
  parser.add_option("--ontology", action="store_true", dest="ontology", default=False,
      help="Insert Ontologies inside the controlled vocabulary")
  parser.add_option("--populate", action="store_true", dest="populate", default=False,
      help="Insert annotations and datasets")
  parser.add_option("--annotations", action="store_true", dest="insert_annotations", default=False,
      help="Insert annotations")
  parser.add_option("--datasets", action="store_true", dest="insert_datasets", default=False,
      help="Insert datasets")
  parser.add_option("--full", action="store_true", dest="full", default=False,
      help="Init EpiDB, creating default users and vocabulary, insert annotations and datasets.")

  args = parser.parse_args()

  init = args[0].init
  insert_annotations = args[0].insert_annotations
  insert_datasets = args[0].insert_datasets
  insert_cv = args[0].cv
  insert_ontology = args[0].ontology


  if args[0].populate:
    insert_cv = True
    insert_annotations = True
    insert_datasets = True

  if args[0].full:
    init = True
    insert_annotations = True
    insert_cv = True
    insert_ontology = True        
    insert_datasets = True

  main(init, insert_annotations, insert_datasets, insert_cv, insert_ontology)
