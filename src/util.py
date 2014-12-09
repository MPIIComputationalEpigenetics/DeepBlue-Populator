import urllib
import os.path


def has_error(status, msg, errors):
    if status == "okay":
        return False
    ss = msg.split(":")[0]
    for e in errors:
        if ss == e:
            return False
    return True


"""
removes a certian set of special characters from the string.
"""


def clean_string(string):
    new = ""
    for c in string:
        if c not in ['(', ')', '_', '_', '-', '+', '.']:
            new += c

    return new.strip().lower()


"""
removes a certain set of special characters and all parts sourrounded
by parantheses from the string.
"""


def clean_term(string):
    new = ""
    consume = False
    for c in string:
        if c == '(':
            consume = True
        elif c == ')':
            consume = False
        elif not consume and c not in ['(', ')', '_', '_', '-', '+', '.']:
            new += c

    return new.strip().lower()


"""
downloads the file at `url' and stores it in `localFile'.
"""


def download_file(url, localFile):
    if os.path.isfile(localFile):
        raise Exception("Error: File already exists " + localFile)

    # a special opener to simulate firefox queries
    class Opener(urllib.FancyURLopener):
        version = 'Mozilla/5.0'

    myopener = Opener()
    myopener.retrieve(url, localFile)
