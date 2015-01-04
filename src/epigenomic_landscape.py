import os
import threading
import re

from log import log

import db
import settings
import client

from repository import Repository
from dataset import Dataset
from attribute_mapper import AttributeMapper

_regex_eq = re.compile("(.*?)=(.*)")
_regex_dp = re.compile(".*?=(.*?):(.*)")

class EpigenomicLandscapeRepository(Repository):

    def __init__(self, project, genome, path, user_key):
        super(EpigenomicLandscapeRepository, self).__init__(project, genome, ["bed", "bedgraph", "wig"], path, user_key)

    def read_datasets(self):

        for file_name in os.listdir(os.path.join(self.path, "experiments")):
            if os.path.splitext(file_name)[1][1:] == "exp":

                lines = open(os.path.join(self.path, "experiments", file_name)).readlines()

                meta = {}
                file_type = file_path = sample_id = ""
                for line in lines:
                    match_eq = _regex_eq.match(line)

                    if match_eq.group(1) == "data":
                        file_path = os.path.join(self.path, "experiments", match_eq.group(2).strip())
                        file_type = os.path.splitext(line)[1][1:].strip()
                    elif match_eq.group(1) == "sample":
                        sample_line = match_eq.group(2).strip()
                        path = os.path.join(self.path, "samples", sample_line + ".sample")
                        if os.path.exists(path):
                            sample_id = self.process_sample_file(path)
                        else:
                            sample_id = sample_line
                    else:
                        meta[match_eq.group(1)] = match_eq.group(2).strip()

                if not (file_path and file_type and sample_id):
                    log.error("Error parsing " + os.path.join(self.path, "experiments", file_name))
                    return

                dataset = EpigenomicLandscapeDataset(file_path, file_type, meta,
                                                     file_directory=os.path.join(self.path, "samples"),
                                                     sample_id=sample_id, repo_id=self.id)
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

    def process_sample_file(self, path):
        """Returns ID for sample in path, inserts sample into DeepBlue if it's not already
        :param path: path to .sample-file
        :return: DeepBlue's ID for that sample
        """
        lines = open(path).readlines()

        extra_metadata = {}
        biosource = ""

        for line in lines:
            match_eq = _regex_eq.match(line)

            group1 = match_eq.group(1)
            if group1 == "biosource":
                biosource = match_eq.group(2)
            if group1 == "name":
                extra_metadata["name"] = match_eq.group(2)
            if group1.startswith("extra_metadata"):
                match_dp = _regex_dp.match(line)
                extra_metadata[match_dp.group(1)] = match_dp.group(2)

        if not biosource:
            log.error("Error parsing " + path)
            return ""

        epidb = client.EpidbClient(settings.DEEPBLUE_HOST, settings.DEEPBLUE_PORT)
        (s, samples) = epidb.list_samples(biosource, extra_metadata, self.user_key)
        if samples:
            return samples[0][0]
        else:
            (s, sample_id) = epidb.add_sample(biosource,
                                              extra_metadata,
                                              self.user_key)
            return sample_id


    def _make_dataset(file_name, type, meta, file_directory, sample_id, repository):
        return EpigenomicLandscapeDataset(file_name, type, meta, file_directory, sample_id, repository)

class EpigenomicLandscapeAttributeMapper(AttributeMapper):
    def __init__(self, dataset):
        super(self.__class__, self).__init__(dataset)

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
        return os.path.join(self.file_directory, self.file_name)

    def _load(self):
        pass

    def _process(self, user_key=None):
        log.info("processing dataset %s", self)

        am = EpigenomicLandscapeAttributeMapper(self)

        #if not os.path.exists(self.download_path):
        #    raise IOError(self.download_path, self.file_name)

        am.extra_metadata['__local_file__'] = self.download_path

        #f = open(self.download_path, 'r')
        #file_content = f.read()
        #f.close()
        file_content = ""
        #TODO ;)

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

        epidb = client.EpidbClient(settings.DEEPBLUE_HOST, settings.DEEPBLUE_PORT)

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