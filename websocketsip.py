#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import signal
import pjsua as pj
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket


# Logging callback
def log_cb(level, str, len):
    print str,

lib = None
acc = None

def signal_handler(signal, frame):
        global lib
        print('You pressed Ctrl+C!')
        # We're done, shutdown the library
        if lib:
            lib.destroy()
            lib = None
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

if len(sys.argv) < 4:
    print "Use: websocketsip.py <sipserver> <login> <password>"
    sys.exit(0)

try:
    lib = pj.Lib()
    # Init library with default config
    lib.init(log_cfg=pj.LogConfig(level=3, callback=log_cb))

    # Create UDP transport which listens to any available port
    lib.create_transport(pj.TransportType.UDP)

    # Start the library
    lib.start()

    # Create local/user-less account
    try:
        acc_cfg = pj.AccountConfig(sys.argv[1], sys.argv[2], sys.argv[3])
        acc = lib.create_account(acc_cfg)

    except pj.Error, err:
        print 'Error creating account:', err

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
    lib = None
    sys.exit(-1)


class MyCallCallback(pj.CallCallback):
    def __init__(self, websocket=None, call=None):
        self.websocket = websocket
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        s_text = self.call.info().state_text
        code = self.call.info().last_code
        reason = self.call.info().last_reason
        print "Call is ", s_text,
        print "last code =", code,
        print "(" + reason + ")"
        self.websocket.sendMessage(
            u'Call is {}, last code={} ({})'.format(s_text, code, reason))
        if s_text == 'DISCONNCTD':
            # nullify call istance to prevent lib from crash
            self.websocket.call = None

    # Notification when call's media state has changed.
    def on_media_state(self):
        global lib
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            lib.conf_connect(call_slot, 0)
            lib.conf_connect(0, call_slot)
            self.websocket.sendMessage(u"Hello world, I can talk!")
            print "Hello world, I can talk!"


class SimpleSip(WebSocket):

    call = None

    def make_call(self, uri):
        # Make call
        if self.call:
            print 'only one call supported'
            return
        print "calling ", uri, '...'
        if uri.startswith('sip:'):
            self.sendMessage(u"Calling {}...".format(self.data))
            self.call = acc.make_call(uri.encode(), MyCallCallback(self))
        else:
            self.sendMessage(u"Wrong SIP id {}.".format(uri))

    def hangup(self):
        print 'called hangup call'
        if self.call:
            self.call.hangup()
            self.call = None
        else:
            self.sendMessage(u"You have no call")

    def hold(self):
        print 'called hold call'
        if self.call:
            self.call.hold()
        else:
            self.sendMessage(u"You have no call")

    def unhold(self):
        print 'called unhold call'
        if self.call:
            self.call.unhold()
        else:
            self.sendMessage(u"You have no call")

    def mute_mic(self):
        print 'called mute mic call'
        if not self.lib:
            return
        try:
            tx_level, rx_level = self.lib.conf_get_signal_level(0)
            if rx_level > 0.0:
                self.lib.conf_set_rx_level(0, 0)
                levels = self.lib.conf_get_signal_level(0)
                self.sendMessage(u"Mic muted (level: {})".format(levels))
            else:
                self.lib.conf_set_rx_level(0, 1)
                levels = self.lib.conf_get_signal_level(0)
                self.sendMessage(u"Mic unmuted (level: {})".format(levels))
        except Exception as e:
            print e,

    def handleMessage(self):
        # commands in plain text like:
        # methodname first second ...
        # would be dispatched to self.methodname(first, second, ...)
        # e.g.: 'sum 3.1415 666' >>> self.sum(3.1415, 666)
        print self.address, self.data
        if not self.lib:
            self.sendMessage(u"Somethong wrong with SIP library")
        if self.acc:
            command = self.data.split()
            # dispatch comand to self method
            func = getattr(self, command[0], None)
            if func:
                func(*command[1:])
            else:
                self.sendMessage(u"Unknown function")
        else:
            self.sendMessage(u"Sip account not found")

    def handleConnected(self):
        # The Lib supports only one instance in memory
        global lib
        global acc
        self.lib = lib
        self.acc = acc
        self.sendMessage(u"Connected to server. SIP Account={}".format(acc))
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'


server = SimpleWebSocketServer('', 8000, SimpleSip)
server.serveforever()
