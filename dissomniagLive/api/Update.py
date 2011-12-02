# -*- coding: utf-8 -*-
'''
Created on 11.11.2011

@author: Sebastian Wallat
'''
from xml.etree import ElementTree#
import dissomniagLive
import logging
log = logging.getLogger("dissomniagLive.api.Update.py")

def update(infoXml):
    xml = ElementTree.XML(infoXml)
    dissomniagLive.getIdentity().fetchConfig(xml, update = True)
    
    return dissomniagLive.getIdentity().getXMLStatusAnswer()