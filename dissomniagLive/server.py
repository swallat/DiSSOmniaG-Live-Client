# -*- coding: utf-8 -*-
"""
Created on 28.09.2011

@author: Sebastian Wallat
"""
# Imports for XML RPC Server
import xmlrpclib, traceback, sys, sched, time, logging
from twisted.web import xmlrpc, server, http
from twisted.internet import defer, reactor, ssl

import dissomniagLive

log = logging.getLogger("server.py")

#===============================================================================
# The Following Twisted XML-RPC Code was extracted in main Parts 
# from the Glab ToMaTo Project.
#===============================================================================


class Introspection():
    def __init__(self, papi):
        self.api = papi

    def listMethods(self, user = None):
        return [m for m in dir(self.api) if (callable(getattr(self.api, m)) 
                                             and not m.startswith("_"))]
    
    # ToDO Reimplememtz
    def methodSignature(self, method, user = None):
        func = getattr(self.api, method)
        if not func:
            return "Unknown method: %s" % method
        import inspect
        argspec = inspect.getargspec(func)
        argstr = inspect.formatargspec(argspec.args[:-1], defaults = argspec.defaults[:-1])
        return method + argstr

    def methodHelp(self, method, user = None):
        func = getattr(self.api, method)
        if not func:
            return "Unknown method: %s" % method
        doc = func.__doc__
        if not doc:
            return "No documentation for: %s" % method
        return doc
        
class APIServer(xmlrpc.XMLRPC):
    #def __init__(self, papi):
    def __init__(self, papi):
        self.api = papi
        self.introspection = Introspection(self.api)
        xmlrpc.XMLRPC.__init__(self, allowNone = True)
        #self.logger = tomato.lib.log.Logger(tomato.config.LOG_DIR + "/api.log")

    #def log(self, function, args, user):
    #    if len(str(args)) < 50:
    #        self.logger.log("%s%s" % (function.__name__, args), user = user.name)
    #    else:
    #        self.logger.log(function.__name__, bigmessage = str(args) + 
    #                        "\n", user = user.name)

    def execute(self, function, args, user):
        try:
            #self.log(function, args, user)
            #return function(*(args[0]), user = user, **(args[1]))
            return function(*(args))
        except xmlrpc.Fault, exc:
            #fault.log(exc)
            raise exc
        except Exception, exc:
            #fault.log(exc)
            #self.logger.log("Exception: %s" % exc, user = user.name)
            #raise fault.wrap(exc)
            raise exc

    def render(self, request):
        username = request.getUser()
        passwd = request.getPassword()
        sign, user = dissomniagLive.getIdentity().authRPCUser(username, passwd) 
        if sign != dissomniagLive.LOGIN_SIGN.VALID_USER:
            request.setResponseCode(http.UNAUTHORIZED)
            if username == '' and passwd == '':
                return 'Authorization required!'
            else:
                return 'Authorization Failed!'
        request.content.seek(0, 0)
        args, functionPath = xmlrpclib.loads(request.content.read())
        function = None
        if hasattr(self.api, functionPath):
            function = getattr(self.api, functionPath)
        if functionPath.startswith("_"):
            functionPath = functionPath[1:]
        if hasattr(self.introspection, functionPath):
            function = getattr(self.introspection, functionPath)
        if function:
            request.setHeader("content-type", "text/xml")
            defer.maybeDeferred(self.execute, function, args, user).addErrback(self._ebRender).addCallback(self._cbRender, request)
            return server.NOT_DONE_YET
        
#===============================================================================
# End of Extraction
#===============================================================================

def startRPCServer():
    log.info("Starting RPC Server")
    api_server = APIServer(dissomniagLive.api)
    if dissomniagLive.config.SSL:
        log.info("Using SSL")
        sslContext = ssl.DefaultOpenSSLContextFactory(dissomniagLive.config.sslPrivateKey, dissomniagLive.config.sslCertFile)
        reactor.listenSSL(dissomniagLive.config.rpcServerPort, server.Site(api_server), contextFactory = sslContext) 
    else:
        reactor.listenTCP(dissomniagLive.config.rpcServerPort, server.Site(api_server))
        
    reactor.run()
