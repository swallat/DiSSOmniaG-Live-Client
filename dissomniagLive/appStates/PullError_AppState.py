'''
Created on 30.11.2011

@author: Sebastian Wallat
'''
import dissomniagLive
from dissomniagLive.appStates import *

class PullError_AppState(AbstractAppState):
    '''
    classdocs
    '''

    def clone(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        self.app.state._resetGitHard(actor)
        return self.app.state.clone(actor)
    
    def start(self, actor, scriptName):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        self.app.state._resetGitHard(actor)
        if self.app.state.refreshGit(actor):
            return self.app.state.start(actor, scriptName)
        else:
            return False
    
    def stop(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        self.app.state._resetGitHard(actor)
        if self.app.state.refreshGit(actor):
            return self.app.state.stop(actor)
        else:
            return False
    
    def after_interrupt(self, actor):
        return True
    
    def compile(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        self.app.state._resetGitHard(actor)
        if self.app.state.refreshGit(actor):
            return self.app.state.compile(actor)
        else:
            return False
    
    def refreshGit(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        self.app.state._resetGitHard(actor)
        return self.app.state.refreshGit(actor, tagOrCommit)
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        self.app.state._resetGitHard(actor)
        return self.app.state.refreshAndReset(actor, tagOrCommit)
    
    def reset(self, actor):
        return self.refreshGit(actor)
    
    def clean(self, actor):
        return True