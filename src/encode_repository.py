import os.path
import re
import urllib

from epidb_interaction import PopulatorEpidbClient
from dataset import Dataset
from log import log
from repository import Repository


"""
A Repository refers to a source of datasets belonging to a certain project.
It detects the available datasets in the repository and can coordinate their
retrival and processing.
"""


class EncodeRepository(Repository):
    def __init__(self, proj, genome, path):
        super(EncodeRepository, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed", "bigWig"], path)

    def __str__(self):
        return "<ENCODE Repository: [%s, %s]>" % (self.path, self.data_types)

    @property
    def index_path(self):
        """
        index_path is the path to the file which contains information of all
        datasets in the repository.
        """
        return os.path.join(self.path, "files.txt")

    def read_datasets(self):
        """
        read_datasets analyses the repositorie's index file and flags
        new datasets.
        """
        epidb = PopulatorEpidbClient()

        epigenetic_mark = None

        new = 0
        f = urllib.urlopen(self.index_path)
        for line in f:
            s = line.strip().split(None, 1)
            file_name, meta_s = s[0], s[1]

            meta = {}
            for kv in meta_s.split("; "):
                fs = kv.split("=")
                meta[fs[0]] = fs[1]

            if "objStatus" in meta:
                # do not include obsolete datasets
                if meta["objStatus"].startswith("renamed") or \
                        meta["objStatus"].startswith("replaced") or \
                        meta["objStatus"].startswith("revoked"):
                    log.info("Not including obsolete dataset %s", line.strip())
                    continue

            if "dataType" not in meta:
                log.info("Line %s from %s does not have datatype" % (line, self.path))
                continue

            r = re.findall('[A-Z][a-z]*', meta["composite"])

            if r[-2] in ["Haib", "Sydh", "Broad", "Uw", "Uchicago", "Psu", "Licr", "Caltech"]:
                # filter out project/instutute names
                em = r[-1]
            else:
                em = r[-2] + r[-1]

            if not epigenetic_mark:
                epigenetic_mark = em
            elif epigenetic_mark and epigenetic_mark != em:
                print "datatype was set %s but new is %s" % (epigenetic_mark, em)

            meta["epigenetic_mark"] = epigenetic_mark

            if epigenetic_mark == "Histone" and meta["antibody"].find("_") != -1:
                meta["antibody"] = meta["antibody"].split("_")[0]

            (status, samples_id) = epidb.list_samples("", {"term": meta["cell"]})
            if status != "okay" or not len(samples_id):
                log.critical("Sample for biosource %s was not found", meta["cell"])
                log.critical(samples_id)

            # First (and only element) and them get its ID
            sample_id = samples_id[0][0]

            size = meta["size"]
            suf = size[-1].lower()
            value = float(size[:-1])

            if suf == 'k':
                s = value * 1024
            elif suf == 'm':
                s = value * 1024 * 1024
            elif suf == 'g':
                s = value * 1024 * 1024 * 1024
            else:
                s = value

            meta["size"] = s

            ds = Dataset(file_name, meta["type"], meta, sample_id=sample_id)
            if self.add_dataset(ds):
                new += 1
                self.has_updates = True

        log.info("found %d new datasets in %s", new, self)
