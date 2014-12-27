import os
import threading

from log import log

import db
import settings

from repository import Repository
from dataset import Dataset
from attribute_mapper import AttributeMapper
from client import EpidbClient

class EpigenomicLandscapeRepository(Repository):

    def __init__(self, proj, genome, path, user_key):
        super(EpigenomicLandscapeRepository, self).__init__(proj, genome, ["bed", "bedgraph", "wig"], path, user_key)

    def read_datasets(self):
        #rsync

        for file in os.listdir(self.path):
            if os.path.splitext(file)[1][1:] == "exp":

                lines = open(os.path.join(self.path, file)).readlines()
                meta = {}
                for line in lines:
                    line_split = line.split("=")

                    if line_split[0] == "data":
                        file_path = line_split[1].strip()
                        file_type = os.path.splitext(line)[1][1:].strip()
                    elif line_split[0] == "sample":
                        sample_id = line_split[1].strip()
                    else:
                        meta[line_split[0]] = line_split[1].strip()

                directory = ""

                dataset = EpigenomicLandscapeDataset(file_path, file_type, meta, file_directory=directory, sample_id=sample_id, repo_id=self.id)
                self.add_dataset(dataset)

    def process_datasets(self, key=None):

        def process(dataset):
            try:
                dataset.load(load_sem)
                dataset.process(key, process_sem)
                dataset.save()
            except IOError as ex:
                log.exception("error on downloading or reading dataset of %s failed: %s", dataset, ex)
            except Exception as ex:
                log.exception("processing of %s failed %s", dataset, repr(ex))

        threads = []
        load_sem = threading.Semaphore(settings.max_downloads)
        process_sem = threading.Semaphore(settings.max_threads)

        for e in db.find_not_inserted(self.id, self.data_types):
            ds = EpigenomicLandscapeDataset(e["file_name"], e["type"], e["meta"], e["file_directory"], e["sample_id"], e["repository_id"])
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

    def _make_dataset(file_name, type, meta, file_directory, sample_id, repository):
        return EpigenomicLandscapeDataset(file_name, type, meta, file_directory, sample_id, repository)

class EpigenomicLandscapeAttributeMapper(AttributeMapper):
    def __init__(self, dataset):
        super(self, dataset)

    @property
    def name(self):
        return self.dataset.meta["name"]

    @property
    def genome(self):
        return self.dataset.repository["genome"]

    @property
    def epigenetic_mark(self):
        return self.dataset.meta["epigenetic_mark"]

    @property
    def biosource(self):
        return self.dataset.meta["biosource"]

    @property
    def technique(self):
        return self.dataset.meta["technique"]

    @property
    def project(self):
        return self.dataset.meta["project"]

    @property
    def description(self):
        return self.dataset.meta["description"]

    @property
    def extra_metadata(self):
        return self.dataset.meta

    @property
    def format(self):
        return self.dataset.meta["format"]

class EpigenomicLandscapeDataset(Dataset):

    @property
    def download_path(self):
        #TODO
        raise NotImplementedError()

    def _load(self):
        #TODO
        raise NotImplementedError()
        pass

    def _process(self, user_key=None):
        log.info("processing dataset %s", self)

        am = EpigenomicLandscapeAttributeMapper(self)

        if not os.path.exists(self.download_path):
            raise IOError(self.download_path, self.file_name)

        am.extra_metadata['__local_file__'] = self.download_path

        f = open(self.download_path, 'r')
        file_content = f.read()
        f.close()

        file_split = file_content.split("\n", 1)
        first_line = file_split[0]

        while first_line.startswith('#') or first_line.startswith("track") or first_line.startswith("browser"):
            file_content = file_split[1]
            file_split = file_content.split("\n", 1)
            first_line = file_split[0]
            log.debug(first_line)

        data_splited = file_content.split("\n")
        data_splited = [x for x in data_splited if x]
        data_splited.sort()
        file_content = "\n".join(data_splited)

        epidb = EpidbClient(settings.DEEPBLUE_HOST, settings.DEEPBLUE_PORT)

        if self.sample_id:
            sample_id = self.sample_id
        else:
            (status, samples_id) = epidb.list_samples(am.biosource, {}, user_key)
            if status != "okay" or not len(samples_id):
                log.critical("Sample for biosource %s was not found", am.biosource)
                log.critical(samples_id)
                return
            sample_id = samples_id[0][0]

        if am.format in ["bedgraph", "wig"]:
            exp_name = am.name + "." + am.format
        else:
            exp_name = am.name + ".bed"

        args = (exp_name, am.genome, am.epigenetic_mark, sample_id, am.technique,
        am.project, am.description, file_content, am.format, am.extra_metadata,
        user_key)

        res = epidb.add_experiment(*args)

        if res[0] == "okay" or res[1].startswith("102001"):
            self.inserted = True
            self.insert_error = ""
            self.save()
            log.info("dataset %s inserted ", exp_name)
        else:
            msg = "Error while inserting dataset: res: %s\nexperiment_name: %s\nformat:%s\nfile_content: %s\ndownload_path: %s" % (
                res, am.name, am.format, file_content[0:500], self.download_path)
            self.insert_error = msg
            self.save()
            log.info(msg)

        os.remove(self.download_path)
