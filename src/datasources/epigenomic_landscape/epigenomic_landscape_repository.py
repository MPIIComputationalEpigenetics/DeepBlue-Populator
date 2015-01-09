import os
import threading
import re

from log import log
import db
import settings
import client
import util
from repository import Repository
from datasources.epigenomic_landscape.epigenomic_landscape_dataset import EpigenomicLandscapeDataset


_regex_eq = re.compile("(.*?)=(.*)")
_regex_dp = re.compile(".*?=(.*?):(.*)")

class EpigenomicLandscapeRepository(Repository):

    def __init__(self, project, genome, path, user_key):
        super(EpigenomicLandscapeRepository, self).__init__(project, genome, ["bed", "bedgraph", "wig"], path, user_key)
        #TODO: shouldn't  be called here:
        init(user_key)


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
                            sample_id = self._process_sample_file(path)
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

    def _process_sample_file(self, path):
        """Returns ID for sample in path, inserts sample into DeepBlue if it's not already
        :param path: path to .sample-file
        :return: Sample name
        """
        epidb = client.EpidbClient(settings.DEEPBLUE_HOST, settings.DEEPBLUE_PORT)

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
                if match_dp.group(2):
                    epidb.add_sample_field(match_dp.group(1), "string", None, self.user_key)
                    extra_metadata[match_dp.group(1)] = match_dp.group(2)

        if not biosource:
            log.error("Error parsing " + path)
            return ""

        (s, samples) = epidb.list_samples(biosource, extra_metadata, self.user_key)
        if samples:
            sample_id = samples[0][0]
        else:
            if not epidb.is_biosource(biosource, self.user_key)[0] == "okay":
                log.error("biosource " + biosource + " doesn't exist " + self.path)

            (s, sample_id) = epidb.add_sample(biosource, extra_metadata, self.user_key)
            if util.has_error(s, sample_id, []):
                log.error("Sample not inserted " + path)

        return sample_id


    def _make_dataset(file_name, type, meta, file_directory, sample_id, repository):
        return EpigenomicLandscapeDataset(file_name, type, meta, file_directory, sample_id, repository)


def init(user_key):
    epidb = client.EpidbClient(settings.DEEPBLUE_HOST, settings.DEEPBLUE_PORT)
    epidb.add_sample_field("name", "string", None, user_key)