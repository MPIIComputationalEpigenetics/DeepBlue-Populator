import codecs
import os.path

f = codecs.open("20140317.data.index", encoding='iso_8859_1')

lines = f.read().split("\n")

header_keys = lines[0].split()

print "header"
print header_keys
print "-" * 20


sample_extra_info_keys = ["SAMPLE_ID", "SAMPLE_NAME", "DISEASE", "BIOMATERIAL_PROVIDER",
		"BIOMATERIAL_TYPE", "DONOR_ID", "DONOR_SEX", "DONOR_AGE", "DONOR_HEALTH_STATUS", "DONOR_ETHNICITY", "DONOR_REGION_OF_RESIDENCE",
		"SPECIMEN_PROCESSING", "SPECIMEN_STORAGE"]

remove_fields = ["FILE_MD5", "FILE_SIZE", "MOLECULE"]

lines_info = {}

for l in lines[1:]:
	if not l.strip():
		continue

	line_info = {}
	values = l.split("\t")


	sample_extra_info = {}
	for k in sample_extra_info_keys:
	#	sample_extra_info[k] = line_info[k]

	#print line_info

	#print sample_extra_info["BIOMATERIAL_PROVIDER"]

	#print "add_sample(" + line_info["CELL_TYPE"] + "," + str(sample_extra_info) + ")"

	#file_path = line_info["FILE"]
	#file_name = file_path.split("/")[-1]

	#file_type = file_name.split(".")[-1]
	#if file_type == "gz":
	#	file_type = file_name.split(".")[-2]
	#print file_name
	#print file_type

	
	#print os.path.dirname(file_path)

	#for field in line_info.keys():
	#	if field in sample_extra_info_keys + remove_fields:
	#		line_info.pop(field)

	#print line_info


	#print line_info
