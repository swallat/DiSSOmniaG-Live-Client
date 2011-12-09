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
        return self.app.state.clone(actor)
    
    def start(self, actor, scriptName):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.state.start(actor, scriptName)
    
    def stop(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.state.ststop(actor)
    
    def after_interrupt(self, actor):
        return True
    
    def compile(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.state.compile(actor)
    
    def refreshGit(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.state.refreshGit(actor, tagOrCommit)
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.state.refreshAndReset(actor, tagOrCommit)
    
    def reset(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return True
    
    def clean(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.COMPILED)
        return self.app.state.clean(actor)