import os

from log import log
import settings
import client
from dataset import Dataset
from datasources.epigenomic_landscape.epigenomic_landscape_attribute_mapper import EpigenomicLandscapeAttributeMapper

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