import os.path
import urllib2
import os.path
import pprint
import json

from dataset import Dataset
from repository import Repository
import util
from epidb_interaction import PopulatorEpidbClient

pp = pprint.PrettyPrinter(depth=6)

project_name = "Blueprint HSC differentiation"

class ProgenitorsRepository(Repository):
    def __init__(self, proj, genome, path):
        super(ProgenitorsRepository, self).__init__(proj, genome, ["bigwig"], path)

    def __str__(self):
        return "<Progenitors Repository: [%s, %s]>" % (self.path, self.data_types)

    @property
    def index_path(self):
        return "datasources/progenitors/progenitor_trackhub.json"

    def read_datasets(self):
        epidb = PopulatorEpidbClient()

        j = json.load(open(self.index_path))

        hub_description = j['hub_description']
        genome = hub_description['assembly']
        project_description = hub_description['description'] + " " + hub_description['description_url']

        add_project = (project_name, project_description)
        print epidb.add_project(*add_project)

        datasets = j["datasets"]
        samples = j["samples"]

        map_sample = {}

        for s_id in samples:
            sample = samples[s_id]
            biosource_url = sample['sample_ontology_uri'].split(";")[0]
            sample["source"] = project_name
            s, bs = epidb.list_biosources({"url": biosource_url})
            print s, bs
            biosource = bs[0][1]
            add_sample = (biosource, sample)
            map_sample[s_id] = add_sample

        for d in datasets:
            dataset = datasets[d]
            dataset_name = d
            sample_id = dataset['sample_id']
            epigenetic_mark = dataset['experiment_attributes']['experiment_type']
            technique = dataset['experiment_attributes']['assay_type']
            sample = map_sample[dataset['sample_id']]
            (status, db_sample_id) = epidb.add_sample(sample[0], sample[1])

            extra_metadata = {}
            extra_metadata['experiment_ontology_uri'] = dataset['experiment_attributes']['experiment_ontology_uri']
            extra_metadata['reference_registry_id'] = dataset['experiment_attributes']['reference_registry_id']

            for key in dataset['analysis_attributes']:
                extra_metadata[key] = dataset['analysis_attributes'][key]


            for f in dataset['browser']:
                file = dataset['browser'][f][0]

                data_url = file['big_data_url']
                extra_metadata['data_type'] = f

                name = data_url.split("/")[-1]

                meta = {"genome": genome,
                            "epigenetic_mark": epigenetic_mark,
                            "sample": db_sample_id,
                            "technique": technique,
                            "project": project_name,
                            "description": sample[1]['cell_type'],
                            "data_url": data_url,
                            "extra_metadata": extra_metadata}

                print meta
                ds = Dataset(data_url, "bigwig", meta, sample_id=db_sample_id)

                if self.add_dataset(ds):
                    self.has_updates = True

