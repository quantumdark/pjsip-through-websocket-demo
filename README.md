# pjsip-through-websocket-demo
A small demo to demonstrate managing the softphone pjsua from javascript through a websocket 

# installation
0) optional: create virtualenv and activate it  
1) Build pjproject and pjsua-python module and install it  
2) git clone https://github.com/dpallot/simple-websocket-server.git  
3) install simple-websocket-server

# How to try
1) start the server ./websocketsip.py <sipserver> <login> <password>
2) open websocket.html from the project simple-websocket-server  
3) Try commands, you'll see something like this:  
  
response: Connected to server. SIP Account={Account <sip:1111111@sip.------.com>}  
sent: make_call sip:111111111111@sip.------.com  
response: Calling make_call sip:111111111111@sip.------.com...  
response: Call is CALLING, last code=0 ()  
response: Call is EARLY, last code=183 (Session Progress)  
response: Hello world, I can talk!  
response: Call is EARLY, last code=180 (Ringing)  
response: Call is CONNECTING, last code=200 (OK)  
response: Call is CONFIRMED, last code=200 (OK)  
response: Hello world, I can talk!  
sent: hold  
response: Call is DISCONNCTD, last code=200 (Normal call clearing)  
sent: hold  
response: You have no call  
sent: make_call sip:111111111111@sip.------.com  
response: Calling make_call sip:111111111111@sip.------.com...  
response: Call is CALLING, last code=0 ()  
response: Call is EARLY, last code=183 (Session Progress)  
response: Hello world, I can talk!  
response: Call is EARLY, last code=180 (Ringing)  
response: Call is CONNECTING, last code=200 (OK)  
response: Call is CONFIRMED, last code=200 (OK)  
response: Hello world, I can talk!  
sent: hangup  
response: Call is DISCONNCTD, last code=603 ()  
disconnected  
