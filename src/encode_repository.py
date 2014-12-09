import os.path
import re
import urllib

from client import EpidbClient
from dataset import Dataset
from settings import DEEPBLUE_HOST, DEEPBLUE_PORT
from log import log
from db import mdb
from repository import Repository


"""
A Repository refers to a source of datasets belonging to a certain project.
It detects the available datasets in the repository and can coordinate their
retrival and processing.
"""


class EncodeRepository(Repository):
    def __init__(self, proj, genome, path, user_key):
        # super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed", "bigWig"], path, user_key)
        super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed"], path, user_key)

    def __str__(self):
        return "<ENCODE Repository: [%s, %s]>" % (self.path, self.data_types)

    """
    index_path is the path to the file which contains information of all
    datasets in the repository.
    """

    @property
    def index_path(self):
        return os.path.join(self.path, "files.txt")

    @property
    def id(self):
        idl = mdb.repositories.find_one({
                                            "project": self.project, "path": self.path}, ["_id"])
        if not idl:
            return None
        return idl["_id"]

    """
    read_datasets analyses the repositorie's index file and flags
    new datasets.
    """

    def read_datasets(self):
        epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

        epigeneticMark = None

        new = 0
        f = urllib.urlopen(self.index_path)
        for line in f:
            s = line.strip().split(None, 1)
            file_name, meta_s = s[0], s[1]

            meta = {}
            for kv in meta_s.split("; "):
                fs = kv.split("=")
                meta[fs[0]] = fs[1]

            if not meta.has_key("dataType"):
                log.info("Line %s from %s does not have datatype" % (line, self.path))
                continue

            r = re.findall('[A-Z][a-z]*', meta["composite"])

            if r[-2] in ["Haib", "Sydh", "Broad", "Uw", "Uchicago", "Psu", "Licr", "Caltech"]:
                #filter out project/instutute names
                em = r[-1]
                print em
            else:
                em = r[-2] + r[-1]
                print em

            if epigeneticMark == None:
                epigeneticMark = em
            elif epigeneticMark != None and epigeneticMark != em:
                print "datatype was set %s but new is %s" % (epigeneticMark, em)

            meta["epigenetic_mark"] = epigeneticMark

            if epigeneticMark == "Histone" and meta["antibody"].find("_") != -1:
                meta["antibody"] = meta["antibody"].split("_")[0]

            (status, samples_id) = epidb.list_samples("", {"term": meta["cell"]}, self.user_key)
            if status != "okay" or not len(samples_id):
                log.critical("Sample for biosource %s was not found", am.biosource)
                log.critical(samples_id)

            # First (and only element) and them get its ID
            sample_id = samples_id[0][0]

            size = meta["size"]
            suf = size[-1].lower()
            value = float(size[:-1])

            if (suf == 'k'):
                s = value * 1024
            elif (suf == 'm'):
                s = value * 1024 * 1024
            elif (suf == 'g'):
                s = value * 1024 * 1024 * 1024
            else:
                s = value

            meta["size"] = s

            ds = Dataset(file_name, meta["type"], meta, sample_id=sample_id)
            if self.add_dataset(ds):
                new += 1
                self.has_updates = True

        log.info("found %d new datasets in %s", new, self)
