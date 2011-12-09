# -*- coding: utf-8 -*-
'''
Created on 29.11.2011

@author: Sebastian Wallat
'''

import abc
from abc import abstractmethod
import os, re

import dissomniagLive

class AbstractAppState(metaclass=abc.ABCMeta):
    '''
    classdocs
    '''

    def __init__(self, app):
        '''
        Constructor
        '''
        
        self.app = app
        
    def multiLog(self, msg, loggerFunction = None):
        if loggerFunction != None:
            loggerFunction(msg)
            
        self.app._appendRemoteLog(msg)
        
    @abstractmethod
    def clone(self, actor):
        raise NotImplementedError()
    
    @abstractmethod
    def clean(self, actor):
        raise NotImplementedError()
    
    @abstractmethod
    def start(self, actor, scriptName):
        raise NotImplementedError()
    
    @abstractmethod
    def stop(self, actor):
        raise NotImplementedError()
    
    @abstractmethod
    def after_interrupt(self, actor):
        raise NotImplementedError()
    
    @abstractmethod
    def compile(self, actor):
        raise NotImplementedError()
    
    @abstractmethod
    def refreshGit(self, actor, tagOrCommit = None):
        raise NotImplementedError()
    
    @abstractmethod
    def refreshAndReset(self, actor, tagOrCommit = None):
        raise NotImplementedError()
    
    @abstractmethod
    def reset(self, actor):
        raise NotImplementedError()
    
    def sourceEnviron(self, actor):
        log = self.app.getLogger()
        environFile = os.path.join(self.app._getTargetPath(), "operate/environ")
        
        if os.path.isfile(environFile):
            lines = []
            with open(environFile) as f:
                f = lines.readlines()
            prog = re.compile("^(.*)=(.*)$")   
            for line in lines:
                for result in prog.finditer(line):
                    key = result.groups()[0].strip()
                    value = result.groups()[1].strip()
                    os.environ[key] = value
                    self.multiLog("Added Environ parameter. Key: %s, Value: %s" % (key, value), log.info)
        return True

    
class AbstractRuntime_AppState(AbstractAppState, metaclass=abc.ABCMeta):
    
    def setRunningScript(self, scriptName):
        self.scriptName = scriptName
        