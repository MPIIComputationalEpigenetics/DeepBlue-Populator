import platform
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

ROOT = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_PATH = os.path.join(ROOT, "download/")
DATA_DIR = os.path.join(ROOT, "../data/")

# always check:
# /TL/deep-share/archive00/software/dtdrpc/dtd_srv.info 
=======
DEEP_XMLRPC_SERVER = "http://deep01:50005"

"""
Threads
"""
max_threads = 4
