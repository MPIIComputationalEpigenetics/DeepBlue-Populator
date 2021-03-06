import os.path
import re
import urllib

from epidb_interaction import PopulatorEpidbClient
from dataset import Dataset
from log import log
from repository import Repository


"""
This repository is used to load the old (a.k.a FTP distributed) ENCODE's data.
Currently, I am rolling it back because I want to import the segmentation data
 that it is not available in the new ENCODE's API.
"""
class EncodeRepositoryFTP(Repository):
    def __init__(self, proj, genome, path):
        super(EncodeRepositoryFTP, self).__init__(proj, genome, ["broadPeak", "narrowPeak", "bed"], path)

    def __str__(self):
        return "<ENCODE FTPs Repository: [%s, %s]>" % (self.path, self.data_types)

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
                log.info("datatype was set %s but new is %s" , epigenetic_mark, em)

            meta["epigenetic_mark"] = epigenetic_mark

            if epigenetic_mark == "Histone" and meta["antibody"].find("_") != -1:
                meta["antibody"] = meta["antibody"].split("_")[0]

            sample_biosource = meta["cell"]

            if sample_biosource == "HSMM":
                sample_biosource = 'skeletal muscle myoblast'
            if sample_biosource == "NHLF":
                sample_biosource = "fibroblast of lung"


            sample_metadata = {"source":"ENCODE FTP"}
            (status, samples_id) = epidb.list_samples(sample_biosource, sample_metadata)

            if status == "okay" and len(samples_id):
                sample_id = samples_id[0][0]
            else:
                log.critical(samples_id)
                log.info("Sample for biosource %s was not found in the old ENCODE FTP data. Dont worry! We are going to create a new sample. ", meta["cell"])
                (status, sample_id) = epidb.add_sample(sample_biosource, sample_metadata)
                if (status != "okay"):
                    log.critical("Not possible to create a new sample for %s - %s", sample_biosource, str(sample_metadata))
                    continue

            # First (and only element) and them get its ID
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