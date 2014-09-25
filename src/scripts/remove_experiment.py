from pymongo import MongoClient

print "************************************"
print "*  Use this script VERY carefully. *"
print "************************************"

experiment_name = raw_input('What is the name of the experiment: ')
experiment_name_up = raw_input('AGAIN: What is the name of the experiment. Put a ! in the end! : ')

if not experiment_name_up.startswith(experiment_name) or not experiment_name_up[-1] == "!":
	print "Names does not match."
	quit()

DEEPBLUE_MONGO_DB_HOST = "localhost"
DEEPBLUE_MONGO_DB_PORT = 27017
DEEPBLUE_MONGO_DB_DATABASE = "deepblue"

print DEEPBLUE_MONGO_DB_HOST
print DEEPBLUE_MONGO_DB_PORT
print DEEPBLUE_MONGO_DB_DATABASE

user = "Populator"

_client = MongoClient(DEEPBLUE_MONGO_DB_HOST, DEEPBLUE_MONGO_DB_PORT)

db = _client[DEEPBLUE_MONGO_DB_DATABASE]

experiment = db.experiments.find_one({"name": experiment_name, "user": user})

if not experiment:
	print 'Experiment ' + experiment_name + ' not found'
	quit()

experiment_id = experiment['_id']
dataset_id = experiment['D']
genome_name = experiment['norm_genome']

print experiment_id
print dataset_id

genome = db.genomes.find_one({"norm_name": genome_name})

for chromosome in genome['chromosomes']:
	collection_name = "regions."+genome_name+"."+chromosome["name"]
	print 'Removing experiment data from ' + collection_name
	print db[collection_name].remove({"D": dataset_id})

db.experiments.remove({"_id": experiment_id})
