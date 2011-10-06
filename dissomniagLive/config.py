# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""

import os

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

rpcServerPort = 8008

SSL = True

#Generate with: openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem
sslPrivateKey = "/etc/ssl/private/ssl-cert-snakeoil.key"
sslCertFile = "/etc/ssl/certs/ssl-cert-snakeoil.pem"

