# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""
import dissomniagLive

class LOGIN_SIGN(object):
    VALID_USER = 0
    NO_SUCH_USER = 1
    SECRET_UNVALID = 2
    UNVALID_ACCESS_METHOD = 3

class LiveIdentity(object):
    """
    classdocs
    """
    uuid = None
    adminPW = None
    isStarted = False
    
    def __new__(cls, *args, **kwargs):
        # Store instance on cls._instance_dict with cls hash
        key = str(hash(cls))
        if not hasattr(cls, '_instance_dict'):
            cls._instance_dict = {}
        if key not in cls._instance_dict:
            cls._instance_dict[key] = \
                super(LiveIdentity, cls).__new__(cls, *args, **kwargs)
        return cls._instance_dict[key]

    def __init__(self):
        if not '_ready' in dir(self):
            # Der Konstruktor wird bei jeder Instanziierung aufgerufen.
            # Einmalige Dinge wie zum Beispiel die Initialisierung von Klassenvariablen müssen also in diesen Block.
            self._ready = True
            
            self._prepare()
        
    def getIdentity(self):
        pass
        
    def _prepare(self):
        pass
    
    def _mountCdImage(self):
        pass
    
    def _renameInterfaces(self):
        pass
    
    def _parseUUID(self):
        pass
    
    def getUUID(self):
        pass
    
    def _parseAdminPW(self):
        pass
    
    def _copySSHKeys(self):
        pass
    
    def _addInitialUserKeys(self):
        pass
    
    def _generateSSLCertificates(self):
        pass
    
    def authRPCUser(self, username, password):
        if username != "admin":
            return LOGIN_SIGN.NO_SUCH_USER, None
        if password != "test":
            return LOGIN_SIGN.SECRET_UNVALID, None
        if username == "admin" and password == "test":
            return LOGIN_SIGN.VALID_USER, None
        else:
            return LOGIN_SIGN.UNVALID_ACCESS_METHOD, None
        
    def start(self):
        if self.isStarted:
            raise RuntimeError("Restart is not allowed!")
        else:
            self.isStarted = True
            dissomniagLive.server.startRPCServer()
            
