'''
Created on 30.11.2011

@author: Sebastian Wallat
'''
import shutil, subprocess
import re
import dissomniagLive
from dissomniagLive.appStates import *

class Cloned_AppState(AbstractAppState):
    '''
    classdocs
    '''
    
    def sourceEnviron(self, actor):
        log = self.app.getLogger()
        environFile = os.path.join(self.app._getTargetPath, "operate/environ")
        
        if os.path.isFile(environFile):
            lines = []
            with open(environFile) as f:
                f = lines.readlines()
            prog = re.compile("^(.*)=(.*)$")   
            for line in lines:
                for result in prog.finditer(line):
                    key = result.groups()[0].strip()
                    value = result.groups()[1].strip()
                    os.environ[key] = value
                    self.multiLog("Added Environ parameter. Key: %s, Value: %s" % (key, value), log.info)
        return True
    
    def clone(self, actor):
        raise NotImplementedError()
                    
    def start(self, actor):
        raise NotImplementedError()
    
    def stop(self, actor):
        raise NotImplementedError()
    
    def after_interrupt(self, actor):
        raise NotImplementedError()
    
    def compile(self, actor):
        raise NotImplementedError()
    
    def refreshGit(self, actor, tagOrCommit = None):
        log = self.app.getLogger()
        
        cmd = shutil.split("git pull")
        
        self.app.proc = subprocess.Popen(cmd, cwd = self.app._getTargetPath, stdout = subprocess.Popen, stdout = subprocess.Popen)
    
    def refreshAndReset(self, actor, tagOrCommot = None):
        raise NotImplementedError()
    
    def reset(self, actor):
        raise NotImplementedError()
                
        