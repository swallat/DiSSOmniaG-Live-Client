# -*- coding: utf-8 -*-
'''
Created on 11.11.2011

@author: Sebastian Wallat
'''

import dissomniagLive
import logging
log = logging.getLogger("api.Update.py")

def update(self, infoXml):
    
    return dissomniagLive.getIdentity().getXMLStatusAnswer()