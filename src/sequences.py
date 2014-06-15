import gzip
import os
import itertools

from multiprocessing import Pool

from client import EpidbClient
from settings import DATA_DIR, DEEPBLUE_HOST, DEEPBLUE_PORT, max_threads
from log import log

def insert_sequence(t):
	user_key = t[0]
	seq_info = t[1]

	print seq_info

	log.info("Inserting %s for %s" %(seq_info["genome"], seq_info["chromosome"]))

	sequence = gzip.open(seq_info["sequence_path"]).read()

	epidb = EpidbClient(DEEPBLUE_HOST, DEEPBLUE_PORT)

	print epidb.upload_chromosome(seq_info["genome"], seq_info["chromosome"], sequence, user_key)


def insert_chromosome_sequences(epidb, genome, user_key):
	seqs_dir = os.path.join(DATA_DIR, "genomes/", genome)

  	seq_infos = []

	for file_name in os.listdir(seqs_dir):
		if file_name.endswith(".gz"):
			chromosome = file_name.split(".")[0]
			f_full = os.path.join(seqs_dir, file_name)
						
			seq_info = {}
			seq_info["genome"] = genome
			seq_info["chromosome"] = chromosome
			seq_info["sequence_path"] = f_full

			seq_infos.append(seq_info)

	total = len(seq_infos)
  	count = 0
  	p = Pool(max_threads)
  	log.info("Inserting Chromosome Sequence. Total of " + str(total) + " sequences.")    

  	p.map(insert_sequence, itertools.izip(itertools.repeat(user_key), seq_infos))
  
  	p.close()
  	p.join()