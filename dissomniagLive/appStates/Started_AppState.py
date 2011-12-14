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
import subprocess
import signal
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
    
    def _gatherResults(self, actor):
        log = self.app.getLogger()
        resultFolder = self.app._getResultsDirectory()
        
        for dirname, dirnames, filenames in os.walk(resultFolder):
            for filename in filenames:
                fileToAdd = os.path.abspath(os.path.join(dirname, filename))
                
                cmd = shlex.split("git add %s" % fileToAdd)
                self.multiLog("git add %s" % fileToAdd, log.info)
                try:
                    self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn = os.setsid)
                    output = self.app.proc.communicate()
                    self.multiLog(str(output), log.info)
                except Exception as e:
                    pass
                
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
                
                proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn = os.setsid)
                
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
                self.app._setIgnoreRefresh(mSet = True)
                
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
        self.multiLog("Gather results exists normally.", log.info)
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
            self.multiLog("Starting app with script %s." % str(file), log.info)
            self.app._sendInfo()
            self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn = os.setsid)
            output = self.app.proc.communicate()
            self.multiLog(str(output), log.info)
        except OSError as e:
            self.multiLog("Script %s is not executable or is not a script file. %s" % (file,str(e)))
            self.app._selectState(dissomniagLive.app.AppState.RUNTIME_ERROR)
            self.app.state.setRunningScript(scriptName)
            return False
        
        if self.app.isInterrupted:
            self.multiLog("script execution was interrupted %s ." % scriptName, log.error)
        
        if self.app.proc.returncode != 0 and not self.app.isInterrupted:
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
                os.killpg(self.app.proc.pid, signal.SIGTERM)
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