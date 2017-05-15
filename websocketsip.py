#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import ConfigParser as cf
import signal
import pjsua as pj
import logging
import logging.config
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from jsonrpc import JSONRPCResponseManager, dispatcher
from jsonrpc.jsonrpc2 import JSONRPC20Request

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('wssip')


CONFIGFILE = 'websocketsip.conf'




try:
    config = cf.ConfigParser()
    config.readfp(open(CONFIGFILE))
    config.read(['site.cfg', os.path.expanduser('~/.myapp.cfg')])
except IOError:
    logger.error('Failed to load config file: %s' % CONFIGFILE)
    sys.exit(-1)
try:
    server = config.get('SIP', 'server')
    login = config.get('SIP', 'login')
    password = config.get('SIP', 'password')
    sockethost = config.get('WEBSOCKET', 'host')
    if sockethost == '*':
        sockethost = ''
    socketport = config.getint('WEBSOCKET', 'port')
except cf.NoOptionError as e:
    logger.error(e)
    sys.exit(-1)
except cf.NoSectionError as e:
    logger.error(e)
    sys.exit(-1)
except Exception as e:
    logger.exception(e)
    sys.exit(-1)

lib = None
acc = None

# Logging callback
def log_cb(level, str, len):
    logger.info(str)

def signal_handler(signal, frame):
        global lib
        logger.info('You pressed Ctrl+C!')
        # We're done, shutdown the library
        if lib:
            lib.destroy()
            lib = None
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


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
        acc_cfg = pj.AccountConfig(server, login, password)
        acc = lib.create_account(acc_cfg)

    except pj.Error, err:
        logger.info('Error creating account: %s', err)

except pj.Error, e:
    logger.error("Exception: %s", str(e))
    lib.destroy()
    lib = None
    sys.exit(-1)


class MyCallCallback(pj.CallCallback):
    """
    Call state variations.
    NULL            -- call is not initialized.
    CALLING         -- initial INVITE is sent.
    INCOMING        -- initial INVITE is received.
    EARLY           -- provisional response has been sent or received.
    CONNECTING      -- 200/OK response has been sent or received.
    CONFIRMED       -- ACK has been sent or received.
    DISCONNECTED    -- call is disconnected.

    Call media state variations.
    NULL        -- media is not available.
    ACTIVE      -- media is active.
    LOCAL_HOLD  -- media is put on-hold by local party.
    REMOTE_HOLD -- media is put on-hold by remote party.
    ERROR       -- media error (e.g. ICE negotiation failure).
    """
    media_state = {
        pj.MediaState.NULL: 'not_available',
        pj.MediaState.ACTIVE: 'active',
        pj.MediaState.LOCAL_HOLD: 'local_hold',
        pj.MediaState.REMOTE_HOLD: 'remote_hold',
        pj.MediaState.ERROR: 'error',
    }
    def __init__(self, websocket=None, call=None):
        self.websocket = websocket
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        s_text = self.call.info().state_text
        code = self.call.info().last_code
        reason = self.call.info().last_reason
        media_state = self.media_state.get(
                     self.call.info().media_state,
                     'unknown'
                 )
        notify20(self.websocket, 'call_status_update', 
                 {'status': s_text,
                  'code': code,
                  'reason': reason,
                  'media_state': media_state})
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
            s_text = self.call.info().state_text
            code = self.call.info().last_code
            reason = self.call.info().last_reason
            media_state = self.media_state.get(
                         self.call.info().media_state,
                         'unknown'
                     )
            notify20(self.websocket, 'call_media_state_update', 
                     {'status': s_text,
                      'code': code,
                      'reason': reason,
                      'media_state': media_state})


def notify20(websocket, method, params=None):
    # Sending notifications to the clients helper function
    try:
        notification = unicode(
            JSONRPC20Request(method, params, is_notification=True).json,
            'utf-8')
        logger.info("Sending notification: %r", notification)
        websocket.sendMessage(notification)
    except Exception as e:
        logger.exception(e)


class Dispatcher:

    call = None

    def __init__(self, websocket):
        global lib
        global acc
        self.lib = lib
        self.acc = acc
        self.websocket = websocket

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError

    def make_call(self, sip_uri):
        logger.debug('called make_call method')
        # Make call
        if self.call:
            logger.info('only one call supported')
            return
        logger.info("calling %s...", uri)
        if uri.startswith('sip:'):
            self.call = acc.make_call(
                uri.encode(),
                MyCallCallback(self.websocket))
            return True
        else:
            raise ValueError("Wrong SIP id {}.".format(uri))

    def hangup(self):
        logger.debug('called hangup method')
        if self.call:
            self.call.hangup()
            self.call = None
            return True
        else:
            return False

    def hold(self):
        logger.debug('called hold method')
        if self.call:
            self.call.hold()
            return True
        else:
            return False

    def unhold(self):
        logger.debug('called unhold method')
        if self.call:
            self.call.unhold()
            return True
        else:
            return False

    def mute_mic(self):
        logger.debug('called mute_mic method')
        if not self.lib:
            return
        tx_level, rx_level = self.lib.conf_get_signal_level(0)
        if rx_level > 0.0:
            self.lib.conf_set_rx_level(0, 0)
            levels = self.lib.conf_get_signal_level(0)
            return levels
        else:
            self.lib.conf_set_rx_level(0, 1)
            levels = self.lib.conf_get_signal_level(0)
            return levels

    def enum_devices(self):
        return ["%s <in: %s, out: %s>" % (dev.name,
                                          dev.input_channels,
                                          dev.output_channels
                                          ) for dev in self.lib.enum_snd_dev()]

    def get_current_devices(self):
        return self.lib.get_snd_dev()

    def set_current_devices(self, capture_dev, playback_dev):
        return self.lib.set_snd_dev(capture_dev, playback_dev)


class WebSocketSip(WebSocket):

    def handleMessage(self):
        logger.debug("Reseived from %s data: %s", self.address, self.data)
        # dispatch comand
        try:
            response = JSONRPCResponseManager.handle(self.data, self.dispatcher)
        except Exception as e:
            logger.exception(e)
        if response is not None:
            logger.info("Request: %r, Response: %r",
                        self.data,
                        unicode(response.json, 'utf-8'))
            self.sendMessage(unicode(response.json, 'utf-8'))
        else:
            logger.info("Notification received: %r", self.data)

    def handleConnected(self):
        # The Lib supports only one instance in memory
        self.dispatcher = Dispatcher(self)
        notify20(self, 'connected', {'account': str(acc)})
        logger.info('Connected: %s', self.address)

    def handleClose(self):
        logger.info('Connection closed: %s', self.address)


server = SimpleWebSocketServer(sockethost, socketport, WebSocketSip)
server.serveforever()
