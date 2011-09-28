import config
from identity import *
import server
import api
import logging, logger

log = logging.getLogger("__init__")

def getIdentity():
    return LiveIdentity()

def run():
    getIdentity().start()
