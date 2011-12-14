# -*- coding: utf-8 -*-
# DiSSOmniaG (Distributed Simulation Service wit OMNeT++ and Git)
# Copyright (C) 2011, 2012 Sebastian Wallat, University Duisburg-Essen
# 
# Based on an idea of:
# Sebastian Wallat <sebastian.wallat@uni-due.de, University Duisburg-Essen
# Hakim Adhari <hakim.adhari@iem.uni-due.de>, University Duisburg-Essen
# Martin Becke <martin.becke@iem.uni-due.de>, University Duisburg-Essen
#
# DiSSOmniaG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DiSSOmniaG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DiSSOmniaG. If not, see <http://www.gnu.org/licenses/>
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
        # Add APP_HOME Path
        os.environ["APP_HOME"] = self.app._getTargetPath()
        
        if os.path.isfile(environFile):
            lines = []
            with open(environFile) as f:
                lines = f.readlines()
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
        