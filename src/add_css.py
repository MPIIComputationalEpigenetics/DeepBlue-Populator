# ftp://ftp.ebi.ac.uk/pub/databases/blueprint/releases/current_release/homo_sapiens/secondary_analysis/Segmentation_of_ChIP-Seq_data/SEGMENTATION.tar.gz

import os
import os.path

from cStringIO import StringIO

import xmlrpclib

url = "http://deepblue.mpi-inf.mpg.de/xmlrpc"
user_key = "*******"

server = xmlrpclib.Server(url, allow_none=True)


states = [
    "1_Repressed_Polycomb_High",
    "2_Repressed_Polycomb_Low",
    "3_Low_signal",
    "4_Heterochromatin_High",
    "5_Transcription_High",
    "6_Transcription_Low",
    "7_Genic_Enhancer_High",
    "8_Enhancer_High",
    "9_Active_Enhancer_High",
    "10_Distal_Active_Promoter_2Kb_High",
    "11_Active_TSS_High_Signal_H3K4me3_H3K4me1",
    "12_Active_TSS_High_Signal_H3K4me3_H3K27Ac"
]


root_dir_name = "../data/SEGMENTATION_Blueprint_release_201608"
sub_dirs = ["SEGMENTATION_cell_lines", "SEGMENTATION_disease",
            "SEGMENTATION_healthy", "SEGMENTATION_healthy_model"]

for sub_dir in sub_dirs:
    dir_name = os.path.join(root_dir_name, sub_dir)
    print dir_name
    files = os.listdir(dir_name)

    converted_dir = dir_name + "_converted"

    for original_file_name in files:
        original_file = os.path.join(dir_name, original_file_name)

        if not original_file.endswith(".bed"):
          continue

        SAMPLE_NAME = original_file_name.split("_")[0]
        l = server.list_samples(None, {"SAMPLE_NAME":"{}".format(SAMPLE_NAME)}, user_key)[1]

        if not l:
          SAMPLE_NAME = original_file_name.split("_")[0]+"_"+original_file_name.split("_")[1]
          l = server.list_samples(None, {"SAMPLE_NAME":"{}".format(SAMPLE_NAME)}, user_key)[1]

          if not l:
            print "shit"

        sample_id = l[0][0]

        with open(original_file, 'r') as o_f:
          file_str = StringIO()
          for o_line in o_f:
            (chrm, start, end, stage) = o_line.split()
            stage_value = int(stage[1:]) - 1 # attention to -1 !
            stage_string = states[stage_value]
            file_str.write("{}\t{}\t{}\t{}\n".format(chrm, start, end, stage_string))



          frm = "CHROMOSOME,START,END,NAME"

          em = {
            "software":"ChromHMM package v1.11",
            "contact":"Felipe Were <fnicolau@cnio.es>; Enrique Carrillo <ecarrillo@cnio.es>",
            "url":"ftp.ebi.ac.uk/pub/databases/blueprint/releases/current_release/homo_sapiens/secondary_analysis/Segmentation_of_ChIP-Seq_data/ftp://ftp.ebi.ac.uk/pub/databases/blueprint/releases/current_release/homo_sapiens/secondary_analysis/Segmentation_of_ChIP-Seq_data/SEGMENTATION.tar.gz",
            "centre":"Spanish National Cancer Research Center- Centro Nacional de Investigaciones Oncologicas (CNIO). Madrid, Spain."
          }

          params = (original_file_name, "GRCh38", "Chromatin State Segmentation", sample_id, "Chromatin State Segmentation by ChromHMM", "BLUEPRINT Epigenome", None, file_str.getvalue(), frm, em, user_key)

          print server.add_experiment(*params)
