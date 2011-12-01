# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""

import os
import pwd
import grp

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

group = user

uid = pwd.getpwnam(user).pw_uid

gid = grp.getgrnam(group).gr_gid

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


