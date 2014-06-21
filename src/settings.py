import sys
import os.path
import logging

"""
Config Variables
"""

EPIDB_INIT_USER = ("Epidb System", "deepblue@mpi-inf.mpg.de", "MPI-Inf")
EPIDB_POPULATOR_USER = ("Populator", "deepblue-populator@mpi-inf.mpg.de", "MPI-Inf")
EPIDB_AUTHKEY_FILE = ".populator.epidb"

LOG_LEVEL = logging.DEBUG

MDB_HOST = "localhost"
MDB_PORT = 27017

DEEPBLUE_HOST = "localhost"
DEEPBLUE_PORT = 31415

VOCAB_URL = "ftp://hgdownload.cse.ucsc.edu/apache/cgi-bin/encode/cv.ra"

# TODO: Remove absolute path
ROOT = "/Users/albrecht/mpi/DeepBlue-Populator/src"
#ROOT = "/opt/mongodb/epidb/src/epidb/populator"
DOWNLOAD_PATH = os.path.join(ROOT, "download/")
DATA_DIR = os.path.join(ROOT, "../data/")


"""
Threads
"""
max_downloads = 4
max_threads = 8
