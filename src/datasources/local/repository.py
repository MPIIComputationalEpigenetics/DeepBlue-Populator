from __future__ import absolute_import

import os
import threading
import re

from log import log
import db
from epidb_interaction import PopulatorEpidbClient
import settings
import util
from repository import Repository
from datasources.local.dataset import EpigenomicLandscapeDataset


_regex_eq = re.compile("(.*?)=(.*)")
_regex_dp = re.compile(".*?=(.*?):(.*)")

_folder_experiments = "metadata_exp"
_folder_samples = "metadata_sample"
_folder_data = "data"
_fileending_experiments = "exp"
_fileending_samples = "sample"

class EpigenomicLandscapeRepository(Repository):

    def __init__(self, project, genome, path):
        super(EpigenomicLandscapeRepository, self).__init__(project, genome, ["bed", "bedgraph", "wig"], path)


    def read_datasets(self):

        epidb = PopulatorEpidbClient()

        for file_name in os.listdir(os.path.join(self.path, _folder_samples)):
           sample_file = os.path.join(self.path, _folder_samples, file_name)
           print self._get_sample_id(sample_file)


        for file_name in os.listdir(os.path.join(self.path, _folder_experiments)):
            if os.path.splitext(file_name)[1][1:] == _fileending_experiments:

                lines = open(os.path.join(self.path, _folder_experiments, file_name)).readlines()

                meta = {}
                file_type = file_path = sample_id = biosource = ""
                for line in lines:
                    match_eq = _regex_eq.match(line)

                    if match_eq.group(1) == "data":
                        file_path = match_eq.group(2).strip()
                        file_type = os.path.splitext(line)[1][1:].strip()
                    elif match_eq.group(1) == "biosource":
                        biosource = match_eq.group(2).strip()
                    elif match_eq.group(1) == "sample":
                        sample_line = match_eq.group(2).strip()
                        path = os.path.join(self.path, _folder_samples , sample_line + "." + _fileending_samples)
                        if os.path.exists(path):
                            #Line is path for .sample file
                            sample_id = self._get_sample_id(path)
                        elif sample_line.startswith("GSM"):
                            #Line is Sample ID from GSM
                            (status, id) = epidb.add_sample_from_gsm(biosource, sample_line)
                            if id.startswith("The ID"):
                                id_split = id.split(" ")
                                sample_id = id_split[len(id_split) - 1]
                            else:
                                sample_id = id
                        elif sample_line.startswith("s") and sample_line[1:].isalnum():
                            #Line is DeepBlue sampleID
                            sample_id = sample_line
                    elif match_eq.group(1):
                        meta[match_eq.group(1)] = match_eq.group(2).strip()

                if not (file_path and file_type and sample_id):
                    log.error("Error parsing " + os.path.join(self.path, _folder_experiments, file_name) + " (file_path: '" + str(file_path) + "' file_type: '" + str(file_type) + "' sample_id: '" + str(sample_id)+ "')")
                    continue

            	file_full_name = file_path.split("/")[-1]
           	file_type = file_full_name.split(".")[-1]
            	if file_type == "gz":
                	file_type = file_full_name.split(".")[-2]
            	directory = os.path.dirname(file_path)

		if not directory:
			directory = os.path.join(self.path, _folder_data)

		if file_type == "bg":
			file_type = "bedgraph"

        	dataset = EpigenomicLandscapeDataset(file_path, file_type, meta,
                                                     file_directory=directory,
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

    def _get_sample_id(self, path):
        """Returns ID for sample in path, inserts sample into DeepBlue if it's not already
        :param path: path to .sample-file
        :return: SampleID
        """
        epidb = PopulatorEpidbClient()

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
                    extra_metadata[match_dp.group(1)] = match_dp.group(2)

        if not biosource:
            log.error("Error parsing sample file: " + path + " - BioSource not informed. ")
            return ""

        extra_metadata["source"] = self.project
	print biosource
	print extra_metadata
        (s, sample_id) = epidb.add_sample(biosource, extra_metadata)
        print "new sample:" , sample_id
        if util.has_error(s, sample_id, []):
            log.error("Sample not inserted " + path + " - " + sample_id)

        return sample_id


    def _make_dataset(self, file_name, type, meta, file_directory, sample_id, repository):
        return EpigenomicLandscapeDataset(file_name, type, meta, file_directory, sample_id, repository)
