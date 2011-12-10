'''
Created on 30.11.2011

@author: Sebastian Wallat
'''
import os, shutil
import subprocess
import dissomniagLive
from dissomniagLive.appStates import *

class Init_AppState(AbstractAppState):
    '''
    classdocs
    '''
        
    def clone(self, actor): 
        log = self.app.getLogger()
        
        self.multiLog("Try to clone from %s to %s" % (self.app._getServerConnector(), self.app._getTargetPath()), log.info)
        cmd = shlex.split("git clone %s %s -b %s" % (self.app._getServerConnector(), self.app._getTargetPath(), self.app.branchName))
        self.app.proc = subprocess.Popen(cmd, cwd = dissomniagLive.config.appBaseFolder, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, preexec_fn = os.setsid)
        
        output = self.app.proc.communicate()
        self.multiLog(str(output))
        
        
        if self.app.isInterrupted:
            self.multiLog("Clone Interrupted!", log.error)
            return self.after_interrupt(self)
        
        if self.app.proc.returncode != 0:
            self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
            self.multiLog("Could not clone repository! returncode: %s, output: %s" % (str(self.app.proc.returncode), str(output)), log.error)
            return False
        
        try:
            os.chdir(os.path.join(dissomniagLive.config.appBaseFolder, self.app._getTargetPath()))
        except OSError:
            self.multiLog("Cannot chdir to App Directory!", log.error)
            self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
            return False
        
        if not os.path.exists(os.path.join(self.app._getTargetPath(), "log")):
            try:
                os.makedirs(os.path.join(self.app._getTargetPath(), "log"), 0o755)
                os.chown(os.path.join(self.app._getTargetPath(), "log"), 1000, 1000)
            except OSError:
                self.multiLog("Cannot create app log folder", log.error)
                self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
                return False
        
        if not os.path.exists(os.path.join(self.app._getTargetPath(), "operate")):
            try:
                os.makedirs(os.path.join(self.app._getTargetPath(), "operate"), 0o755)
                os.chown(os.path.join(self.app._getTargetPath(), "operate"), 1000, 1000)
            except OSError:
                self.multiLog("Cannot create app operate folder", log.error)
                self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
                return False
            
        if not os.path.exists(os.path.join(self.app._getTargetPath(), "results")):
            try:
                os.makedirs(os.path.join(self.app._getTargetPath(), "results"), 0o755)
                os.chown(os.path.join(self.app._getTargetPath(), "results"), 1000, 1000)
            except OSError:
                self.multiLog("Cannot create app results folder", log.error)
                self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
                return False
            
        self.multiLog("App cloned!", log.info)
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        if hasattr(self.app.state, "sourceEnviron"):
            self.app.state.sourceEnviron(actor)
        return True
        
    
    def start(self,actor, scriptName):
        if self.clone(actor):
            return self.app.state.start(actor, scriptName)
        else:
            return False
    
    def stop(self, actor):
        if self.clone(actor):
            return self.app.state.stop(actor)
        else:
            return False
    
    def after_interrupt(self, actor):
        log = self.app.getLogger()
        if os.path.exists(self.app._getTargetPath()):
            try:
                shutil.rmtree(self.app._getTargetPath())
            except OSError:
                self.multiLog("Cannot delete App folder.", log.error)
                return False
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return True
    
    def compile(self, actor):
        if self.clone(actor):
            return self.app.state.compile(actor)
        else:
            return False
    
    def refreshGit(self, actor, tagOrCommit = None):
        if self.clone(actor):
            return self.app.state.refreshGit(actor, tagOrCommit)
        else:
            return False
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        return True
    
    def reset(self, actor):
        return True
    
    def clean(self, actor):
        return True
        