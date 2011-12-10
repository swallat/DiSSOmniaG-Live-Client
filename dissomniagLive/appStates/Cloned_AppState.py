'''
Created on 30.11.2011

@author: Sebastian Wallat
'''
import shutil, subprocess, shlex
import re
import os
import dissomniagLive
from dissomniagLive.appStates import *

class Cloned_AppState(AbstractAppState):
    '''
    classdocs
    '''
    
    def clone(self, actor):
        log = self.app.getLogger()
        self.multiLog("Try to refreshGit instead of clone.", log.info)
        return self.refreshGit(actor)
                    
    def start(self, actor, scriptName):
        if self.compile(actor):
            return self.app.state.start(actor, scriptName)
    
    def stop(self, actor):
        return self.compile(actor)
    
    def after_interrupt(self, actor):
        log = self.app.getLogger()
        self.multiLog("Recreate git for sanity reasons!")
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        self.app.state.after_interrupt(actor)
        return self.app.state.clone()
    
    def compile(self, actor):
        log = self.app.getLogger()
        fileA = os.path.join(self.app._getOperateDirectory(), "compile")
        fileB = os.path.join(self.app._getOperateDirectory(), "compile.sh")
        file = None
        if os.path.isfile(fileA):
            file = fileA
        elif os.path.isfile(fileB) and file == None:
            file = fileB
        else:
            self.multiLog("Skipped compile.", log.info)
            self.app._selectState(dissomniagLive.app.AppState.COMPILED)
            return True
        
        try:
            os.chmod(file, 0o777)
        except OSError:
            pass
        self.sourceEnviron(actor)
        cmd = shlex.split(os.path.abspath(file))
        log.error("POINT %s" % cmd)
        try:
            self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.STDOUT, preexec_fn = os.setsid)
        except OSError:
            self.multiLog("The file %s is not an excecutable shell file. Skip compile." % file)
            self.app._selectState(dissomniagLive.app.AppState.COMPILED)
            return True
        
        output = self.app.proc.communicate()
        self.muliLog(str(output))
        
        if self.app.isInterrupted:
            self.multiLog("Compile was inerrupted.", log.error)
            return self.after_interrupt(actor)
        
        if self.app.proc.returncode != 0:
            self.multiLog("Compile failed!", log.error)
            self.app._selectState(dissomniagLive.app.AppState.COMPILE_ERROR)
            return False
        self.app._selectState(dissomniagLive.app.AppState.COMPILED)
        return True
                
    def _resetGitHard(self, actor):
        log = self.app.getLogger()
        cmd = shlex.split("git reset --hard")
        self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.STDOUT, preexec_fn = os.setsid)
        
        output = self.app.proc.communicate()
        self.multiLog(str(output))
        
        if self.app.isInterrupted or self.app.proc.returncode != 0:
            self.multiLog("Git reset --hard interrupted or not possible.", log.info)
            self.reset(actor) # INIT State
            return self.app.state.clone(actor)
        else:
            return True
        
    
    def refreshGit(self, actor, tagOrCommit = None):
        log = self.app.getLogger()
        
        cmd = shlex.split("git pull")
        
        self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.STDOUT, preexec_fn = os.setsid)
        
        output = self.app.proc.communicate()
        self.multiLog(str(output))
        
        if self.app.isInterrupted:
            self.multiLog("Git pull interrupted.", log.info)
            return self.after_interrupt(actor)
        
        if self.app.proc.returncode != 0:
            self.multiLog("Could not git pull.", log.error)
            self._resetGitHard(actor)
            self.app._selectState(dissomniagLive.app.AppState.PULL_ERROR)
            return False
        
        if tagOrCommit != None:
            cmd = shlex.split("git checkout %s", tagOrCommit)
            self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.STDOUT, preexec_fn = os.setsid)
            
            output = self.app.proc.communicate()
            self.multiLog(str(output[0]))
            
            if self.app.isInterrupted:
                self.multiLog("Git checkout %s interrupted." % tagOrCommit, log.error)
                return self.after_interrupt(actor)
            
            if self.app.proc.returncode != 0:
                self.multiLog("Git checkout %s failed." % tagOrCommit, log.error)
                self._resetGitHard(actor)
        
        return True
            
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        return self.refreshGit(actor, tagOrCommit)
    
    def reset(self, actor):
        log = self.app.getLoger()
        self.multiLog("Reset from CLONED TO INIT.", log.info)
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return self.app.state.after_interrupt(actor)
    
    def clean(self, actor):
        return True
        