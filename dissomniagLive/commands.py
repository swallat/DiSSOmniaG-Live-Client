# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""
import subprocess, shlex, logging
import dissomniag

log = logging.getLogger("dissomniagLive.commands.py")

class InteractiveCommand(object):
    """
    classdocs
    """


    def __init__(self):
        """
        Constructor
        """
        
class StandardCmd(object):
    
    def __init__(self, cmd, log):
        
        if type(cmd) == 'list':
            self.cmd = cmd
        else:
            self.cmd = shlex.split(cmd)
        
        self.log = log
        self.output = []
        self.runned = False
        
    def multiLog(self, msg):
        msg = msg.strip()
        self.log.info(msg)
        self.output.append(msg)
        
    def run(self):
        if self.runned:
            raise RuntimeError('A Standard CMD can only be called once.')
        
        self.runned = True
        
        self.multiLog("Running %s" % " ".join(self.cmd))
        
        self.proc = subprocess.Popen(self.cmd, stdin = subprocess.PIPE,
                                               stdout = subprocess.PIPE,
                                               stderr = subprocess.STDOUT)#
        self._readOutput(self.proc)
        com = self.proc.communicate()[0]
        if com != []:
            self.multiLog(com)
        return self.proc.returncode, self.output
    
    def _readOutput(self, proc):
        while True:
            line = proc.stdout.readline()
            if not line:
                return
            self.multiLog(line)
        
