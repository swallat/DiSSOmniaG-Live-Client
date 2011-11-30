# -*- coding: utf-8 -*-
'''
Created on 29.11.2011

@author: Sebastian Wallat
'''
import multiprocessing, threading
import subprocess, shlex, logging
import time
import dissomniagLive

class AppState:
    INIT = 0
    CHECKED_OUT = 1
    COMPILED = 2
    STARTED = 3
    CLONE_ERROR = 4
    PULL_ERROR = 5
    COMPILE_ERROR = 6
    RUNTIME_ERROR = 7
    
    @staticmethod
    def isValid(appState):
        if 0 <= appState < 8:
            return True
        else:
            return False
    
    @staticmethod
    def getName(appState):
        if appState == AppState.INIT:
            return "INIT"
        elif appState == AppState.CHECKED_OUT:
            return "CHECKED_OUT"
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

    def __init__(self, name, serverUri):
        
        '''
        Constructor
        '''
        multiprocessing.Process.__init__(self)
        
        self.name = name
        self.serverUri = serverUri
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
        
    def selectState(self, appState):
        if not AppState.isValid(appState):
            return
                
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
                    
                    
    def _prepare(self):
        """
        Select Initial State and CheckOut
        """
    
    def _cleanUp(self):
        """
        Delete git Folder and do other cleanup work
        """
        self._removeMeFromDispatcher()
    
    def _removeMeFromDispatcher(self):
        """
        Delete current object from Dispatcher
        """
        
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
            
    def _start(self):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._Tstart))
    
    def _stop(self):
        with self.lock:
            self._abstractStartActor(GeneralActor(self, self._Tstop))
            
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
    
    def _Tstart(self, actor, *args, **kwargs):
        pass
    
    def _Tstop(self, actor, *args, **kwargs):
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
            
            
    
                
            
            
        
        