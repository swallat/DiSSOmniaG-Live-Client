from . import config
from .identity import *
from . import server
from . import api
from . import logger
from . import commands
from .appStates import *
import logging

log = logging.getLogger("__init__")

def getIdentity():
    return LiveIdentity()

def run():
    getIdentity().start()
