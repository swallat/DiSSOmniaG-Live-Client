# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""
import os
import logging
import sys
import netifaces
import crypt, string, random
from xml.etree import ElementTree
import dissomniagLive

log = logging.getLogger("dissomniagLive.identity")

class LOGIN_SIGN(object):
    VALID_USER = 0
    NO_SUCH_USER = 1
    SECRET_UNVALID = 2
    UNVALID_ACCESS_METHOD = 3

class LiveIdentity(object):
    """
    classdocs
    """
    uuid = None
    adminPW = None
    serverIp = None
    isStarted = False
    pathToCd = "/media/cdrom/"
    liveInfoFile = os.path.join(pathToCd, "liveInfo.xml")
    
    def __new__(cls, *args, **kwargs):
        # Store instance on cls._instance_dict with cls hash
        key = str(hash(cls))
        if not hasattr(cls, '_instance_dict'):
            cls._instance_dict = {}
        if key not in cls._instance_dict:
            cls._instance_dict[key] = \
                super(LiveIdentity, cls).__new__(cls, *args, **kwargs)
        return cls._instance_dict[key]

    def __init__(self):
        if not '_ready' in dir(self):
            # Der Konstruktor wird bei jeder Instanziierung aufgerufen.
            # Einmalige Dinge wie zum Beispiel die Initialisierung von Klassenvariablen müssen also in diesen Block.
            self._ready = True
            
            self._prepare()
        
    def getIdentity(self):
        pass
        
    def _prepare(self):
        if not self._mountCdImage():
            log.Error("General Error")
            sys.exit(-1)
            
        with open(self.liveInfoFile, 'rt') as f:
            tree = ElementTree.parse(f)
        
        uuid = tree.find("uuid")
        if uuid:
            self.uuid = str(uuid.text)
        
        serverIp = tree.find("serverIp")
        if serverIp:
            self.serverIp = str(serverIp.text)
        
        password = tree.find("password")
        if password:
            self._parseAdminPW(str(password.text))
        
        iterInterfaces = []
        interfaces = tree.findall("interfaces")
        for interface in interfaces:
            name = interface.find("name")
            mac = interface.find("mac")
            if name and mac:
                i = {}
                i["name"] = str(name.text)
                i["mac"] = str(mac.text)
                iterInterfaces.append(iter)
                
        self._renameInterfaces(iterInterfaces)
        self._generateSSLCertificates()
    
    def _mountCdImage(self):
        try:
            os.mkdir(self.pathToCd, mode = '0777')
        except IOError, e:
            log.Error("Could not create Cdrom Directory!")
            return False
        
        cmd = dissomniagLive.commands.StandardCmd("mount /dev/cdrom /media/cdrom", log = log)
        code, output = cmd.run()
        if code != 0:
            log.Error("Could not mount Cd")
            return False
        return True
        
    
    def _renameInterfaces(self, iterInterfaces):
        # Stop gnome-network-manager
        cmd = dissomniagLive.commands.StandardCmd("/etc/init.d/network-manager stop")
        code, output = cmd.run()
        if code != 0:
            pass
        
        # Deactivate all Interfaces
        for interface in self._getLocalInterfaceNames():
            cmd = dissomniagLive.commands.StandardCmd("/sbin/ifconfig %s down" % str(interface), log)
            code, output = cmd.run()
            if code != 0:
                pass
        
        # Stop Networking
        cmd = dissomniagLive.commands.StandardCmd("/etc/init.d/networking stop", log)
        code, output = cmd.run()
        if code != 0:
            pass
        
        # Add udev rules
        with open("/etc/udev/rules/70-persistent-net.rules", 'a') as f:
            for interface in iterInterfaces:
                f.write('KERNEL=="eth*", ATTR{address}=="%s", NAME="%s"\n' % (interface["mac"], interface["name"]))
            f.flush()
        
        # Add network/interfaces definition
        
        with open("/etc/network/interfaces", 'a') as f:
            for interface in iterInterfaces:
                f.write("\nauto %s\n" % interface["name"])
                f.write("iface %s inet dhcp\n\n" % interface["name"])
            f.flush()
        
        # Stop udev
        
        cmd = dissomniagLive.commands.StandardCmd("/etc/init.d/udev stop", log)
        code, output = cmd.run()
        if code != 0:
            pass
        
        # Start udev
        cmd = dissomniagLive.commands.StandardCmd("/etc/init.d/udev start", log)
        code, output = cmd.run()
        if code != 0:
            pass
        
        # Restart Networking
        cmd = dissomniagLive.commands.StandardCmd("/etc/init.d/networking restart", log)
        code, output = cmd.run()
        if code != 0:
            pass
    
    def getUUID(self):
        return self.uuid
    
    def _parseAdminPW(self, password):
        saltchars = string.ascii_letters + string.digits + './'
        salt = "$1$"
        salt += ''.join([ random.choice(saltchars) for x in range(8) ])
        self.adminPW = crypt.crypt(password, salt)
        
    def authServer(self, username, password):
        if username != self.uuid:
            return False
        
        if not self.adminPW == crypt.crypt(password, self.adminPW):
            return False
        
        return True
    
    def _copySSHKeys(self):
        pass
    
    def _addInitialUserKeys(self):
        pass
    
    def _generateSSLCertificates(self):
        # Regenerate SSL Certs
        cmd = dissomniagLive.commands.StandardCmd("make-ssl-cert generate-default-snakeoil", log)
        code, output = cmd.run()
        if code != 0:
            pass
    
    def _getLocalInterfaceNames(self):
        excludedInterfaces = ['lo', 'lo0']
        returnMe = []
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            if interface in excludedInterfaces:
                continue
            returnMe.append(interface)
        return returnMe
    
    def authRPCUser(self, username, password):
        if username != "admin":
            return LOGIN_SIGN.NO_SUCH_USER, None
        if password != "test":
            return LOGIN_SIGN.SECRET_UNVALID, None
        if username == "admin" and password == "test":
            return LOGIN_SIGN.VALID_USER, None
        else:
            return LOGIN_SIGN.UNVALID_ACCESS_METHOD, None
        
    def start(self):
        if self.isStarted:
            raise RuntimeError("Restart is not allowed!")
        else:
            self.isStarted = True
            dissomniagLive.server.startRPCServer()
            
