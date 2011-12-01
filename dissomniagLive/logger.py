# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""

import logging, os, sys
import logging.handlers
import time
import glob

import dissomniagLive

def setUpLogger(logger):
    logger.setLevel(logging.DEBUG)
    if not os.path.exists(dissomniagLive.config.logDir):
        os.makedirs(dissomniagLive.config.logDir)
    
    debugFile = dissomniagLive.config.debugFilename
    warningFile = dissomniagLive.config.warningFilename
        
    firstRun = True
    if os.path.isfile(debugFile) or os.path.isfile(warningFile):
        firstRun = False

    debugHandler = logging.handlers.RotatingFileHandler(debugFile,
                                                    mode = 'a',
                                                    maxBytes = 1000000,
                                                    backupCount = 10)
    debugHandler.setLevel(logging.DEBUG)
    
    
    
    warningHandler = logging.handlers.RotatingFileHandler(warningFile,
                                                          mode = 'a',
                                                          maxBytes = 1000000,
                                                          backupCount = 10)
    warningHandler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(threadName)-10s %(levelname)-8s %(message)s")
    debugHandler.setFormatter(formatter)
    warningHandler.setFormatter(formatter)
    logger.addHandler(warningHandler)
    logger.addHandler(debugHandler)
    
    if dissomniagLive.config.logToStdOut:
        stdOutHandler = logging.StreamHandler(stream = sys.stdout)
        stdOutHandler.setFormatter(formatter)
        logger.addHandler(stdOutHandler)
    
    
    if not firstRun:
        # Roll over on application start
        for handler in logger.handlers:
            if not isinstance(handler, logging.handlers.RotatingFileHandler):
                continue
            handler.doRollover()
    
    # Add timestamp
    logger.warning('\n---------\nLog started on %s.\n---------\n' % time.asctime())
    
    return logger

def doLogEnd():
    # Add timestamp
    logger.warning('\n---------\nLog closed on %s.\n---------\n' % time.asctime())
    
    

logger = setUpLogger(logging.getLogger('dissomniagLive'))
