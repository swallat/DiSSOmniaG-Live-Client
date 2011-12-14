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
import dissomniagLive
from dissomniagLive.appStates import *

class CloneError_AppState(AbstractAppState):
    '''
    classdocs
    '''

    def clone(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return self.app.state.clone(actor)
    
    def start(self, actor, scriptName):
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return self.app.state.start(actor, scriptName)
    
    def stop(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return self.app.state.stop(actor)
    
    def after_interrupt(self, actor):
        return True
    
    def compile(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return self.app.state.compile(actor)
    
    def refreshGit(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return self.app.state.refreshGit(actor, tagOrCommit)
    
    def refreshAndReset(self, actor, tagOrCommit = None):
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return self.app.state.refreshAndReset(actor, tagOrCommit)
    
    def reset(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return True
    
    def clean(self, actor):
        self.app._selectState(dissomniagLive.app.AppState.INIT)
        return self.app.state.clean(actor)