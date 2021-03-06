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
import os
import subprocess
import shlex
import dissomniagLive
from dissomniagLive.appStates import *

class Compiled_AppState(AbstractAppState):
    '''
    classdocs
    '''

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
        self.app.state.refreshGit(actor, tagOrCommit)
        return self.app.state.compile(actor)
    
    def clean(self, actor):
        log = self.app.getLogger()
        self.multiLog("Starting Script %s.", log.info)
        
        self.sourceEnviron(actor)
        scriptName = "clean"
        fileA = os.path.join(self.app._getOperateDirectory(), scriptName)
        fileB = os.path.join(self.app._getOperateDirectory(), "%.sh" % scriptName)
        file = None
        if os.path.isfile(fileA):
            file = fileA
        elif os.path.isfile(fileB) and file == None:
            file = fileB
        else:
            self.multiLog("Couldn't start script %s. File not found." % scriptName, log.error)
            self.app._selectState(dissomniagLive.app.AppState.CLONED)
            return True
        
        cmd = file
        try:
            self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath(), stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn = os.setsid)
        except OSError as e:
            self.multiLog("Script %s is not executable or is not a script file. %s" % (file,str(e)))
            self.app._selectState(dissomniagLive.app.AppState.CLONED)
            return True
        
        output = self.app.proc.communicate()
        self.multiLog(str(output), log.info)
        
        if self.app.isInterrupted:
            self.app._selectState(dissomniagLive.app.AppState.CLONED)
            return False
        
        if self.app.proc.returncode != 0:
            self.multiLog("Script executed with failures!", log.error)
            self.app._selectState(dissomniagLive.app.AppState.CLONED)
            return False
        
        self.multiLog("CLEAN finished execution.", log.info)
        self.app._selectState(dissomniagLive.app.AppState.CLONED)
        return True
    
    def reset(self, actor):
        return self.clean(actor)
        