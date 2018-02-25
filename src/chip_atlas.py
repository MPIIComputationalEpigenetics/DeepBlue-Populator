from collections import namedtuple, defaultdict
from pprint import pprint
from epidb_interaction import PopulatorEpidbClient
from dataset import Dataset
from repository import Repository

from log import log

from datasources.encode.transcription_factors import EncodeTFs



class ChIPAtlas(Repository):

    def __init__(self, proj, genome, path):
        super(ChIPAtlas, self).__init__(
            proj, genome, ["bed", "bigBed"], path)
        self.encode_tfs = EncodeTFs(genome)
        self.epigenetic_marks = []

    def __str__(self):
        return "<ChIPAtlas Repository: [%s, %s]>" % (self.path, self.data_types)

    @property
    def index_path(self):
        """
        index_path is the path to the file which contains information of all datasets in the repository.
        """
        return "experimentList.tab"

    def read_datasets(self):
        """
        File description:
        1	Experimental ID (SRX, ERX, DRX)	SRX097088
        2	Genome assembly	hg19
        3	Antigen class	TFs and others
        4	Antigen	GATA2
        5	Cell type class	Blood
        6	Cell type	K-562
        7	Cell type description	Primary Tissue=Blood|Tissue Diagnosis=Leukemia Chronic Myelogenous
        8	Processing logs (# of reads, % mapped, % duplicates, # of peaks [Q < 1E-05])	30180878,82.3,42.1,6691
        9	Title	GSM722415: GATA2 K562bmp r1 110325 3
        10	Meta data submitted by authors	source_name=GATA2 ChIP-seq K562 BMP
              cell line=K562
              chip antibody=GATA2
              antibody catalog number=Santa Cruz SC-9008
        """

        keys = ["ID", "genome", "antigen_class", "antigen",
                "cell_type_class", "cell_type", "cell_type_description",
                "processing_logs", "title", "extra_metadata"]

        cell_types_map = {"prostate": "prostate gland"}

        epidb = PopulatorEpidbClient()

        Experiment = namedtuple('Experiment', keys, verbose=True)

        # Histone Modification
        # Control Data
        # Transcription Factor Binding Sites


        missing = defaultdict(int)
        total = 0
        good = 0
        bad = 0
        new = 0
        f = open("experimentList.tab")
        #f = []
        for line in f:
            total += 1
            if total % 1000 == 0:
                print total
                print missing
                print len(missing)
                print good
                print bad

            line = line.strip()
            s = line.split("\t", 9)
            if len(s) == 9:   # Not extra metadata
                s.append("")
            experiment = Experiment._make(s)

            genome = getattr(experiment, "genome")
            if genome.lower() != self.genome.lower():
                continue

            antigen = getattr(experiment, "antigen")

            if antigen == "H3K9K14ac":
                antigen = "H3K9/14ac"


            if antigen == "DNase-Seq":
                antigen = "DNA Accessibility"


            if antigen.lower() in ["na", "unclassified"]:
                bad += 1
                continue

            if antigen.lower() == "input control":
                antigen = "Input"

            if not self.epigenetic_marks:
                print "loading epigenmetic marks"
                (s, ems) = epidb.list_epigenetic_marks({})
                self.epigenetic_marks = [em[1].lower() for em in ems]

            if antigen.lower() not in self.epigenetic_marks:
                log.info("it is not in " + antigen)
                tf_metadata = self.encode_tfs[antigen]
                if not tf_metadata:
                    log.error("Metadata for " + antigen + " not found")
                    continue

                print 'Importing ', antigen
                (s, em) = epidb.add_epigenetic_mark(antigen, str(tf_metadata), {"category": "Transcription Factor Binding Sites"})
                if (s == "okay"):
                    print em
                    self.epigenetic_marks.append(antigen)
                else:
                    log.error("Still missing %s %s", antigen, em)

            biosource = None
            cell_type = getattr(experiment, "cell_type").lower()
            if cell_type in ["na", "unclassified"]:
                bad += 1
                continue

            status, _ = epidb.is_biosource(cell_type)
            if status == "okay":
                biosource = cell_type
            elif cell_type in cell_types_map:
                biosource = cell_types_map[cell_type]
            else:
                cell_type_class = getattr(experiment, "cell_type_class").lower()
                status, _ = epidb.is_biosource(cell_type_class)
                if status == "okay":
                    biosource = cell_type_class
                elif cell_type_class in cell_types_map:
                    biosource = cell_types_map[cell_type_class]
                else:
                    missing[(cell_type, cell_type_class)] += 1
                    bad += 1
                    continue

            good += 1

            cell_type_description = getattr(experiment, "cell_type_description")
            if cell_type_description == "NA":
                sample_info = {}
            else:
                sample_info = dict([key.split("=") for key in cell_type_description.split("|")])

            sample_info["source"] = "ChIP-Atlas"
            status, sample_id = epidb.add_sample(biosource, sample_info)

            ID = getattr(experiment, "ID")
            #for threshold in ["05", "10", "20"]:
            # We will include only the data with q-value <= 10
            for threshold in ["10"]:
                file_url = "http://dbarchive.biosciencedbc.jp/kyushu-u/{0}/eachData/bed{2}/{1}.{2}.bed".format(self.genome, ID, threshold)
                ds = Dataset(file_url, "bed", experiment._asdict(), sample_id=sample_id)
                if self.add_dataset(ds):
                    new += 1
                    self.has_updates = True

        pprint(missing)
        print bad
        print new
        print good
