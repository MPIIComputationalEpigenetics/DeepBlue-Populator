import settings
from log import log
from client_v2 import EpidbClient

_key = ""
def get_key():
    """
    loads a previously obtained authentication key for
    epidb from the key file, defined in the settings.
    """
    if not _key:
        with open(settings.EPIDB_AUTHKEY_FILE, 'r') as f:
            for l in f.readlines():
                (user, email, inst, key) = l.split(':')
                if (user, email, inst) == (settings.EPIDB_POPULATOR_USER[0],
                                           settings.EPIDB_POPULATOR_USER[1],
                                           settings.EPIDB_POPULATOR_USER[2]):
                    return key

    log.info("Authentication key loaded")

class PopulatorEpidbClient(EpidbClient):
    def __init__(self):
        super(PopulatorEpidbClient, self).__init__(get_key(),
                                                   settings.DEEPBLUE_HOST,
                                                   settings.DEEPBLUE_PORT)