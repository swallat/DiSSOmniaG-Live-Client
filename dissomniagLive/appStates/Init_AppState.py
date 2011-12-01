'''
Created on 30.11.2011

@author: Sebastian Wallat
'''
import os, shutil
impor subproccess
import dissomniagLive
from dissomniagLive.appStates import *

class Init_AppState(AbstractAppState):
    '''
    classdocs
    '''
        
    def clone(self):
        os.environ[] = 
        log = self.app.getLogger()
        self.multiLog("Try to clone from %s to %s" % (self.app._getServerConnector(), self.app._getTargetPath()), log.info)
        cmd = shutil.shlex("git clone %s %s -b %s" % (self.app._getServerConnector(), self.app._getTargetPath()), self.app.branchName)
        self.app.proc = subprocess.Popen(cmd, cwd = dissomniagLive.config.appBaseFolder, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        self.app.proc.write = "yes\n"
        
        stdout, stderr = self.app.proc.communicate()
        
        if self.app.isInterrupted:
            self.multiLog("Clone Interrupted!", log.error)
            return self.after_interrupt(self)
        
        if self.app.proc.returncode != 0:
            self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
            self.multiLog("Could not clone repository!", log.error)
            return False
        
        try:
            os.chdir(os.path.join(dissomniagLive.config.appBaseFolder, self.app._getTargetPath()))
        except OSError:
            self.multiLog("Cannot chdir to App Directory!", log.error)
            self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
            return False
        
        if not os.path.exists(os.path.join(self.app._getTargetPath, "log")):
            try:
                os.makedirs(os.path.join(self.app._getTargetPath, "log"), 0o755)
                os.chown(os.path.join(self.app._getTargetPath, "log"), 1000, 1000)
            except OSError:
                self.multiLog("Cannot create app log folder", log.error)
                self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
                return False
        
        if not os.path.exists(os.path.join(self.app._getTargetPath, "operate")):
            try:
                os.makedirs(os.path.join(self.app._getTargetPath, "operate"), 0o755)
                os.chown(os.path.join(self.app._getTargetPath, "operate"), 1000, 1000)
            except OSError:
                self.multiLog("Cannot create app operate folder", log.error)
                self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
                return False
            
        if not os.path.exists(os.path.join(self.app._getTargetPath, "results")):
            try:
                os.makedirs(os.path.join(self.app._getTargetPath, "results"), 0o755)
                os.chown(os.path.join(self.app._getTargetPath, "results"), 1000, 1000)
            except OSError:
                self.multiLog("Cannot create app results folder", log.error)
                self.app._selectState(dissomniagLive.app.AppState.CLONE_ERROR)
                return False
            
        self.app._addGitLog(self.app._getTargetPath())
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        if hasattr(self.app.state, "sourceEnviron") and callable(self.app.state, "sourceEnviron"):
            self.app.state.sourceEnviron(actor)
        return True
        
    
    def start(self,actor):
        raise NotImplementedError()
    
    def stop(self, actor):
        raise NotImplementedError()
    
    def after_interrupt(self, actor):
        log = self.app.getLogger()
        if os.path.exists(self.app._getTargetPath):
            try:
                shutil.rmtree(self.app._getTargetPath())
            except OSError:
                self.multiLog("Cannot delete App folder.", log.error)
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return True
    
    def compile(self, actor):
        raise NotImplementedError()
    
    def refreshGit(self, actor):
        raise NotImplementedError()
    
    def refreshAndReset(self, actor):
        raise NotImplementedError()
    
    def reset(self, actor):
        raise NotImplementedError()
        