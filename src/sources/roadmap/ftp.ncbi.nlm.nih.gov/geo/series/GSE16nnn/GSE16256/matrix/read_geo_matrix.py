import pprint

#files = ["GSE16256-GPL10999_series_matrix.txt", "GSE16256-GPL13393_series_matrix.txt", "GSE16256-GPL9052_series_matrix.txt", "GSE16256-GPL11154_series_matrix.txt",  "GSE16256-GPL16791_series_matrix.txt",  "GSE16256-GPL9115_series_matrix.txt"]
files = ["GSE16256-GPL10999_series_matrix.txt"]

fms = []

for _file in files:
	file_metadata = {}
	samples = {}
	f = open(_file).readlines()
	print _file
	for line in f:
		s_line = line.split("\t")
		#print s_line[0], len(s_line)

		if len(s_line) == 2 and len(s_line[1].strip()) > 0 and s_line[0] != "!Series_sample_id":
			k = s_line[0][1:]
			if not file_metadata.has_key(k):
				file_metadata[k] = []	
			file_metadata[k].append(s_line[1].strip()[1:-1])


		elif len(s_line) > 2:
			k = s_line[0][1:]
			for pos in range(1, len(s_line[1:])):
				if not samples.has_key(pos):
					samples[pos] = {}

				if len(s_line[pos][1:-1].strip()) > 0:
					if not samples[pos].has_key(k):
						samples[pos][k] = []
					samples[pos][k].append(s_line[pos][1:-1])


	file_metadata["samples"] = samples
	pp = pprint.PrettyPrinter(depth=6)

	fms.append(file_metadata)

	for s in file_metadata["samples"]:
		pp.pprint(file_metadata["samples"][s]["Sample_characteristics_ch1"])
		for i in range(1, 5):
			k = "Sample_supplementary_file_%d" % i
			if not file_metadata["samples"][s].has_key(k): break

			pp.pprint(file_metadata["samples"][s][k])
		
		pp.pprint(file_metadata)