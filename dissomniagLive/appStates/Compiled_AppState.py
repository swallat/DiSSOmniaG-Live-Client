'''
Created on 30.11.2011

@author: Sebastian Wallat
'''
import os
import subprocess
import shlex
import dissomniagLive
from dissomniagLive.appStates import *

class Compiled_AppState(AbstractAppState):
    '''
    classdocs
    '''
    
    def sourceEnviron(self, actor):
        log = self.app.getLogger()
        environFile = os.path.join(self.app._getTargetPath(), "operate/environ")
        
        if os.path.isFile(environFile):
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

    def clone(self, actor):
        return True
    
    def start(self, actor, scriptName):
        self.app._selectState(dissomniagLive.app.AppState.STARTED)
        return self.app.state.start(actor, scriptName)                
    
    def stop(self, actor):
        return True
    
    def after_interrupt(self, actor):
        return True
    
    def compile(self, actor):
        return True
    
    def refreshGit(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.state.refreshGit(actor, tagOrCommit)
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        if self.app.state.refreshGit(actor, tagOrCommit):
            return self.app.state.compile(actor)
        else:
            return False
    
    def reset(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return True
        