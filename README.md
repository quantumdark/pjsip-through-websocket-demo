# pjsip-through-websocket-demo
A small demo to demonstrate managing the softphone pjsua from javascript through a websocket 

# installation
0) optional: create virtualenv and activate it  
1) Build pjproject and pjsua-python module and install it  
2) git clone https://github.com/dpallot/simple-websocket-server.git  
3) install simple-websocket-server
4) install packages from req.txt

# How to try
0) Check websocketsip.conf
1) start the server ./websocketsip.py
2) open debug.html
3) Try commands, you'll see something like this:  

connected
response: {"jsonrpc": "2.0", "params": {"account": "{Account <sip:111@sip.zadarma.com>}"}, "method": "connected"}
sent:  {"jsonrpc": "2.0", "id": 3, "method": "make_call", "params": {"uri": "oflfd1223"}}
response: {"jsonrpc": "2.0", "id": 3, "error": {"message": "Invalid params", "code": -32602, "data": {"message": "make_call() got an unexpected keyword argument 'uri'", "args": ["make_call() got an unexpected keyword argument 'uri'"], "type": "TypeError"}}}
sent:  {"jsonrpc": "2.0", "id": 3, "method": "make_call", "params": {"sip_uri": "oflfd1223"}}
response: {"jsonrpc": "2.0", "id": 3, "error": {"message": "Server error", "code": -32000, "data": {"message": "global name 'uri' is not defined", "args": ["global name 'uri' is not defined"], "type": "NameError"}}}
sent:  {"jsonrpc": "2.0", "id": 4, "method": "hangup"}
response: {"jsonrpc": "2.0", "result": false, "id": 4}

