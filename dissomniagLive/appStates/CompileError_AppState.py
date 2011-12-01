'''
Created on 30.11.2011

@author: Sebastian Wallat
'''
import dissomniagLive
from dissomniagLive.appStates import *

class CompileError_AppState(AbstractAppState):
    '''
    classdocs
    '''

    def clone(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.clone(actor)
    
    def start(self, actor, scriptName):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.start(actor, scriptName)
    
    def stop(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.stop(actor)
    
    def after_interrupt(self, actor):
        return True
    
    def compile(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.compile(actor)
    
    def refreshGit(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.refreshGit(actor, tagOrCommit)
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.refreshAndReset(actor, tagOrCommit)
    
    def reset(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return True  