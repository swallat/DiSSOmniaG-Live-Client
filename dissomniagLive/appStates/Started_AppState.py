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
    
    def sourceEnviron(self, actor):
        log = self.app.getLogger()
        environFile = os.path.join(self.app._getTargetPath(), "operate/environ")
        
        if os.path.isfile(environFile):
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
    
    def _gatherResults(self, actor):
        log = self.app.getLogger()
        resultFolder = self.app._getResultsDirectory()
        
        for dirname, dirnames, filenames in os.walk(resultFolder):
            for filename in filenames:
                fileToAdd = os.path.abspath(os.path.join(dirname, filename))
                
                cmd = shlex.split("git add %s" % fileToAdd)
                self.multiLog("git add %s" % fileToAdd, log.info)
                try:
                    self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    output = self.app.proc.communicate()
                    self.multiLog(str(output), log.info)
                except Exception as e:
                    pass
                
                if self.app.isInterrupted:
                    self.multiLog("gather results was interrupted ", log.error)
                    self.app._selectState(dissomniagLive.app.AppState.COMPILED)
                    return False
                
                if self.app.proc.returncode != 0:
                    self.multiLog("git add failure. git add %s" % fileToAdd, log.error)
        
        try:
            cmd = shlex.split("git commit -a -m \"Results added\"")
            self.multiLog("git commit -a -m  \"Results added\"" , log.info)
            proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            
            output = proc.communicate()
            self.multiLog(str(output), log.info)
            
            if proc.returncode != 0 and proc.returncode != 1: # 1 == Nothing to commit
                self.multiLog("git commit failure. Output: %s" % str(output), log.error)
                self.app._selectState(dissomniagLive.app.AppState.COMPILED) # State COMPILED
                self.app.state.reset(actor) # State CLONED
                if self.app.state._resetGitHard(actor):
                    return self.app.state.compile(actor)
                else:
                    return False
            if proc.returncode != 1:
                cmd = shlex.split("git push")
                self.multiLog("git push", log.info)
                
                proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                
                output = proc.communicate()
                self.multiLog(str(output), log.info)
                
                if proc.returncode != 0:
                    self.multiLog("git push failure. Output: %s" % str(output), log.error)
                    self.app._selectState(dissomniagLive.app.AppState.COMPILED) # State COMPILED
                    self.app.state.reset(actor) # State CLONED
                    if self.app.state._resetGitHard(actor): # In CLONED
                        return self.app.state.compile(actor)
                    else:
                        return False
                self.app._setIgnoreRefresh(set = True)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.multiLog("gatherResults EXCEPTION. %s" % str(e), log.error)
            self.app._selectState(dissomniagLive.app.AppState.COMPILED) # State COMPILED
            self.app.state.reset(actor) # State CLONED
            if self.app.state._resetGitHard(actor):
                return self.app.state.compile(actor)
            else:
                return False
        
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
            self.app._selectState(dissomniagLive.app.AppState.RUNTIME_ERROR)
            self.app.state.setRunningScript(scriptName)
            return False
        
        cmd = file
        try:
            self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        except OSError as e:
            self.multiLog("Script %s is not executable or is not a script file. %s" % (file,str(e)))
            self.app._selectState(dissomniagLive.app.AppState.RUNTIME_ERROR)
            self.app.state.setRunningScript(scriptName)
            return False
        
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
        self._gatherResults(actor)
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
        self._gatherResults(actor)
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
        return self.app.state.refreshGit(actor, tagOrCommit)
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        self.stop(actor)
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        if self.app.refreshGit(actor, tagOrCommit):
            if hasattr(self, "scriptName"):
                return self.app.state.start(actor, self.scriptName)
            else:
                return self.app.state.compile(actor)
        else:
            return False
    
    def reset(self, actor):
        return self.stop(actor)
    
    def clean(self, actor):
        self.stop(actor)
        return self.app.state.clean(actor)