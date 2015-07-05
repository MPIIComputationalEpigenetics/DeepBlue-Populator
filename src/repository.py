import threading
import os.path
import abc

import db
from dataset import Dataset
from settings import max_threads
from log import log

from multiprocessing import Pool

class NonpersistantRepository(Exception):
    """
    NonpersistantRepository exception is raised if certain operations on a
    repository are attempted before it has been saved to the database.
    """
    def __init__(self, repo, msg):
        super(NonpersistantRepository, self).__init__()
        self.repository = repo
        self.msg = msg

    def __str__(self):
        return "%s has not been stored: %s" % os.path.join(self.repository, self.msg)

def process(dataset):
    try:
        dataset.load()
        dataset.process()
        dataset.save()
    except IOError as ex:
        log.exception("error on downloading or reading dataset of %s failed: %s", dataset, ex)
    except Exception as ex:
        log.exception("processing of %s failed %s", dataset, repr(ex))


class Repository(object):
    """
    A Repository refers to a source of datasets belonging to a certain project.
    It detects the available datasets in the repository and can coordinate their
    retrieval and processing.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, proj, genome, data_types, path):
        self.project = proj
        self.genome = genome
        self.data_types = data_types
        self.path = path

    def __str__(self):
        return "<Repository: [%s, %s, %s]>" % (self.genome, self.project, self.path)

    def __eq__(self, other):
        if not isinstance(other, Repository):
            return False
        return self.path == other.path and self.genome == other.genome

    def __hash__(self):
        return hash(self.path)


    @property
    def index_path(self):
        """
        index_path is the path to the file which contains information of all
        datasets in the repository.
        """
        raise NotImplementedError("")

    @property
    def id(self):
        idl = db.repo_id(self.project, self.path, self.genome)
        if not idl:
            return None
        return idl["_id"]


    @abc.abstractmethod
    def read_datasets(self):
        """
        read_datasets analyses the repository's index file and flags
        new datasets.
        """
        pass


    def exists(self):
        """
        exists checks if the repository has already been added to the database.
        """
        return db.repo_exists(self.project, self.path, self.genome, self.data_types)


    def has_unimported(self):
        """
        has_unimported checks if the repository
        """
        return db.count_unimported(self.project, self.path)


    def save(self):
        """
        Saves the repository to the database if it doesn't exist already. Updates it if
        project attributes changed slightly.
        """
        if self.exists():
            return

        if db.repo_exists(self.project, self.path, self.genome):
            db.repo_update(self)
        else:
            db.repo_save(self)


    def add_dataset(self, dataset):
        if not dataset.repository_id:
            dataset.repository_id = self.id

        if not dataset.exists():
            dataset.save()
            return True
        return False


    def process_datasets(self):
        """
        process_datasets starts downloading and processing of all datasets in the
        database that belong to the repository and have not been inserted yet.
        """
        if not self.id:
            raise NonpersistantRepository(self, "cannot process datasets for unsaved repository")

        c = list(db.find_not_inserted(self.id, self.data_types))
        log.info("%d datasets in %s require processing", len(c), self)

        datasets = []
        for e in db.find_not_inserted(self.id, self.data_types):
            # reconstruct Datasets from database
            ds = self._make_dataset(e["file_name"], e["type"], e["meta"], e["file_directory"], e["sample_id"], e["repository_id"])
            ds.id = e["_id"]
            # create download dirs
            p = os.path.split(ds.download_path)[0]
            if not os.path.exists(p):
                os.makedirs(p)
            # start processing
            datasets.append(ds)

        p = Pool(max_threads)
        p.map(process, datasets)
        p.close()
        p.join()


    def _make_dataset(self, file_name, type, meta, file_directory, sample_id, repository):
        return Dataset(file_name, type, meta, file_directory, sample_id, repository)
