# -*- coding: utf-8 -*-
'''
Created on 11.11.2011

@author: Sebastian Wallat
'''
from xml.etree import ElementTree#
import dissomniagLive
import logging
log = logging.getLogger("api.Update.py")

def update(self, infoXml):
    xml = ElementTree.fromstring(infoXml)
    self.dissomniagLive.getIdentity().fetchConfig(xml, update = True)
    
    return dissomniagLive.getIdentity().getXMLStatusAnswer()