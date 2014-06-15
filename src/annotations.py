import itertools

from multiprocessing import Pool

from client import EpidbClient
from settings import DEEPBLUE_HOST, DEEPBLUE_PORT, log, max_threads
from sources_annotation import annotations


def insert_annotation(t):
  key = t[0]
  annotation = t[1]
  log.info("Inserting %s" %(annotation.name))
  file_data = open(annotation.data_file).read()
  epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)
  r = epidb.add_annotation(annotation.name, annotation.genome, annotation.description,
  file_data, annotation.file_format, annotation.extra_metadata, key)
  if r[0] == "error":
    log.info("Error while inserting annotation %s: %s" %(annotation.name, r[1]))
  else:
    log.info("Annotation %s inserted (%s)" %(annotation.name, r[1]))

def insert_annotations(key):
  total = len(annotations)
  count = 0
  p = Pool(max_threads)
  log.info("Inserting annotation. Total of " + str(total) + " annotations.")    

  p.map(insert_annotation, itertools.izip(itertools.repeat(key), annotations))
  
  p.close()
  p.join()
