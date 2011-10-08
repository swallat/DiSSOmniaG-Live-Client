# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""
import os
import logging
import sys
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
        
    @staticmethod
    def getIdentity():
        return LiveIdentity()
        
    def prepare(self):
        if not self._mountCdImage():
            log.Error("General Error")
            sys.exit(-1)
            
        with open(self.liveInfoFile, 'rt') as f:
            tree = ElementTree.parse(f)
        
        uuid = tree.find("uuid")
        if uuid != None:
            self.uuid = str(uuid.text)
        
        serverIp = tree.find("serverIp")
        if serverIp != None:
            self.serverIp = str(serverIp.text)
        
        password = tree.find("password")
        if password != None:
            self._parseAdminPW(str(password.text))
        
        iterInterfaces = []
        interfaces = tree.findall("interface")
        for interface in interfaces:
            name = interface.find("name")
            mac = interface.find("mac")
            if name != None and mac != None:
                i = {}
                i["name"] = str(name.text)
                i["mac"] = str(mac.text)
                iterInterfaces.append(i)
        self.iterInterfaces = iterInterfaces
        try:
            self._renameInterfaces(iterInterfaces)
            self._generateSSLCertificates()
        finally:
            self._umountCdImage()
    
    def _mountCdImage(self):
        try:
            os.mkdir(self.pathToCd, 444)
        except IOError as e:
            log.Error("Could not create Cdrom Directory!")
            
        
        cmd = dissomniagLive.commands.StandardCmd("mount /dev/cdrom /media/cdrom", log = log)
        code, output = cmd.run()
        if code != 0:
            log.Error("Could not mount Cd")
        return True
    
    def _umountCdImage(self):
        cmd = dissomniagLive.commands.StandardCmd("umount /dev/cdrom", log = log)
        code, output = cmd.run()
        if code != 0:
            log.Error("Could not umount Cd")
    
        try:
            os.rmdir(self.pathToCd)
        except IOError as e:
            log.Error("Could not create Cdrom Directory!")
        
        return True
        
        
    
    def _renameInterfaces(self, iterInterfaces):
        # Deactivate all Interfaces
        lastFound = False
        i = 0
        while not lastFound:
            interface = "eth%d" % i
            cmd = dissomniagLive.commands.StandardCmd("/sbin/ifconfig %s down" % str(interface), log)
            code, output = cmd.run()
            i = i + 1
            if code != 0:
                lastFound = True
                break
                    
        # Stop Networking
        cmd = dissomniagLive.commands.StandardCmd("/etc/init.d/networking stop", log)
        code, output = cmd.run()
        if code != 0:
            pass
        
        # Add udev rules
        with open("/etc/udev/rules.d/70-persistent-net.rules", 'a') as f:
            for interface in iterInterfaces:
                f.write('KERNEL=="eth*", ATTR{address}=="%s", NAME="%s"\n' % (interface["mac"], interface["name"]))
            f.flush()
        
        # Add network/interfaces definition
        
        with open("/etc/network/interfaces", 'w') as f:
            f.write("auto lo\n")
            f.write("iface lo inet loopback\n")
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
        """
        this is dangerous. Delete following return to secure
        """
        #return self.authRPCUser(username, password)
        ### End DANGEROUS
        
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
            self.prepare()
            self.isStarted = True
            dissomniagLive.server.startRpcServer()
            
    def cleanUp(self):
        pass
            
