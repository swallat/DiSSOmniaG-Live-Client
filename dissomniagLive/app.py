# -*- coding: utf-8 -*-
'''
Created on 29.11.2011

@author: Sebastian Wallat
'''
import multiprocessing, threading
import signal
import subprocess, shlex, logging, os
import time
import xmlrpc.client
from xml.etree import ElementTree#
import dissomniagLive
from dissomniagLive import appStates
import shutil

class AppState:
    INIT = 0
    CLONED = 1
    COMPILED = 2
    STARTED = 3
    CLONE_ERROR = 4
    PULL_ERROR = 5
    COMPILE_ERROR = 6
    RUNTIME_ERROR = 7
    
    @staticmethod
    def isValid(appState):
        if 0 <= appState < 8 and isinstance(appState, int):
            return True
        else:
            return False
    
    @staticmethod
    def getName(appState):
        if appState == AppState.INIT:
            return "INIT"
        elif appState == AppState.CLONED:
            return "CLONED"
        elif appState == AppState.COMPILED:
            return "COMPILED"
        elif appState == AppState.STARTED:
            return "STARTED"
        elif appState == AppState.CLONE_ERROR:
            return "CLONE_ERROR"
        elif appState == AppState.PULL_ERROR:
            return "PULL_ERROR"
        elif appState == AppState.COMPILE_ERROR:
            return "COMPILE_ERROR"
        elif appState == AppState.RUNTIME_ERROR:
            return "RUNTIME_ERROR"
        
class AppActions:
    START = 0
    STOP = 1
    COMPILE = 2
    RESET = 3
    INTERRUPT = 4
    REFRESH_GIT = 5
    REFRESH_AND_RESET = 6
    CLONE = 7
    DELETE = 8
    CLEAN = 9
    
    @staticmethod
    def isValid(appState):
        if 0 <= appState < 10 and isinstance(appState, int):
            return True
        else:
            return False
    
    @staticmethod
    def getName(appState):
        if appState == AppActions.START:
            return "START"
        elif appState == AppActions.STOP:
            return "STOP"
        elif appState == AppActions.COMPILE:
            return "COMPILE"
        elif appState == AppActions.RESET:
            return "RESET"
        elif appState == AppActions.INTERRUPT:
            return "INTERRUPT"
        elif appState == AppActions.REFRESH_GIT:
            return "REFRESH_GIT"
        elif appState == AppActions.REFRESH_AND_RESET:
            return "REFRESH_AND_RESET"
        elif appState == AppActions.CLONE:
            return "CLONE"
        elif appState == AppActions.DELETE:
            return "DELETE"
        elif appState == AppActions.CLEAN:
            return "CLEAN"
    
    

class App(multiprocessing.Process):
    '''raise NotImplementedError() 
    classdocs
    '''

    def __init__(self, name, serverUser, serverIpOrHost, rpcServerConnector, branchName, nodeUUID, appDeleteListener):
        
        '''
        Constructor
        '''
        multiprocessing.Process.__init__(self)
        
        self.name = name
        self.serverConnector = ("%s@%s:%s.git" % (serverUser, serverIpOrHost, self.name))
        self.serverUser = serverUser
        self.serverIpOrHost = serverIpOrHost
        self.rpcServerConnector = rpcServerConnector
        self.nodeUUID = nodeUUID
        self.appDeleteListener = appDeleteListener
        self.r_lock = multiprocessing.RLock()
        self.lock = multiprocessing.Condition(self.r_lock)
        self.threadingLock = threading.RLock()
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.state = 0
        self.namespace.log = "INIT"
        self.namespace.actionToDoArrived = False
        self.namespace.action = None
        self.namespace.scriptName = None
        self.namespace.tagOrCommit = None
        self.isRunning = True
        self.stateObjects = {}
        self.state = None
        self.log = None
        self.formatter = None
        self.time = None
        self.isInterrupted = False
        self.branchName = branchName
        self.ignoreRefresh = False
    
    def run(self):
        with self.lock:
            self._prepare()
            while self.isRunning:
                if not self.namespace.actionToDoArrived:
                    self.lock.wait() # Nur warten, wenn kein Auftrag vorliegt 
                
                if self.namespace.actionToDoArrived:
                    self.namespace.actionToDoArrived = False
                    
                    action = self.namespace.action
                    self.namespace.action = None
                    
                    scriptName = self.namespace.scriptName
                    self.namespace.scriptName = None
                    
                    tagOrCommit = self.namespace.tagOrCommit
                    self.namespace.tagOrCommit = None
                    
                    if action == AppActions.START:
                        self._startScript(scriptName)
                    elif action == AppActions.STOP:
                        self._stop()
                    elif action == AppActions.INTERRUPT:
                        self._interrupt()
                    elif action == AppActions.REFRESH_GIT:
                        self._refreshGit(tagOrCommit)
                    elif action == AppActions.REFRESH_AND_RESET:
                        self._refreshGitAndReset(tagOrCommit)
                    elif action == AppActions.CLONE:
                        self._clone()
                    elif action == AppActions.COMPILE:
                        self._compile()
                    elif action == AppActions.RESET:
                        self._reset()
                    elif action == AppActions.DELETE:
                        self._appendRemoteLog("Delete App!")
                        self.log.info("Delete App!")
                        self.isRunning = False
                        break
                    elif action == AppActions.CLEAN:
                        self._clean()
                    
            self._stop()
            self._cleanUp()
            
    def startMe(self, scriptName = None):
        with self.lock:
            self.namespace.scriptName = scriptName
            self.namespace.action = AppActions.START
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
    
    def stop(self):
        with self.lock:
            self.namespace.action = AppActions.STOP
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
    
    def interrupt(self):
        with self.lock:
            self.namespace.action = AppActions.INTERRUPT
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
    
    def refreshGit(self, commitOrTag = None):
        with self.lock:
            self.namespace.commitOrTag = commitOrTag
            self.namespace.action = AppActions.REFRESH_GIT
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
    
    def refreshAndReset(self, commitOrTag = None):
        with self.lock:
            self.namespace.commitOrTag = commitOrTag
            self.namespace.action = AppActions.REFRESH_AND_RESET
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
    
    def clone(self):
        with self.lock:
            self.namespace.action = AppActions.CLONE
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
    
    def compile(self):
        with self.lock:
            self.namespace.action = AppActions.COMPILE
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
    
    def reset(self):
        with self.lock:
            self.namespace.action = AppActions.RESET
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
            
    def delete(self):
        with self.lock:
            self.namespace.action = AppActions.DELETE
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
        
    def clean(self):
        with self.lock:
            self.namespace.action = AppActions.CLEAN
            self.namespace.actionToDoArrived = True
            self.lock.notify_all()
            return True
    
    def getInfo(self):
        return self._getInfoXmlMsg()

    def _prepare(self):
        """
        Select Initial State and CheckOut
        """
        self.stateObjects = {}
        self.stateObjects[AppState.CLONED] = appStates.Cloned_AppState(self)
        self.stateObjects[AppState.CLONE_ERROR] = appStates.CloneError_AppState(self)
        self.stateObjects[AppState.COMPILED] = appStates.Compiled_AppState(self)
        self.stateObjects[AppState.COMPILE_ERROR] = appStates.CompileError_AppState(self)
        self.stateObjects[AppState.INIT] = appStates.Init_AppState(self)
        self.stateObjects[AppState.PULL_ERROR] = appStates.PullError_AppState(self)
        self.stateObjects[AppState.RUNTIME_ERROR] = appStates.RuntimeError_AppState(self)
        self.stateObjects[AppState.STARTED] = appStates.Started_AppState(self)
        
        dissomniagLive.LiveIdentity.prepareSSHEnvironment()
        dissomniagLive.LiveIdentity.disableStrictServerKeyChecking(self.serverIpOrHost)
        
        self._initLogger()
        self.log.info("Select Initial State")
        
        self._selectState(AppState.INIT)
        
        self._clone()
        
    def _initLogger(self):
        with self.threadingLock:
            self.log = logging.getLogger(self.name)
            self.log.setLevel(logging.DEBUG)
            self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - :: %(message)s")
            self.time = time.strftime("%d_%m_%Y_%H_%M_%S")
            fileHandler = logging.FileHandler(os.path.join(dissomniagLive.config.appLogFolder, ("%s_%s.DEBUG" % (self.name, self.time))))
            fileHandler.setFormatter(self.formatter)
            self.log.addHandler(fileHandler)
    
    def _addGitLog(self, appFolder):
        with self.threadingLock:
            if self.log == None:
                self._initLogger()
                
            logFile = ("%s/log/%s_%s.DEBUG" % (self.appFolder, self.name, self.time))
            gitFileHandler = logging.FileHandler(os.path.join(dissomniagLive.config.appBaseFolder, logFile))
            gitFileHandler.setFormatter(self.formatter)
            self.log.addHandler(gitFileHandler)
    
    def getLogger(self):
        with self.threadingLock:
            if self.log == None:
                self._initLogger()
            
            if self.log != None:
                return self.log
        
        
    def _getServerConnector(self):
        return self.serverConnector
    
    def _getTargetPath(self):
        return os.path.join(dissomniagLive.config.appBaseFolder, ("%s.app" % self.name))
    
    def _getOperateDirectory(self):
        return os.path.join(self._getTargetPath(), dissomniagLive.config.operateSubdirIdentifier)
    
    def _getResultsDirectory(self):
        return os.path.join(self._getTargetPath(), dissomniagLive.config.resultsSubdirIdentifier)
    
    def _getIgnoreRefresh(self):
        with self.lock:
            return self.ignoreRefresh
    
    def _setIgnoreRefresh(self, mSet = False):
        with self.threadingLock:
            self.ignoreRefresh = mSet
        
    def _selectState(self, appState):
        with self.threadingLock:
            if AppState.isValid(appState):
                self.state = self.stateObjects[appState]
                self.namespace.state = appState
        
    
    def _cleanUp(self):
        """
        Delete git Folder and do other cleanup work
        """
        try:
            shutil.rmtree(self._getTargetPath())
        except OSError:
            pass
        self._removeMeFromDispatcher()
    
    def _removeMeFromDispatcher(self):
        """
        Delete current object from Dispatcher
        """
        self.appDeleteListener.deleteApp(self.name)
        
    def _cleanLog(self):
        with self.threadingLock:
            self.namespace.log = ""
            
    def _appendRemoteLog(self, msg):
        with self.threadingLock:
            self.namespace.log = self.namespace.log + msg + "\n"
            
    def _getInfoXmlMsg(self):
        with self.threadingLock:
            tree = ElementTree.Element("AppInfo")
            uuid = ElementTree.SubElement(tree, "uuid")
            uuid.text = str(self.nodeUUID)
            appName = ElementTree.SubElement(tree, "appName")
            appName.text = str(self.name)
            state = ElementTree.SubElement(tree, "state")
            state.text = str(self.namespace.state)
            log = ElementTree.SubElement(tree, "log")
            log.text = str(self.namespace.log)
            return ElementTree.tostring(tree)
        
    def _sendInfo(self):
        with self.threadingLock: # Da wir auf namespace Daten lesend bzw. schreibend zugreifen
            try:
                proxy = xmlrpc.client.ServerProxy(dissomniagLive.getIdentity().getServerUri())
                self.log.info(self._getInfoXmlMsg())
                proxy.updateAppInfo(self._getInfoXmlMsg())
            except Exception as e:
                self.log.error("Could not send Info to central system. %s" % str(e))
            else:
                self._cleanLog()
    
    def _interrupt(self):
       if hasattr(self, "proc") and self.proc.poll() == None:
            try:
                with self.threadingLock:
                    self.isInterrupted = True
                    if isinstance(self.proc, subprocess.Popen):
                        os.killpg(self.proc.pid, signal.SIGTERM) # Let the actor join the process
            except OSError:
                pass
            finally:
                if isinstance(self.thread, GeneralActor) and self.thread.is_alive():
                    self.log.info("Try to join")
                    self.thread.join()
                    self.log.info("Joined")
                self.isInterrupted = False
                    
    def _abstractActor(self, actorToRun):
        with self.lock:
            if isinstance(actorToRun, GeneralActor):
                self._interrupt()
                self.thread = actorToRun
                self.thread.start()
    
    def _startStandard(self):
        self._startScript("start")
            
    def _startScript(self, scriptName):
        with self.lock:
            if scriptName == None:
                self._startStandard()
            else:
                self._abstractActor(GeneralActor(self, self._Tstart, scriptName = scriptName))
    
    def _stop(self):
        with self.lock:
            if self.namespace.state == AppState.STARTED:
                self._interrupt()
            else:
                self._abstractActor(GeneralActor(self, self._Tstop))
            
    def _clone(self):
        with self.lock:
            self._abstractActor(GeneralActor(self, self._Tclone))
            
    def _compile(self):
        with self.lock:
            self._abstractActor(GeneralActor(self, self._Tcompile))
    
    def _reset(self):
        with self.lock:
            self._abstractActor(GeneralActor(self, self._Treset))
            
    def _refreshGit(self, tagOrCommit = None):
        with self.lock:
            if not self._getIgnoreRefresh():
                self._abstractActor(GeneralActor(self, self._TrefreshGit, tagOrCommit = tagOrCommit))
            else:
                self._setIgnoreRefresh(mSet = False)
    
    def _refreshGitAndReset(self, tagOrCommit = None):
        with self.lock:
            if not self._getIgnoreRefresh():
                self._abstractActor(GeneralActor(self, self._TrefreshGitAndReset, tagOrCommit = tagOrCommit))
            else:
                self._setIgnoreRefresh(mSet = False)
            
    def _clean(self):
        with self.lock:
            self._abstractActor(GeneralActor(self, self._Tclean))
    
    def _Tstart(self, actor, scriptName, *args, **kwargs):
        return self.state.start(actor, scriptName)
    
    def _Tstop(self, actor, *args, **kwargs):
        return self.state.stop(actor)

    def _Tclone(self, actor, *args, **kwargs):
        return self.state.clone(actor)
    
    def _Tcompile(self, actor, *args, **kwargs):
        return self.state.compile(actor)
    
    def _Treset(self, actor, *args, **kwargs):
        return self.state.reset(actor)
    
    def _TrefreshGit(self, actor, tagOrCommit = None, *args, **kwargs):
        return self.state.refreshGit(actor, tagOrCommit)
    
    def _TrefreshGitAndReset(self, actor, tagOrCommit = None, *args, **kwargs):
        return self.state.refreshAndReset(actor)
    
    def _Tclean(self, actor, *args, **kwargs):
        return self.state.clean(actor)
        
class GeneralActor(threading.Thread):
    
    worker = None
    
    def __init__(self, app, functionToRun, *args, **kwargs):
            
        threading.Thread.__init__(self, group = None, target = None, name = None, verbose = None)
        self.app = app
        self.functionToRun = functionToRun
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        ret = None
        try:
            ret = self.functionToRun(actor = self, *self.args, **self.kwargs)
        finally:
            import logging
            log = logging.getLogger("dissomniagLive.app.GeneralActor")
            log.info("App %s, %s finished. Ret: %s" % (self.app.name, self.functionToRun.__name__, str(ret)))
            self.app._sendInfo()
            log.info("App %s, After sendInfo %s" % (self.app.name, self.functionToRun.__name__))
            
            
            
            
    
                
            
            
        
        