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
import pwd

try:
    isDebug = (True if (os.environ['DEBUG'] in ("True", "1")) else False)
except KeyError:
    isDebug = False
    
execDir = (os.getcwd() if isDebug else "/usr/share/omnet/")

logDir = (os.path.join(os.getcwd(), "log") if isDebug else "/var/log/")

confDir = (os.getcwd() if isDebug else "/etc/omnet/")

debugFilename = os.path.join(logDir, "dissomniag_DEBUG")

warningFilename = os.path.join(logDir, "dissomniag_WARNING")

logToStdOut = True

localRpcServerPort = 8008

remoteRpcServerPort = 8008

user = "user"

uid = pwd.getpwnam(user).pw_uid

gid = pwd.getpwnam(user).pw_gid

rootPrivKey = "/root/.ssh/id_rsa"
rootPubKey = "/root/.ssh/id_rsa.pub"
userPrivKey = "/home/user/.ssh/id_rsa"
userPubKey = "/home/user/.ssh/id_rsa.pub"

def getRoot():
    os.seteuid(0)
    os.setegid(0)
    
def getUserPerm():
    os.setegid(gid)
    os.seteuid(uid)
    

SSL = True

pidFile = "/var/run/dissomniag_live.pid"

#Generate with: openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem
sslPrivateKey = "/etc/ssl/private/ssl-cert-snakeoil.key"
sslCertFile = "/etc/ssl/certs/ssl-cert-snakeoil.pem"

appBaseFolder = "/home/user/apps/"
appLogFolder = os.path.join(appBaseFolder, "logs")

operateSubdirIdentifier = "operate"
resultsSubdirIdentifier = "results"

