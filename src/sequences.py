import gzip
import os

from settings import DATA_DIR, log

genome = "hg19"

def insert_chromosome_sequences(epidb, genome, user_key):
	genomes = DATA_DIR + "genomes/" + genome + "/"

	for file_name in os.listdir(genomes):
		if file_name .endswith(".gz"):
			chromosome = file_name.split(".")[0]
			f_full = genomes + file_name
			sequence = gzip.open(f_full).read()

		 	log.info("Inserting %s for %s" %(chromosome, genome) )

			print epidb.upload_chromosome(genome, chromosome, sequence, user_key)
