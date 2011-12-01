'''
Created on 30.11.2011

@author: Sebastian Wallat
'''
import subprocess
import shlex
import os
import dissomniagLive
from dissomniagLive.appStates import *

class Started_AppState(AbstractRuntime_AppState):
    '''
    classdocs
    '''

    def clone(self, actor):
        return True
    
    def start(self, actor, scriptName):
        log = self.app.getLogger()
        self.multiLog("Starting Script %s.", log.info)
        self.setRunningScript(scriptName)
        
        self.sourceEnviron(actor)
        
        fileA = os.path.join(self.app._getOperateDirectory(), scriptName)
        fileB = os.path.join(self.app._getOperateDirectory(), "%.sh" % scriptName)
        file = None
        if os.path.isfile(fileA):
            file = fileA
        elif os.path.isfile(fileB) and file == None:
            file = fileB
        else:
            self.multiLog("Couldn't start script %s. File not found." % scriptName, log.error)
            return False
        
        cmd = file
        self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        
        output = self.app.proc.communicate()
        self.multiLog(str(output), log.info)
        
        if self.app.isInterrupted:
            self.multiLog("script execution was interrupted %s ." % scriptName, log.error)
            return self.afterInterrupt(actor)
        
        if self.app.proc.returncode != 0:
            self.multiLog("Script executed with failures!", log.error)
            self.app._selectState(dissomniagLive.app.AppState.RUNTIME_ERROR)
            self.app.state.setRunningScript(scriptName)
            return False
        self.multiLog("Script finished execution.", log.info)
        self.app._selectState(dissomniagLive.app.AppState.COMPILED)
        return True
    
    def stop(self, actor):
        log = self.app.getLogger()
        self.multiLog("Stop Running app.")
        
        if self.app.proc != None and isinstance(self.app.proc, subprocess.Popen):
            try:
                self.app.proc.kill()
            except Exception as e:
                self.multiLog("Stop throwed exception %s." % str(e), log.error)
        
        self.app._selectState(dissomniagLive.app.AppState.COMPILED)
        return True
    
    def after_interrupt(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.COMPILED)
        return True
    
    def compile(self, actor):
        return True
    
    def refreshGit(self, actor, tagOrCommit = None):
        self.stop(actor)
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return self.app.refreshGit(actor, tagOrCommit)
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        self.stop(actor)
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        if self.app.refreshGit(actor, tagOrCommit):
            return self.app.start(actor, self.scriptName)
        else:
            return False
    
    def reset(self, actor):
        return self.stop(actor)  