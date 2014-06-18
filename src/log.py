import logging
import sys

from settings import LOG_LEVEL


"""
Logging configurations
"""

log = logging.Logger("main")

log.addHandler(logging.StreamHandler(sys.stderr))
log.setLevel(LOG_LEVEL)