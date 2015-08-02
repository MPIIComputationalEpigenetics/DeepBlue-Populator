import os
import gzip
import util
import attribute_mapper_factory
import subprocess

from subprocess import call
from formats import format_builder
from settings import DOWNLOAD_PATH, OS
from log import log
from db import mdb
from bedgraphtowig import try_to_convert
from epidb_interaction import PopulatorEpidbClient


"""
MissingFile exception is raised if the file at the given path cannot be found.
"""


class MissingFile(Exception):
    def __init__(self, p, f):
        super(MissingFile, self).__init__()
        self.path = p
        self.file = f

    def __str__(self):
        return "MissingFile: %s" % os.path.join(self.path, self.file)


"""
OrphanedDataset exception is raised if the given dataset cannot be assigned to
a specific repository, which should also be persistent in the database.
"""


class OrphanedDataset(Exception):
    def __init__(self, ds, msg):
        super(OrphanedDataset, self).__init__()
        self.dataset = ds
        self.msg = msg

    def __str__(self):
        return "%s has no parent repository defined: %s" % (self.dataset, self.msg)


"""
Dataset is a logical unit describing a set of data that can be found at
a certain destination. It holds meta data coresponding to the data and is
used to process and insert data into epidb.
"""


class Dataset:
    def __init__(self, file_name, type_, meta={}, file_directory=None, sample_id=None, repo_id=None):

        self.file_name = file_name
        self.type_ = type_
        self.meta = meta
        self.file_directory = file_directory
        self.sample_id = sample_id
        self.repository_id = repo_id
        self.inserted = False
        self._id = None

        # plain map as received from database (not a Repository object)
        self._repository = None

    def __str__(self):
        if self.repository_id:
            return "<Dataset %s at %s>" % (self.file_name, self.download_path)
        else:
            return "<Dataset %s [not in any repository]>" % (self.file_name)

    def __eq__(self, other):
        if not isinstance(other, Dataset):
            return False
        return self.repository_id == other.repository_id and self.file_name == other.file_name and self.meta == other.meta

    def __hash__(self):
        return (hash(self.repository_id) << 16) ^ hash(self.file_name)

    @property
    def id(self):
        if self._id:
            return self._id

        # load id if dataset exists but id is unknown
        if self.exists():
            doc = mdb.datasets.find_one({
                "repository_id": self.repository_id,
                "file_name": self.file_name,
                "meta": self.meta
            })
            if doc and doc["_id"]:
                self._id = doc["_id"]
                return self._id
        return None

    @id.setter
    def id(self, val):
        self._id = val


    @property
    def repository(self):
        if not self.repository_id:
            raise OrphanedDataset(self, "cannot get repository without id")
        # only keep cache as long as it matches the repository_id
        if self._repository and self._repository["_id"] == self.repository_id:
            return self._repository
        self._repository = mdb.repositories.find_one({"_id": self.repository_id})
        return self._repository


    @property
    def type(self):
        return self.type_

    """
    exists checks if the Dataset with its unique attributes `repository_id' and
    'file_name' exists in the database.
    """

    def exists(self):
        return mdb.datasets.find({
            "repository_id": self.repository_id,
            "file_name": self.file_name
        }).count() > 0


    """
    save saves the dataset with its meta information to the database
    Note: this does not have anything to do with the actual genetic data
    that belongs to this dataset.
    """

    def save(self):
        if not self.repository_id:
            raise OrphanedDataset(self, "datasets cannot be saved without a repository id")

        doc = {
            "file_name": self.file_name,
            "repository_id": self.repository_id,
            "type": self.type_,
            "meta": self.meta,
            "file_directory": self.file_directory,
            "sample_id": self.sample_id,
            "inserted": self.inserted,
            "insert_error": ""
        }
        # update existing dataset if id is known/it exists
        if self.id:
            doc["_id"] = self.id

        ds_id = mdb.datasets.save(doc)

    """
    download_path is the path where the datasetes data file is stored
    """

    @property
    def download_path(self):
        if not self.repository_id:
            raise OrphanedDataset(self, "download path cannot be determined without repository.")

        return os.path.join(DOWNLOAD_PATH, str(self.repository_id),
                            # do not remove the "." it is used to transform the absolute paths
                            "./"+self.file_name.replace("ftp://", "").replace("http://", "").replace("https://", "").replace("@", ""))

    """
    load downloads the actual data this dataset refers to if it hasn't
    been loaded already.
    """

    def load(self):
      if os.path.exists(self.download_path):
        log.info("%s already downloaded", self)
        return

      if not self.repository_id:
        raise OrphanedDataset(self, "cannot load dataset for unknown repository.")

      rep = mdb.repositories.find_one({"_id": self.repository_id})
      if not rep:
        raise OrphanedDataset(self, "coresponding repository doesn't exist.")


      if self.file_name.startswith("/TL") or self.file_name.startswith("/DEEP_fhgfs"): # Hardcode fix for DEEP Data
        ssh_server = "139.19.33.32" ## Deep32 machine
        ssh_user = "albrecht"
        print "copying", self.file_name
        print "scp %s@%s:%s %s" % (ssh_user, ssh_server, self.file_name, self.download_path)
        subprocess.Popen(["scp", "%s@%s:%s" % (ssh_user, ssh_server, self.file_name), "%s" % (self.download_path)]).wait()

      else:
        if self.file_name.startswith("http://") or self.file_name.startswith("ftp://") or self.file_name.startswith("https://"):
          url = self.file_name
        else:
          url = "/".join(map(lambda x: str(x).rstrip('/'), [rep["path"], self.file_name]))

        log.info("Downloading %s", url)
        util.download_file(url, self.download_path)
        log.info("Download finished %s", url)

    """
    process inserts the downloaded file and specific meta data into Epidb.
    Note: the file must have been downloaded before (c.f. load) method.
    """
    def process(self):
        log.info("processing dataset %s", self)

        project = self.repository["project"]
        am = attribute_mapper_factory.get(project)(self)

        if not os.path.exists(self.download_path):
            raise MissingFile(self.download_path, self.file_name)

        converted_file_name = ""

        # Handle crazy ENCODE big wigs, that can be bedgraph, bedgraph that can be converted to wig, and... wig!
        if (self.meta.has_key("type") and self.meta["type"].lower() == "bigwig") or self.type.lower() == "bigwig":
            print "../third_party/bigWigToWig." + OS + " " + self.download_path + " " + self.download_path + ".wig"
            call(["../third_party/bigWigToWig." + OS, self.download_path, self.download_path + ".wig"])

            wig_file = self.download_path + ".wig"
            (datatype, tmp_file) = try_to_convert(wig_file)

            if datatype == "wig_converted":
                frmt = "wig"
                converted_file_name = tmp_file
            elif datatype == "wig_input":
                converted_file_name = wig_file
                frmt = "wig"
            else:
                converted_file_name = wig_file
                frmt = "bedgraph"

            am.extra_metadata['__local_file__'] = converted_file_name
            file_content = ""

        elif self.type_ == "wig":
            am.extra_metadata['__local_file__'] = wig_file
            file_content = ""
            frmt = "wig"

        elif self.type_ == "bedgraph":
            f = open(self.download_path)
            lines = f.readlines()
            lines.sort()
            f.close()
            f = open(self.download_path+".out", "w")
            f.writelines(lines)
            f.close()
            am.extra_metadata['__local_file__'] = self.download_path+".out"
            file_content = ""
            frmt = "bedgraph"

        else:
            file_type = self.download_path.split(".")[-1]
            file_content = ""
            if file_type == "gz":
                print "gunzip" + " " + self.download_path
                call(["gunzip", self.download_path])
                am.extra_metadata['__local_file__'] = self.download_path[:-3]
            else:
                f = open(self.download_path, 'r')
                am.extra_metadata['__local_file__'] = self.download_path

            f = open(am.extra_metadata['__local_file__'])
            first_line = f.readline()

            while (first_line[:1] == "#" or first_line[:5] == "track" or first_line[:7] == "browser"):
                first_line = f.readline()
                log.debug(first_line)

            extra_info_size = len(first_line.split())
            frmt = format_builder(am.format, extra_info_size)

        epidb = PopulatorEpidbClient()

        if self.sample_id:
            sample_id = self.sample_id
        else:
            (status, samples_id) = epidb.list_samples(am.biosource, {})
            if status != "okay" or not len(samples_id):
                log.critical("Sample for biosource %s was not found", am.biosource)
                log.critical(samples_id)
                return
            sample_id = samples_id[0][0]

        # Do not include file extension on ENCODE files
        exp_name = am.name
        if am.project != "ENCODE":
            if frmt == "bedgraph" or frmt == "wig":
                exp_name = am.name + "." + frmt
            else:
                exp_name = am.name + ".bed"

        args = (exp_name, am.genome, am.epigenetic_mark, sample_id, am.technique,
                am.project, am.description, file_content, frmt, am.extra_metadata)

        am.extra_metadata["__ignore_unknow_chromosomes__"] = True
        print am.extra_metadata

        res = epidb.add_experiment(*args)
        if res[0] == "okay" or res[1].startswith("102001"):
            self.inserted = True
            self.insert_error = ""
            self.save()
            log.info("dataset %s inserted ", exp_name)
        else:
            msg = "Error while inserting dataset: res: %s\nexperiment_name: %s\nformat:%s\nfile_content: %s\ndownload_path: %s\ntype:%s" % (
            res, am.name, frmt, file_content[0:500], self.download_path, self.type)
            self.insert_error = msg
            self.save()
            log.info(msg)

        if os.path.exists(self.download_path):
            os.remove(self.download_path)

        if os.path.exists(self.download_path[:-3]):
            os.remove(self.download_path[:-3])

        if am.extra_metadata.has_key('__local_file__') and os.path.exists(am.extra_metadata['__local_file__']):
            os.remove(am.extra_metadata['__local_file__'])

        print am.extra_metadata.get('__local_file__', "")

        if frmt == "wig" or frmt == "bedgraph":
            if os.path.exists(converted_file_name):
                os.remove(converted_file_name)

