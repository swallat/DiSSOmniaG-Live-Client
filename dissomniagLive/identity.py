# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""
import os
import logging
import sys, socket, fcntl, struct
import crypt, string, random
import xmlrpc.client
from xml.etree import ElementTree#
import subprocess
import threading
import time
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
    commonName = None
    adminPW = None
    serverIp = None
    isStarted = False
    pathToCd = "/media/cdrom/"
    serverReachable = False
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
        
        self.fetchConfig(tree, fetchInterfaces = True)
        
        try:
            self._renameInterfaces(self.iterInterfaces)
            self._generateSSLCertificates()
        finally:
            self._umountCdImage()
            
    def fetchConfig(self, tree, update = False):
        if not update:
            uuid = tree.find("uuid")
            if uuid != None:
                self.uuid = str(uuid.text)
                
        commonName = tree.find("commonName")
        if commonName != None:
            self.commonName = str(commonName.text)
        
        serverIp = tree.find("serverIp")
        if serverIp != None:
            self.serverIp = str(serverIp.text)
        
        password = tree.find("password")
        if password != None:
            self._changePW(str(password.text))
            self._parseAdminPW(str(password.text))
        
        sshKeys = []
        keys = tree.findall("sshKey")
        for key in keys:
            sshKeys.append(str(key.text))
        self._addSSHKeys(sshKeys)
        
        if not update:
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
            
    
    def _mountCdImage(self):
        try:
            os.mkdir(self.pathToCd, 444)
        except (OSError, IOError) as e:
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
        except (OSError, IOError) as e:
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
        
    def _addSSHKeys(self, sshKeys):
        
        # 1. Create SSH Dir
        try:
            os.makedirs("/home/user/.ssh", mode=0o700)
        
            # 2. Add Keys
            with open("/home/user/.ssh/authorized_keys", 'w') as f:
                for key in sshKeys:
                    f.write("%s\n" % key)
            
            # 3. Chmod authorized_keys
            
            os.chmod("/home/user/.ssh/authorized_keys", mode = 0o600)
        except (IOError, OSError):
            pass
        
    
    def getUUID(self):
        return self.uuid
    
    def _changePW(self, password):
        if password == "" or password == " ":
            return
        
        # 1. Change Password for Admin User
        proc = subprocess.Popen("passwd -q root", \
                                stdin = subprocess.PIPE,\
                                stdout = subprocess.PIPE,\
                                stderr = subprocess.STDOUT)
        proc.stdin.write("%s\n%s\n" % (password, password))
        remainder = proc.communicate()
        
        # 2. Change User Password
        proc = subprocess.Popen("passwd -q user", \
                                stdin = subprocess.PIPE,\
                                stdout = subprocess.PIPE,\
                                stderr = subprocess.STDOUT)
        proc.stdin.write("%s\n%s\n" % (password, password))
        remainder = proc.communicate()
    
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
        
    def _getIpAddress(self, ifname):
        if not isinstance(ifname, bytes):
            ifname = str.encode(ifname)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
                                            s.fileno(),
                                            0x8915,  # SIOCGIFADDR
                                            struct.pack('256s', ifname[:15])
                                            )[20:24])
    def _getMaintainIp(self):
        if not self.isStarted:
            return None
        return self._getIpAddress("maintain")
        
    def getXMLStatusAnswer(self):
        tree = ElementTree.Element("NodeLiveInfo")
        uuid = ElementTree.SubElement(tree, "uuid")
        uuid.text = str(self.uuid)
        maintainIp = ElementTree.SubElement(tree, "maintainIp")
        maintainIp.text = str(self._getMaintainIp())
        state = ElementTree.SubElement(tree, "state")
        state.text = "UP"
        return bytes.decode(ElementTree.tostring(tree, pretty_print= True))
        
    
    def authRPCUser(self, username, password):
        if username != "maintain":
            return LOGIN_SIGN.NO_SUCH_USER, None
        if password != "test":
            return LOGIN_SIGN.SECRET_UNVALID, None
        if username == "maintain" and password == self.uuid:
            return LOGIN_SIGN.VALID_USER, None
        else:
            return LOGIN_SIGN.UNVALID_ACCESS_METHOD, None
        
    def getServerUri(self):
        return ("https://%s:%s@%s:%s/" % (self.commonName, self.uuid, self.serverIp, str(dissomniagLive.config.remoteRpcServerPort)))
    
    def sendUpdateToServer(self):
        
        class InitialSend(threading.Thread):
            
            def run(self):
                time.sleep(2)
                proxy = xmlrpc.client.ServerProxy(dissomniagLive.getIdentity().getServerUri())
                for i in range(1,5):
                    if proxy.update(dissomniagLive.getIdentity().getXMLStatusAnswer()) == True:
                        dissomniagLive.getIdentity().serverReachable = True
                        log.info("Pushed local Infos to Server.")
                        break
                if dissomniagLive.getIdentity().serverReachable == False:
                    log.error("Could not reach Central Server!")
                    
        InitialSend().start()
        
        
        
    def start(self):
        if self.isStarted:
            raise RuntimeError("Restart is not allowed!")
        else:
            self.prepare()
            self.isStarted = True
            self.sendUpdateToServer()
            dissomniagLive.server.startRpcServer()
            
    def cleanUp(self):
        pass
            
