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

# Calls
response: {"jsonrpc": "2.0", "params": {"account": "{Account <sip:111@sip.zadarma.com>}"}, "method": "connected"}

sent:  {"jsonrpc": "2.0", "id": 3, "method": "make_call", "params": {"uri": "oflfd1223"}}

response: {"jsonrpc": "2.0", "id": 3, "error": {"message": "Invalid params", "code": -32602, "data": {"message": "make_call() got an unexpected keyword argument 'uri'", "args": ["make_call() got an unexpected keyword argument 'uri'"], "type": "TypeError"}}}

sent:  {"jsonrpc": "2.0", "id": 3, "method": "make_call", "params": {"sip_uri": "oflfd1223"}}

response: {"jsonrpc": "2.0", "id": 3, "error": {"message": "Server error", "code": -32000, "data": {"message": "Wrong SIP id oflfd1223.", "args": ["Wrong SIP id oflfd1223."], "type": "ValueError"}}}

sent:  {"jsonrpc": "2.0", "id": 4, "method": "hangup"}

response: {"jsonrpc": "2.0", "result": false, "id": 4}

# Device management
sent: {"method": "enum_devices", "id": 1, "jsonrpc": "2.0"}

response: {"jsonrpc": "2.0", "result": ["HDA Intel PCH: CX8200 Analog (hw:0,0) <in: 2, out: 2>", "HDA Intel PCH: HDMI 0 (hw:0,3) <in: 0, out: 8>", "HDA Intel PCH: HDMI 1 (hw:0,7) <in: 0, out: 8>", "HDA Intel PCH: HDMI 2 (hw:0,8) <in: 0, out: 8>", "sysdefault <in: 128, out: 128>", "front <in: 0, out: 2>", "surround40 <in: 0, out: 2>", "surround51 <in: 0, out: 2>", "surround71 <in: 0, out: 2>", "hdmi <in: 0, out: 8>", "pulse <in: 32, out: 32>", "dmix <in: 0, out: 2>", "default <in: 32, out: 32>"], "id": 1}

sent: {"method": "set_current_devices", "params": [10, 10], "id": 1, "jsonrpc": "2.0"}

response: {"jsonrpc": "2.0", "result": null, "id": 1}

sent: {"method": "set_current_devices", "params": [12, 12], "id": 1, "jsonrpc": "2.0"}

response: {"jsonrpc": "2.0", "result": null, "id": 1}

sent: {"method": "get_current_devices", "id": 1, "jsonrpc": "2.0"}

response: {"jsonrpc": "2.0", "result": [12, 12], "id": 1}
