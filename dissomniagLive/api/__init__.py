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
class ApiProvider(object):
    
    def update(self, infoXml):
        from . import Update
        return Update.update(infoXml)
    
    def addApps(self, appXml):
        from . import apps
        return apps.addApps(appXml)
    
    def appOperate(self, appXml):
        from . import apps
        return apps.appOperate(appXml)
    
    def getAppInfo(self, appName):
        from . import apps
        return apps.getAppInfo(appName)
    
    def add(self, a, b):
        return a+b
    
    def wait(self):
        print("Enter waiting")
        import time
        time.sleep(60)
        print("Leaving wait")
        return True


