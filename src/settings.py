import platform
import sys
import os.path
import logging

"""
Config Variables
"""

if platform.system() == "Darwin":
	OS = "macosx"
else:
	OS = "linux"

EPIDB_INIT_USER = ("Epidb System", "deepblue@mpi-inf.mpg.de", "MPI-Inf")
EPIDB_POPULATOR_USER = ("Populator", "deepblue-populator@mpi-inf.mpg.de", "MPI-Inf")
EPIDB_AUTHKEY_FILE = ".populator.epidb"

LOG_LEVEL = logging.DEBUG

MDB_HOST = "localhost"
MDB_PORT = 27027

DEEPBLUE_HOST = "localhost"
DEEPBLUE_PORT = 56573

VOCAB_URL = "ftp://hgdownload.cse.ucsc.edu/apache/cgi-bin/encode/cv.ra"

# TODO: Remove absolute path
ROOT = "/local/data/DeepBlue-Populator/src"
#ROOT = "/opt/mongodb/epidb/src/epidb/populator"
DOWNLOAD_PATH = os.path.join(ROOT, "download/")
DATA_DIR = os.path.join(ROOT, "../data/")


"""
Threads
"""
max_downloads = 32
max_threads = 32
