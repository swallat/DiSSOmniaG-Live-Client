#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 27.09.2011

@author: Sebastian Wallat
"""

import sys, os, time, atexit, signal
import setproctitle
import config

#===============================================================================
# The Following Code is nearly totally written by Sander Marechal.
# It can be found under following URL:
#  http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#===============================================================================
 
class Daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pidfile, debug = False): 
        self.pidfile = pidfile
        self.debug = debug 
    
    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""

        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir('/') 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:

                # exit from second parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1) 
    
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # write pidfile
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')
    
    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon."""

        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:

                pid = int(pf.read().strip())
        except IOError:
            pid = None
    
        if pid:
            message = "pidfile {0} already exist. " + \
                    "Daemon already running?\n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)
        
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""

        # Get the pid from the pidfile
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
    
        if not pid:
            message = "pidfile {0} does not exist. " + \
                    "Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return # not an error in a restart

        # Try killing the daemon process    
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print((str(err.args)))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    def run(self):
        """You should override this method when you subclass Daemon.
        
        It will be called after the process has been daemonized by 
        start() or restart()."""
                
#===============================================================================
# End of extraction.
# It can be found under following URL:
#  http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#===============================================================================



class DissomniagDaemon(Daemon):
    
    def run(self):
        setproctitle.setproctitle("dissomniagLive")
        if self.debug:
            myFile = open("/var/log/dissomniagDaemonInfo.log", "a+")
            myFile.write("In run")
            myFile.flush()
            sys.stdout = myFile
            sys.stderr = myFile
        import dissomniagLive
        dissomniagLive.run()
        
        if self.debug:
            myFile.close()
            
def printUsage():
    print("DiSSOmniagLive Starter.")
    print(("Usage: %s [--nodaemon]|--daemon [start|stop|restart]" % sys.argv[0]))
    print("\t --nodaemon \t\t Starts DiSSOmniaG attached to the users terminal.")
    print("\t --daemon [start|stop|restart] \t Starts, stops or restarts DiSSOmniaG as a daemon process.")

if __name__ == "__main__":
    if os.getuid() != 0:
        print("DiSSOmniaGLive must be started as root!")
        sys.exit(-1)
    
    if len(sys.argv) == 3 and "--daemon" == sys.argv[1]:
            pidFile = config.pidFile
            daemon = DissomniagDaemon(pidFile)
            if 'start' == sys.argv[2]:
                    daemon.start()
            elif 'stop' == sys.argv[2]:
                    daemon.stop()
            elif 'restart' == sys.argv[2]:
                    daemon.restart()
            else:
                    print("Unknown command")
                    printUsage()
                    sys.exit(2)
            sys.exit(0)
    elif len(sys.argv) == 1 or (len(sys.argv) == 2 and "--nodaemon" == sys.argv[1]):
        setproctitle.setproctitle("dissomniagLive")
        import dissomniagLive
        dissomniagLive.run()
    else:
            printUsage()
            sys.exit(2)
