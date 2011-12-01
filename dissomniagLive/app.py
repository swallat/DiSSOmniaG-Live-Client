# -*- coding: utf-8 -*-
'''
Created on 29.11.2011

@author: Sebastian Wallat
'''
import multiprocessing, threading
import subprocess, shlex, logging, os
import time
import dissomniagLive
from dissomniagLive import appStates

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
        elif appState == AppState.CLONEDT:
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

class App(multiprocessing.Process):
    '''
    classdocs
    '''

    def __init__(self, name, serverUser, serverIpOrHost, branchName):
        
        '''
        Constructor
        '''
        multiprocessing.Process.__init__(self)
        
        self.name = name
        self.serverConnector = ("%s@%s:%s.git" % (serverUser, serverIpOrHost, self.name))
        self.serverUser = serverUser
        self.serverIpOrHost = serverIpOrHost
        self.lock = multiprocessing.Condition()
        self.waitingCondition = multiprocessing.Condition(self.lock)
        self.threadingLock = threading.RLock()
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.state = 0
        self.namespace.log = "INIT"
        self.namespace.actionToDoArrived = False
        self.namespace.action = None
        self.isRunning = True
        self.stateObjects = {}
        self.state = None
        self.log = None
        self.formatter = None
        self.time = None
        self.isInterrupted = False
        self.branchName = branchName
        
    def getInfo(self):
        return self.namespace.state, self.namespace.log
    
    def run(self):
        with self.lock:
            self._prepare()
            while self.isRunning:
                if not self.namespace.actionToDoArrived:
                    self.waitingCondition.wait() # Nur warten, wenn kein Auftrag vorliegt 
                
                if self.namespace.actionToDoArrived:
                    self.namespace.actionToDoArrived = False
                    
            self._cleanUp()
                    
                    pexpect
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
        
        self._initLogger()
        self.log.info("Select Initial State")
        
        self._selectState(AppState.INIT)
        
        self._clone()
        
    def _addServerKeyToEnvironment(self):
        
        cmd = shlex.split(("ssh %s@%s" % (self.serverUser, self.serverIpOrHost) ))
        proc = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, subprocess.STDOUT)
        proc.stdout.write("yes\n")
        time.sleep(2)
        proc.terminate()
        return
        
    def _initLogger(self):
        with self.threadingLock:
            self.log = logging.getLogger(self.name)
            self.log.setLevel(logging.DEBUG)
            self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - ", self.name, " :: %(message)s")
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
        return os.path.join(dissomniagLive.config.appBaseFolder, ("%s.app" % self.app.name))
        
        
    def _selectState(self, appState):
        with self.threadingLock:
            if AppState.isValid(appState):
                self.state = self.stateObjects[appState]
                self.namespace.state = AppState.getName(appState)
        
    
    def _cleanUp(self):
        """
        Delete git Folder and do other cleanup work
        """
        self._removeMeFromDispatcher()
    
    def _removeMeFromDispatcher(self):
        """
        Delete current object from Dispatcher
        """
        
    def _cleanLog(self):
        with self.threadingLock and self.lock:
            self.namespace.log = ""
            
    def _appendRemoteLog(self, msg):
        with self.threadingLock and self.lock:
            self.log = self.log + msg + "\n"
        
    def _sendInfo(self):
        with self.lock and self.threadingLock: # Da wir auf namespace Daten lesend bzw. schreibend zugreifen
            pass
    
    def _interrupt(self):
        with self.lock:
            if isinstance(self.thread, threading.Thread) and self.proc.is_alive():
                try:
                    self.isInterrupted = True
                    if isinstance(self.proc, subprocess.Popen):
                        self.proc.interrupt() # Let the actor join the process
                except OSError:
                    pass
                finally:
                    self.thread.join()
                    self.isInterrupted = False
                    
    def _abstractStartActor(self, actorToRun):
        with self.lock:
            if isinstance(actorToRun, threading.Thread):
                self._interrupt()
                self.thread = actorToRun
                self.thread.start()
    
    def _startStandard(self):
        self._startScript("start")
            
    def _startScript(self, scriptName):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._Tstart, scriptName))
    
    def _stop(self):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._Tstop))
            
    def _clone(self):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._Tclone))
            
    def _compile(self):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._Tcompile))
    
    def _reset(self):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._Treset))
            
    def _refreshGit(self, tagOrCommit = None):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._TrefreshGit, tagOrCommit))
    
    def _refreshGitAndReset(self, tagOrCommit = None):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._TrefreshGitAndReset, tagOrCommit))
    
    def _Tstart(self, actor, scriptName, *args, **kwargs):
        pass
    
    def _Tstop(self, actor, *args, **kwargs):
        pass

    def _Tclone(self, actor, *args, **kwargs):
        pass
    
    def _Tcompile(self, actor, *args, **kwargs):
        pass
    
    def _Treset(self, actor, *args, **kwargs):
        pass
    
    def _TrefreshGit(self, actor, tagOrCommit = None, *args, **kwargs):
        pass
    
    def _TrefreshGitAndReset(self, actor, tagOrCommit = None, *args, **kwargs):
        pass
        
class GeneralActor(threading.Thread):
    
    worker = None
    
    def __init__(self, app, functionToRun, *args, **kwargs):
            
        threading.Thread.__init__(self, group = None, target = None, name = None, verbose = None)
        self.app = app
        self.functionToRun = functionToRun
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        self.functionToRun(actor = self, *self.args, **self.kwargs)
        self.app._sendInfo()
            
            
    
                
            
            
        
        