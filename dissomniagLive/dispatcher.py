# -*- coding: utf-8 -*-
'''
Created on 01.12.2011

@author: Sebastian Wallat
'''
import multiprocessing
import threading
import dissomniagLive

class Dispatcher(object):
    '''
    classdocs
    '''


    def __new__(cls, *args, **kwargs):
        # Store instance on cls._instance_dict with cls hash
        key = str(hash(cls))
        if not hasattr(cls, '_instance_dict'):
            cls._instance_dict = {}
        if key not in cls._instance_dict:
            cls._instance_dict[key] = \
                super(Dispatcher, cls).__new__(cls, *args, **kwargs)
        return cls._instance_dict[key]

    def __init__(self):
        if not '_ready' in dir(self):
            # Der Konstruktor wird bei jeder Instanziierung aufgerufen.
            # Einmalige Dinge wie zum Beispiel die Initialisierung von Klassenvariablen müssen also in diesen Block.
            self._ready = True
            self.lock = multiprocessing.RLock()
            self.apps = {}
            
            self.waitingCondition = multiprocessing.Condition()
            self.manager = multiprocessing.Manager()
            self.namespace = self.manager.Namespace()
            self.appDeleteListener = AppDeleteListener(self, self.waitingCondition, self.namespace)
            self.appDeleteListener.start()
            
    def _removeAppFromDict(self, appName):
        with self.lock:
            self.apps.pop(appName)
    
    def _isIn(self, name):
        with self.lock:
            if self.apps.get(name) != None:
                return True
            else:
                return False
        
    def addApp(self, name, serverUser, serverIpOrHost):
        with self.lock:
            if not self._isIn(name):
                app = dissomniagLive.app.App(name, serverUser, serverIpOrHost, dissomniagLive.getIdentity().getServerUri(), name, dissomniagLive.getIdentity().getUUID(), self.appDeleteListener)
                self.apps[name] = app
                return app
                
            
    def _getApp(self, name):
        with self.lock:
            return self.apps.get(name)
        
    def startApp(self, name, serverUser, serverIpOrHost, scriptName):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.start(scriptName)
            else:
                return self.addApp(name, serverUser, serverIpOrHost).start(scriptName)
                
    def stopApp(self, name, serverUser, serverIpOrHost):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.stop()
            else:
                return self.addApp(name, serverUser, serverIpOrHost).stop()
                
    def interruptApp(self, name, serverUser, serverIpOrHost):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.interrupt()
            else:
                return self.addApp(name, serverUser, serverIpOrHost).interrupt()
                
    def refreshGitApp(self, name, serverUser, serverIpOrHost, commitOrTag = None):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.refreshGit(commitOrTag)
            else:
                return self.addApp(name, serverUser, serverIpOrHost).refreshGit(commitOrTag)
    
    def refreshAndResetApp(self, name, serverUser, serverIpOrHost, commitOrTag = None):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.refreshAndReset(commitOrTag)
            else:
                return self.addApp(name, serverUser, serverIpOrHost).refreshAndReset(commitOrTag)
                
    def cloneApp(self, name, serverUser, serverIpOrHost):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.clone()
            else:
                return self.addApp(name, serverUser, serverIpOrHost).clone()
    
    def compileApp(self, name, serverUser, serverIpOrHost):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.compile()
            else:
                return self.addApp(name, serverUser, serverIpOrHost).compile()
                
    def resetApp(self, name, serverUser, serverIpOrHost):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.reset()
            else:
                return self.addApp(name, serverUser, serverIpOrHost).reset()
    
    def deleteApp(self, name, serverUser, serverIpOrHost):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.delete()
            else:
                return True
    
    def getInfo(self, name):
        with self.lock:
            app = self._getApp(name)
            if app != None:
                return app.getInfo()
            else:
                return ""
            
class AppDeleteListener(threading.Thread):
    
    def __init__(self, dispatcher, waitingCondition, namespace):
        threading.Thread.__init__(self, group = None, target = None, name = None, verbose = None)
        self.dispatcher = dispatcher
        self.waitingCondition = waitingCondition
        self.namespace = namespace
        self.namespace.taskArrived = False
        self.namespace.appNameToDelete = None
        self.namespace.killed = False
        
    def run(self):
        with self.waitingCondition:
            while True:
                if not self.namespace.taskArrived:
                    self.waitingCondition.wait()
                if self.namespace.killed:
                    break
                
                appNameToDelete = self.namespace.appNameToDelete
                self.namespace.appNameToDelete = None
                self.dispatcher._removeAppFromDict(appNameToDelete)
                
            
    def deleteApp(self, appNameToDelete):
        with self.waitingCondition:
            self.namespace.appNameToDelete = appNameToDelete
            self.namespace.taskArrived = True
            self.waitingCondition.notify_all()
            
    def killMe(self):
        with self.waitingCondition:
            self.namespace.killed = True
            self.waitingCondition.notify_all()
    
    
    
        