import os
import urllib

import settings
import util
from client import EpidbClient
from settings import DEEPBLUE_HOST, DEEPBLUE_PORT
from log import log


"""
A Vocabulary has a source which is a file or an URL. It can read cell line
and antibody entries from the source.
"""


class ControledVocabulary:
    def __init__(self, fromURL=False):
        self.biosources = []
        self.antibodies = {}

        f = self._load_data(fromURL)
        self.data = self._process_data(f)
        f.close()

    """
    parses the data in the provided file and fills the antibody and cell line lists.
    """

    def _process_data(self, f):
        current = None

        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                continue

            (key, value) = line.split(" ", 1)
            key = key.strip()
            value = value.strip()

            if key == "term":
                # new "term" key finishes the last object
                if current:
                    if current["type"] == "Cell Line":
                        self.biosources.append(current)
                    elif current["type"] == "Antibody":
                        if not "_(" in current["term"]:
                            self.antibodies[current["term"]] = current
                        else:
                            label = current["term"].split("_(")[0]
                            if not self.antibodies.has_key(label):
                                self.antibodies[label] = current


                # start a new object
                current = {}
                current["term"] = value

            # normalize key
            if key == "targetDescription":
                key = "description"

            current[key] = value.strip()

        # add very last object
        if current:
            if current["type"] == "Cell Line":
                self.biosources.append(current)
            elif current["type"] == "Antibody" and not "_(" in current["term"]:
                self.antibodies.append(current)


    """
    retrieves the file from the filesystem or URL and returns it
    """

    def _load_data(self, fromURL):
        if fromURL:
            f = urllib.urlopen(settings.VOCAB_URL)
        else:
            f = file(os.path.join(settings.DATA_DIR, "cv/cv.ra"))
        return f


def process_biosource(i, user_key):
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    biosource_name = i["term"]

    fields = {}

    fields["term"] = biosource_name

    if i.has_key("karyotype"):
        fields["karyotype"] = i["karyotype"]

    if i.has_key("lab"):
        fields["lab"] = i["lab"]

    if i.has_key("organism"):
        fields["organism"] = i["organism"]

    if i.has_key("sex") and i["sex"] != "U":
        fields["sex"] = i["sex"]

    if i.has_key("tier"):
        fields["tier"] = i["tier"]

    if i.has_key("age") and i["age"] != "ageUnknown":
        fields["age"] = i["age"]

    if i.has_key("strain") and i["strain"] != "Unknown":
        fields["strain"] = i["strain"]

    if i.has_key("description"):
        fields["description"] = i["description"]

    if i.has_key("tissue"):
        fields["tissue"] = i["description"]

    if i.has_key("lineage") and i["lineage"] != "missing":
        fields["lineage"] = i["lineage"]

    if i.has_key("childOf"):
        fields["childOf"] = i["childOf"]

    fields["source"] = "ENCODE"

    if epidb.is_biosource(biosource_name, user_key)[0] == 'okay':
        (s, s_id) = epidb.add_sample(biosource_name, fields, user_key)
        if util.has_error(s, s_id, []):
            print "(term) Error while creating sample from the given biosource term"
            print s_id
            print biosource_name
            print fields
    elif i.has_key("tissue") and epidb.is_biosource(i["tissue"], user_key)[0] == 'okay':
        (s, s_id) = epidb.add_sample(i["tissue"], fields, user_key)
        print s, s_id
        if util.has_error(s, s_id, []):
            print "(tissue) Error while creating sample from the given biosource term"
            print s_id
            print biosource_name
            print i["tissue"]
            print fields
    # Manual check
    elif biosource_name == "H7-hESC":
        (s, s_id) = epidb.add_sample("embryonic stem cell", fields, user_key)
        if util.has_error(s, s_id, []):
            print "Error while creating sample for this term"
            print biosource_name
            print fields

    elif biosource_name in ["HVMF", "MEF"]:
        (s, s_id) = epidb.add_sample("fibroblast", fields, user_key)
        if util.has_error(s, s_id, []):
            print "Error while creating sample for this term"
            print biosource_name
            print fields

    elif biosource_name == "Mel_2183":
        (s, s_id) = epidb.add_sample("melanoma cell line", fields, user_key)
        if util.has_error(s, s_id, []):
            print "Error while creating sample for this term"
            print biosource_name
            print fields

    elif biosource_name == "Olf_neurosphere":
        (s, s_id) = epidb.add_sample("neuronal stem cell", fields, user_key)
        if util.has_error(s, s_id, []):
            print "Error while creating sample for this term"
            print biosource_name
            print fields

    elif biosource_name == "Pons_OC":
        (s, s_id) = epidb.add_sample("brain", fields, user_key)
        if util.has_error(s, s_id, []):
            print "Error while creating sample for this term"
            print biosource_name
            print fields

    elif biosource_name == "Urothelia":
        (s, s_id) = epidb.add_sample("urothelial cell", fields, user_key)
        if util.has_error(s, s_id, []):
            print "Error while creating sample for this term"
            print biosource_name
            print fields

    elif biosource_name in ["EpiSC-5", "EpiSC-7"]:
        (s, s_id) = epidb.add_sample("epidermal stem cell", fields, user_key)
        if util.has_error(s, s_id, []):
            print "Error while creating sample for this term"
            print biosource_name
            print fields

    elif biosource_name in ["ES-46C", "ES-CJ7", "ES-D3", "ES-E14", "ES-EM5Sox17huCD25", "ES-TT2", "ES-WW6",
                            "ES-WW6_F1KO", "ZhBTc4"]:
        (s, s_id) = epidb.add_sample('embryonic stem cell', fields, user_key)
        if util.has_error(s, s_id, []):
            print "Error while creating sample for this term"
            print biosource_name
            print fields

    else:
        print "Invalid term ", biosource_name, "Please, check the ENCODE CV and include this term."


def manual_curation(user_key):
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    print epidb.set_biosource_synonym("MEL cell line", "MEL", user_key)  # "http://www.ebi.ac.uk/efo/EFO_0003971"
    print epidb.set_biosource_synonym("CH12.LX", "CH12", user_key)  # "http://www.ebi.ac.uk/efo/EFO_0005233"
    print epidb.set_biosource_synonym("hippocampus", "brain hippocampus", user_key)
    print epidb.add_biosource("embryonic lung", "", {"SOURCE": "MPI internal"}, user_key)
    print epidb.add_biosource("chordoma", "Neoplasm arising from cellular remnants of the notochord; cancer",
                              {"SOURCE": "MPI internal"}, user_key)
    print epidb.set_biosource_synonym("induced pluripotent stem cell", "induced pluripotent cell (iPS)", user_key)
    print epidb.set_biosource_synonym("neuron", "neurons", user_key)  # CL0000540
    print epidb.set_biosource_synonym("enucleate erythrocyte", "enucleated erythrocyte", user_key)

    # Cerebrum_frontal_OC
    print epidb.add_biosource("frontal cerebrum", "", {"SOURCE": "MPI internal"}, user_key)
    print epidb.set_biosource_parent("cerebrum", "frontal cerebrum", user_key)


"""
ensure_vocabulary retrieves a set of cell line and antibody vocabulary and
adds them to Epidb.
Note: This method should be called initially. Datasets with unknown vocabulary
will be rejected by Epidb.
"""


def ensure_vocabulary(user_key):
    epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

    voc = ControledVocabulary()
    log.info("adding %d biosource to the vocabulary", len(voc.biosources))
    log.info("adding %d antibodies to the vocabulary", len(voc.antibodies))

    # add biosources to epidb
    for cl in voc.biosources:
        process_biosource(cl, user_key)

    # add antibodies to epidb
    for ab in voc.antibodies:
        antibody = voc.antibodies[ab]
        log.debug("(Encode) Inserting epigenetic_mark %s", antibody["target"])
        (s, em_id) = epidb.add_epigenetic_mark(antibody["target"], antibody["description"], user_key=user_key)
        if util.has_error(s, em_id, ["105001"]): print "(ENCODE CV Error 8): ", em_id

    log.info("vocabulary added successfully")
