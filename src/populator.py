import os
import os.path

import settings
import column_definitions
import repository_factory
from annotations import insert_annotations
from epidb_interaction import PopulatorEpidbClient
from client import DeepBlueClient
from data_sources import project_sources
from genomes import hg19_info, mm9_info, mm10_info, hs37d5_info, GRCm38mm10_info
from histones import insert_histones
from owl_loader import load_owl
from log import log
from sequences import insert_chromosome_sequences
from db import mdb


"""
The Populator maintains the database connection and delegates
tasks to its repositories and their datasets.
"""


class Populator:
    # epidb access data
    username = settings.EPIDB_POPULATOR_USER[0]
    email = settings.EPIDB_POPULATOR_USER[1]
    institution = settings.EPIDB_POPULATOR_USER[2]
    key = None

    def __init__(self):
        self.repositories = set([])

        if os.path.exists(settings.EPIDB_AUTHKEY_FILE):
            self.load_auth_info()

    def __str__(self):
        return "<Populator>"

    """
    setup_epidb sets up access to epidb
    """

    def setup_epidb(self):
        if os.path.exists(settings.EPIDB_AUTHKEY_FILE):
            log.error("setup file %s for epidb already exists",
                      settings.EPIDB_AUTHKEY_FILE)
            # XXX: exit?
            return False

        epidb = DeepBlueClient(address=settings.DEEPBLUE_HOST, port=settings.DEEPBLUE_PORT)
        res, admin_key = epidb.init_system(*settings.EPIDB_INIT_USER)
        if res == "error":
            log.error("error while initializing the system: %s", admin_key)
            return False

        log.info("admin user created successfully")

        epidb.set_key(admin_key)
        res, u = epidb.add_user(self.username, self.email, self.institution)
        if (res == "error"):
            log.error("error while adding populator user: %s", u)
            return False

        user_id, key = u
        res, u = epidb.modify_user_admin(user_id, "permission_level", "INCLUDE_COLLECTION_TERMS", admin_key)


        self.key = key
        log.info("populator user created successfully")

        with open(settings.EPIDB_AUTHKEY_FILE, 'w') as f:
            f.write("%s:%s:%s:%s" % (settings.EPIDB_INIT_USER + (admin_key,)))
            f.write('\n')
            f.write("%s:%s:%s:%s" % (settings.EPIDB_POPULATOR_USER + (key,)))

        return True

    """
    load_auth_info loads a previously obtained authentication key for
    epidb from the key file, defined in the settings.
    """

    def load_auth_info(self):
        with open(settings.EPIDB_AUTHKEY_FILE, 'r') as f:
            for l in f.readlines():
                (user, email, inst, key) = l.split(':')
                if (user, email, inst) == (self.username, self.email, self.institution):
                    self.key = key
                    break

        log.info("loaded authentication key successfully")

    def insert_basic_data(self):

        self.insert_genomes()
        self.insert_epigenetic_marks()
        self.insert_technologies()
        self.insert_projects()

    def insert_genomes(self):
        epidb = PopulatorEpidbClient()

        print epidb.add_genome("hg19", "Human Genome Assembly hg19", hg19_info)
        print epidb.add_genome("mm9", "Mouse Genome Assembly mm9", mm9_info)
        print epidb.add_genome("mm10", "Mouse Genome Assembly mm10", mm10_info)
        print epidb.add_genome("hs37d5", "Human Genome Assembly HS37 with Decoy Sequences", hs37d5_info)
        print epidb.add_genome("GRCm38mm10", "Mouse Genome Assembly GRCm38 (compatible with mm10)", GRCm38mm10_info)

        insert_chromosome_sequences(epidb, "hg19", self.key)
        insert_chromosome_sequences(epidb, "hs37d5", self.key)
        insert_chromosome_sequences(epidb, "GRCm38mm10", self.key)


    def insert_epigenetic_marks(self):
        # TODO: enforce in the datasource the epigenetic mark
        epidb = PopulatorEpidbClient()

        epidb.add_epigenetic_mark("DNA Methylation", "DNA Methylation")
        epidb.add_epigenetic_mark("DNaseI", "DNaseI hypersensitive sites")
        epidb.add_epigenetic_mark("TFBS", "Transcription factor binding sites")
        epidb.add_epigenetic_mark("Chromatin State Segmentation",
                                  "A common set of states across the cell types were learned by computationally integrating ChIP-seq data for nine factors plus input using a Hidden Markov Model (HMM). In total, fifteen states were used to segment the genome.")
        epidb.add_epigenetic_mark("RNA", "RNA data - Transcriptome")
        epidb.add_epigenetic_mark("mRNA", "Messenger RNA")
        epidb.add_epigenetic_mark("flRNA", "Full length RNA")
        epidb.add_epigenetic_mark("tRNA", "Transfer ribonucleic acid")
        epidb.add_epigenetic_mark("snRNA", "small nuclear RNA")
        epidb.add_epigenetic_mark("Input",
                                  "Experiment Input Data. It is not an epigenetic mark")
        epidb.add_epigenetic_mark("Control",
                                  "Experiment Control Data. It is not an epigenetic mark")
        epidb.add_epigenetic_mark("Regulatory Elements", "General term used by FAIRE-Seq")


        insert_histones(epidb)

    def insert_technologies(self):
        epidb = PopulatorEpidbClient()

        epidb.add_technique("RRBS", "Reduced representation bisulfite sequencing", {})
        epidb.add_technique("Infinium 450k", "Infinium HumanMethylation450", {})
        epidb.add_technique("BisulfiteSeq",
                            "Bisulfite sequencing or Bisulphite sequencing", {})
        epidb.add_technique("WGSBS", "Whole genome shotgun bisulfite sequencing (WGSBS) is every bit as fierce as its name suggests. Shotgun sequencing is a processes for sequencing a lot DNA, such as a whole genome. The DNA is broken up into short fragments which are then sequenced in parallel. The many short fragments (or \"reads\") are then aligned in a computer program to recreate the entire sequence (Anderson, 1981). http://epigenie.com/epigenetics-research-methods-and-technology/methylcytosine-5mc-analysis/bisulfite-conversion/wgsbs-whole-genome-shotgun-bisulfite-sequencing/", {})
        epidb.add_technique("ChIP-seq", "ChIP-sequencing", {})
        epidb.add_technique("ChIP-seq Uniform",
                            "ChIP-sequencing performed uniform processing on datasets produced by multiple data production groups in the ENCODE Consortium",
            {})
        epidb.add_technique("DNase-seq", "DNase I hypersensitive sites sequencing", {})
        epidb.add_technique("DNase-seq Uniform",
                            "DNase I hypersensitive sites sequencing performed uniform processing on datasets produced by multiple data production groups in the ENCODE Consortium",
            {})
        epidb.add_technique("Chromatin State Segmentation by HMM",
                            "ChIP-seq data from the Broad Histone track was used to generate this track. Data for nine factors plus input and nine cell types was binarized separately at a 200 base pair resolution based on a Poisson background model. The chromatin states were learned from this binarized data using a multivariate Hidden Markov Model (HMM) that explicitly models the combinatorial patterns of observed modifications (Ernst and Kellis, 2010). To learn a common set of states across the nine cell types, first the genomes were concatenated across the cell types. For each of the nine cell types, each 200 base pair interval was then assigned to its most likely state under the model. Detailed information about the model parameters and state enrichments can be found in (Ernst et al, accepted).",
            {})
        epidb.add_technique("RNA-seq", "RNA sequencing", {})
        epidb.add_technique("Microarray", "Various microarray techniques", {})
        epidb.add_technique("Affymetrix Mouse Genome 430 2.0 Array", "", {})
        epidb.add_technique("WGBS", "Whole-genome bisulfite sequencing", {})
        epidb.add_technique("MeDIP/MRE", "MeDIP/MRE methylation data we used the output of the mCRF tool (Stevens et al. (2013)) that reports fractional methylation in the range from 0 to 1 and uses an internal BWA mapping.", {})
        epidb.add_technique("NOMe-seq", "Nucleosome Occupancy and Methylome sequencing", {})
        epidb.add_technique("FAIRE-seq", "FAIRE-Seq (Formaldehyde-Assisted Isolation of Regulatory Elements) is a method in molecular biology used for determining the sequences of those DNA regions in the genome associated with regulatory activity.", {})


    def insert_projects(self):
        # TODO: Load these information from the source file.
        # TODO: put in the source
        epidb = PopulatorEpidbClient()

        epidb.add_project("ENCODE", "The ENCODE Project: ENCyclopedia Of DNA Elements")
        epidb.server.set_project_public("ENCODE", True)
        epidb.add_project("BLUEPRINT Epigenome",
                          "BLUEPRINT - A BLUEPRINT of Haematopoietic Epigenomes")
        epidb.server.set_project_public("BLUEPRINT Epigenome", True)
        epidb.add_project("Mouse ENCODE",
                          "The ENCODE Project: ENCyclopedia Of DNA Elements - Mouse")
        epidb.server.set_project_public("Mouse ENCODE", True)
        epidb.add_project("epigenomic landscape - hematopoiesis - mouse - pilot", "")
        epidb.add_project("DEEP", "DEEP - Deutsches Epigenom Programm")
        epidb.server.set_project_public("DEEP", True)
        epidb.add_project("Roadmap Epigenomics", "NIH Roadmap Epigenomics Mapping Consortium")
        epidb.server.set_project_public("Roadmap Epigenomics", True)

    def create_columns(self):
        epidb = PopulatorEpidbClient()

        for col in column_definitions.SIMPLE:
            epidb.create_column_type_simple(*col)
        for col in column_definitions.CATEGORY:
            epidb.create_column_type_category(*col)

        for col in column_definitions.RANGE:
            epidb.create_column_type_range(*col)


    def process_annotations(self):
        insert_annotations(self.key)

    def process_ontology(self):
        load_owl(self.key)

    """
    setup_collections configures database internals for the Populator database
    """

    def setup_collections(self):
        mdb.repositories.ensure_index([("project", 1),("path", 1), ("genome", 1)], unique=True)
        mdb.datasets.ensure_index([("file_name", 1), ("repository_id", 1)], unique=True)

    def load_repositories(self):
        for sources in project_sources:
            for (proj, genome, url) in sources:
                r = repository_factory.load(proj, genome, url)
                log.info("%s loaded", str(r))
                self.repositories.add(r)
                r.save()
        log.info("populator initialized with %d repositories", len(self.repositories))

    """
    check_reposoitories reads all repositories and flags new datasets.
    """

    def check_repositories(self):
        self.setup_collections()

        for rep in self.repositories:
            rep.read_datasets()

        log.info("repositories checked successfully")


    """
    process_repositories downloads all new datasets and inserts them
    into epidb (processing).
    Note: For this method to take any effect check_repositories must be
    invoked beforehand.
    """

    def process_repositories(self):
        log.info("processing repositories")
        for rep in self.repositories:
            rep.process_datasets()

        log.info("repositories processed successfully")

