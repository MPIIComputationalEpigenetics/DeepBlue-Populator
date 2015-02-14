import threading
import os.path
import abc

import db
from dataset import Dataset
from settings import max_threads, max_downloads
from log import log


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


class Repository(object):
    """
    A Repository refers to a source of datasets belonging to a certain project.
    It detects the available datasets in the repository and can coordinate their
    retrival and processing.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, proj, genome, data_types, path, user_key):
        self.project = proj
        self.genome = genome
        self.data_types = data_types
        self.path = path
        self.user_key = user_key

    def __str__(self):
        return "<Repository: [%s, %s]>" % (self.project, self.path)

    def __eq__(self, other):
        if not isinstance(other, Repository):
            return False
        return self.path == other.path

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
        idl = db.repo_id(self.project, self.path)
        if not idl:
            return None
        return idl["_id"]


    @abc.abstractmethod
    def read_datasets(self):
        """
        read_datasets analyses the repositorie's index file and flags
        new datasets.
        """
        pass

    def exists(self):
        """
        exists checks if the repository has already been added to the database.
        """
        return db.repo_exists(self.project, self.genome, self.data_types, self.path)

    def has_unimported(self):
        """
        has_unimported checks if the repository
        """
        return db.count_unimported(self.project, self.path)

    def save(self):
        """
        save saves the repository to the database if it doesn't exist already.
        """
        if self.exists():
            return

        #If repository of the same project with same path exists: update it
        if db.repo_exists(self.project, self.path):
            db.repo_remove(self.project, self.path)

        doc = {
            "project": self.project,
            "genome": self.genome,
            "data_types": self.data_types,
            "path": self.path
        }
        if self.id:
            doc["_id"] = self.id

        log.debug("saving repository: %s", doc)
        db.repo_save(doc)


    def add_dataset(self, dataset):
        if not dataset.repository_id:
            dataset.repository_id = self.id

        if not dataset.exists():
            dataset.save()
            return True
        return False


    def process_datasets(self, key=None):
        """
        process_datasets starts downloading and processing of all datasets in the
        database that belong to the repository and have not been inserted yet.
        """
        if not self.id:
            raise NonpersistantRepository(self, "cannot process datasets for unsaved repository")

        c = list(db.find_not_inserted(self.id, self.data_types))
        log.info("%d datasets in %s require processing", len(c), self)

        threads = []
        load_sem = threading.Semaphore(max_downloads)
        process_sem = threading.Semaphore(max_threads)

        def process(dataset):
            try:
                dataset.load(load_sem)
                dataset.process(key, process_sem)
                dataset.save()
            except IOError as ex:
                log.exception("error on downloading or reading dataset of %s failed: %s", dataset, ex)
            except Exception as ex:
                log.exception("processing of %s failed %s", dataset, repr(ex))

        for e in db.find_not_inserted(self.id, self.data_types):
            # reconstruct Datasets from database
            ds = self._make_dataset(e["file_name"], e["type"], e["meta"], e["file_directory"], e["sample_id"], e["repository_id"])
            ds.id = e["_id"]
            # create download dirs
            p = os.path.split(ds.download_path)[0]
            if not os.path.exists(p):
                os.makedirs(p)
            # start processing
            t = threading.Thread(target=process, args=(ds,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


    def _make_dataset(self, file_name, type, meta, file_directory, sample_id, repository):
        return Dataset(file_name, type, meta, file_directory, sample_id, repository)
