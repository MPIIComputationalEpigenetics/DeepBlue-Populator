import itertools
import gzip
from multiprocessing import Pool

from epidb_interaction import PopulatorEpidbClient
from downloader import download
from log import log
from settings import max_threads
from sources_annotation import annotations


def insert_annotation(t):
    key = t[0]
    annotation = t[1]
    log.info("Inserting %s" % (annotation.name))
    if annotation.local:
        file_path = annotation.data_location
    else:
        file_path = download(annotation.genome, "annotation", annotation.data_location)

    file_type = file_path.split(".")[-1]
    if file_type == "gz":
        file_data = gzip.open(file_path, 'rb').read()
    else:
        file_data = open(file_path
                         , 'r').read()

    epidb = PopulatorEpidbClient()
    r = epidb.add_annotation(annotation.name, annotation.genome, annotation.description,
                             file_data, annotation.file_format, annotation.extra_metadata)
    if r[0] == "error":
        log.info("Error while inserting annotation %s: %s" % (annotation.name, r[1]))
    else:
        log.info("Annotation %s inserted (%s)" % (annotation.name, r[1]))


def insert_annotations(key):
    total = len(annotations)
    count = 0
    p = Pool(max_threads)
    log.info("Inserting annotation. Total of " + str(total) + " annotations.")

    p.map(insert_annotation, itertools.izip(itertools.repeat(key), annotations))

    p.close()
    p.join()
