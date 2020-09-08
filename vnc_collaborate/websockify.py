# A customized version of websockify that uses the websockify library,
# but replaces one method call to allow VNC Websocket connections
# to be relayed to different destinations based on the path
# specified in the URL, which should be a username on the system.
#
# We squash spaces to allow "Charlie Clown" to map to the UNIX user
# "CharlieClown".
#
# We search the .vnc/*.pid files and the system process table to find
# VNC a server that matches the username, otherwise we fall back to
# the server and port specified on the command line as a default.
#
# On Ubuntu 16, need to install with --no-deps:
#   sudo -H pip3 install --no-deps -U websockify
# websockify would like numpy, but PyPI numpy can't run on Python less than 3.6

import sys
import psutil
import glob

# Warning are explicitly disabled here, otherwise we'll get a
#   "no 'numpy' module, HyBi protocol will be slower"
# every time we import vnc_collaborate for anything.

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from websockify import websocketproxy

from websockify.websocketproxy import ProxyRequestHandler

old_new_websocket_client = ProxyRequestHandler.new_websocket_client

def new_websocket_client(self):
    try:
        userID = self.path.split('/')[1].split('?')[0]
    except:
        userID = ''
        pass

    displays = []
    for fn in glob.glob('/home/{}/.vnc/*.pid'.format(userID.replace(' ', '').replace('%20',''))):
        with open(fn) as f:
            pid = int(f.read())
            try:
                p = psutil.Process(pid)
                if 'vnc' in p.cmdline()[0]:
                    displays.append(fn.split('/')[-1].strip('.pid'))
            except psutil.NoSuchProcess:
                pass
    if len(displays) > 0:
        (target_host, target_display) = displays[0].split(':')
        self.server.target_host = target_host
        self.server.target_port = 5900 + int(target_display)

    # pass through to the "parent" class's version of this method
    old_new_websocket_client(self)

ProxyRequestHandler.new_websocket_client = new_websocket_client

def websockify():
    if sys.argv[0] != 'websockify':
        sys.argv.pop(0)

    # This will call WebSocketProxy; its default RequestHandlerClass
    # is ProxyRequestHandler, but we can't override
    # RequestHandlerClass at this point, so we settle for changing the
    # method inside ProxyRequestHandler.

    websocketproxy.websockify_init()