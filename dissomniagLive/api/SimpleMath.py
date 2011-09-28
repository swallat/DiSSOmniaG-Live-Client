# -*- coding: utf-8 -*-
"""
Created on 19.07.2011

@author: Sebastian Wallat
"""
import dissomniagLive
import logging
log = logging.getLogger("api.SimpleMath.py")
    
def add(a, b):
    log.info("Got add Request a: %d, b: %d" % (a, b))
    return a + b

def sub(a, b):
    log.info("Got sub Request a: %d, b: %d" % (a, b))
    return a - b

def mult(a, b):
    log.info("Got mult Request a: %d, b: %d" % (a, b))
    return a * b

def div(a, b):
    log.info("Got div Request a: %d, b: %d" % (a, b))
    return a // b
