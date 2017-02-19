import os.path
import urllib2
import os.path
import pprint

from dataset import Dataset
from repository import Repository
import util
from epidb_interaction import PopulatorEpidbClient


pp = pprint.PrettyPrinter(depth=6)


class BlueprintRepository(Repository):
    def __init__(self, proj, genome, path):
        super(BlueprintRepository, self).__init__(proj, genome,
                                                 ["bed"], path)
                                                # ["RNA_GENE_QUANT_STAR_CRG"], path)
                                                # ["bed", "bigwig", "RNA_GENE_QUANT_STAR_CRG"], path)

    def __str__(self):
        return "<Blueprint Repository: [%s, %s]>" % (self.path, self.data_types)

    """
    index_path is the path to the file which contains information of all
    datasets in the repository.
    """

    @property
    def index_path(self):
        return self.path + "blueprint/releases/20160816/homo_sapiens/20160816.data.index"

    """
    read_datasets analyses the repositorie's index file and flags
    new datasets.
    """
    def read_datasets(self):
        # TODO: convert to the predefined keys
        sample_extra_info_keys = ["SAMPLE_ID", "SAMPLE_NAME", "DISEASE",
                                  "BIOMATERIAL_PROVIDER", "CELL_TYPE", "TISSUE_TYPE",
                                  "BIOMATERIAL_TYPE", "DONOR_ID", "DONOR_SEX",
                                  "DONOR_AGE", "DONOR_HEALTH_STATUS",
                                  "DONOR_ETHNICITY",
                                  "DONOR_REGION_OF_RESIDENCE",
                                  "SPECIMEN_PROCESSING", "SPECIMEN_STORAGE"]

        epidb = PopulatorEpidbClient()

        new = 0

        print self.index_path
        req = urllib2.urlopen(self.index_path)
        content = req.read()
        ucontent = unicode(content, 'iso_8859_1')
        lines = ucontent.split("\n")

        header_keys = lines[0].split()

        for l in lines[1:]:
            if not l.strip():
                continue

            line_info = {}
            values = l.split("\t")

            for i in range(len(header_keys)):
                line_info[header_keys[i]] = values[i]

            sample_extra_info = {}
            for k in sample_extra_info_keys:
                sample_extra_info[k] = line_info[k]

            if line_info["BIOMATERIAL_TYPE"].lower() == "primary cell" or line_info['BIOMATERIAL_TYPE'].lower() == "primary cell culture":
                biosource_name = line_info["CELL_TYPE"]
            elif line_info["BIOMATERIAL_TYPE"].lower() == "primary tissue":
                biosource_name = line_info["TISSUE_TYPE"]
            elif line_info["BIOMATERIAL_TYPE"].lower() == "cell line":
                biosource_name = line_info["CELL_LINE"]
            else:
                print 'Invalid BIOMATERIAL_TYPE: ', line_info['BIOMATERIAL_TYPE']
                print line_info
                print line_info.get("CELL_TYPE", "-")
                print line_info.get("TISSUE_LINE", "-")
                print line_info.get("CELL_LINE", "-")

            if biosource_name.lower() == "none" or not biosource_name.strip():
                print "Invalid biosource name:", biosource_name
                pp.pprint(line_info)
                continue

            if "(" in biosource_name:
                biosource_name_old = biosource_name
                biosource_name = biosource_name.split("(")[0]
                print "Renaming " + biosource_name_old + " to " + biosource_name

            sample_extra_info["source"] = "BLUEPRINT Epigenome"

            epidb.add_biosource(biosource_name, None, {})

            (s, samples) = epidb.list_samples(biosource_name,
                                              sample_extra_info)
            if samples:
                sample_id = samples[0][0]
            else:
                sample_extra_info["source"] = "BLUEPRINT Epigenome"
                (s, sample_id) = epidb.add_sample(biosource_name,
                                                  sample_extra_info)
                if util.has_error(s, sample_id, []):
                    print "Error while loading BLUEPRINT sample:"
                    print biosource_name
                    print sample_extra_info
                    return

            file_path = line_info["FILE"]
            file_full_name = file_path.split("/")[-1]

            meta = line_info

            file_type = file_full_name.split(".")[-1]
            if file_type == "gz":
                file_type = file_full_name.split(".")[-2]
            elif file_type == "bw":
                file_type = "bigwig"
            directory = os.path.dirname(file_path)

            if file_type == "results":
                file_type = meta["FILE_TYPE"]


            ds = Dataset(file_path, file_type, meta, file_directory=directory,
                         sample_id=sample_id)
            if self.add_dataset(ds):
                new += 1
                self.has_updates = True
