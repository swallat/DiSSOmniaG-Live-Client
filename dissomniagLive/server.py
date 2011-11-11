# -*- coding: utf-8 -*-
"""
Created on 06.10.2011

@author: Sebastian Wallat
"""

import socket
import socketserver
import ssl
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, SimpleXMLRPCRequestHandler
try:
    import fcntl
except ImportError:
    fcntl = None

from . import dissomniagLive

#    Easiest way to create the key file pair was to use OpenSSL -- http://openssl.org/ Windows binaries are available
#    You can create a self-signed certificate easily "openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout privatekey.pem"
#    for more information --  http://docs.python.org/library/ssl.html#ssl-certificates
   
class AsyncXMLRPCServerTLS(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
    def __init__(self, addr, requestHandler = SimpleXMLRPCRequestHandler,
                 logRequests = True, allow_none = False, encoding = None, bind_and_activate = True):
        """Overriding __init__ method of the SimpleXMLRPCServer

        The method is an exact copy, except the TCPServer __init__
        call, which is rewritten using TLS
        """
        self.logRequests = logRequests

        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding)

        """This is the modified part. Original code was:

            socketserver.TCPServer.__init__(self, addr, requestHandler, bind_and_activate)

        which executed:

            def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
                BaseServer.__init__(self, server_address, RequestHandlerClass)
                self.socket = socket.socket(self.address_family,
                                            self.socket_type)
                if bind_and_activate:
                    self.server_bind()
                    self.server_activate()

        """
        class VerifyingRequestHandler(SimpleXMLRPCRequestHandler):
            '''
            Request Handler that verifies username and password passed to
            XML RPC server in HTTP URL sent by client.
            '''
            # this is the method we must override
            def parse_request(self):
                # first, call the original implementation which returns
                # True if all OK so far
                if SimpleXMLRPCRequestHandler.parse_request(self):
                    # next we authenticate
                    if self.authenticate(self.headers):
                        return True
                    else:
                        # if authentication fails, tell the client
                        self.send_error(401, 'Authentication failed')
                return False
           
            def authenticate(self, headers):
                from base64 import b64decode
                #    Confirm that Authorization header is set to Basic
                (basic, _, encoded) = headers.get('Authorization').partition(' ')
                assert basic == 'Basic', 'Only basic authentication supported'
               
                #    Encoded portion of the header is a string
                #    Need to convert to bytestring
                encodedByteString = encoded.encode()
                #    Decode Base64 byte String to a decoded Byte String
                decodedBytes = b64decode(encodedByteString)
                #    Convert from byte string to a regular String
                decodedString = decodedBytes.decode()
                #    Get the username and password from the string
                (username, _, password) = decodedString.partition(':')
                #    Check that username and password match internal global dictionary
                if dissomniagLive.getIdentity().authServer(username, password):
                    return True
                else:
                    return False
       
        #    Override the normal socket methods with an SSL socket
        socketserver.BaseServer.__init__(self, addr, VerifyingRequestHandler)
        self.socket = ssl.wrap_socket(
            socket.socket(self.address_family, self.socket_type),
            server_side = True,
            keyfile = dissomniagLive.config.sslPrivateKey,
            certfile = dissomniagLive.config.sslCertFile,
            cert_reqs = ssl.CERT_NONE,
            ssl_version = ssl.PROTOCOL_SSLv23,
            )
        if bind_and_activate:
            self.server_bind()
            self.server_activate()

        """End of modified part"""

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

def startRpcServer():
    # Create server
    server = AsyncXMLRPCServerTLS(("0.0.0.0", dissomniagLive.config.localRpcServerPort), requestHandler = RequestHandler)
    server.register_introspection_functions()

    server.register_instance(dissomniagLive.api.ApiProvider())

    # Run the server's main loop
    print("Starting XML RPC Server")
    server.serve_forever()
    dissomniagLive.getIdentity().cleanUp()
