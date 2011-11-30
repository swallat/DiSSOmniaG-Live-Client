# -*- coding: utf-8 -*-
'''
Created on 29.11.2011

@author: Sebastian Wallat
'''

import abc
from abc import abstractmethod

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
        
    @abstractmethod
    def clone(self):
        raise NotImplementedError()
    
    @abstractmethod
    def start(self):
        raise NotImplementedError()
    
    @abstractmethod
    def stop(self):
        raise NotImplementedError()
    
    @abstractmethod
    def after_interrupt(self):
        raise NotImplementedError()
    
    @abstractmethod
    def compile(self):
        raise NotImplementedError()
    
    @abstractmethod
    def refreshGit(self):
        raise NotImplementedError()
    
    @abstractmethod
    def refreshAndReset(self):
        raise NotImplementedError()
    
    @abstractmethod
    def reset(self):
        raise NotImplementedError()
    
class AbstractRuntime_AppState(AbstractAppState, metaclass=abc.ABCMeta):
    
    @abstractmethod
    def setRunningScript(self, scriptName):
        self.scriptName = scriptName
        