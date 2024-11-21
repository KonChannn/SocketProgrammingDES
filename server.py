import socketio
import eventlet
from eventlet import wsgi

sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Store client information
clients = {}  # Dictionary to store client public keys

@sio.event
def connect(sid, environ):
    print(f'User connected: {sid}')
    clients[sid] = {'public_key': None}
    sio.emit('message', {'msg': f'User {sid} has entered the chat!'})

@sio.event
def register_key(sid, data):
    # Store the client's public key
    public_key = eval(data['public_key'])  # Convert string representation back to key
    clients[sid]['public_key'] = public_key
    print(f"Registered public key for client {sid}")
    
    # If more than one client has registered, distribute keys
    registered_clients = [
        other_sid for other_sid, client_info in clients.items() 
        if client_info['public_key'] is not None
    ]
    
    if len(registered_clients) > 1:
        # Distribute all public keys to all clients
        for target_sid in registered_clients:
            other_keys = {
                other_sid: str(client_info['public_key']) 
                for other_sid, client_info in clients.items() 
                if other_sid != target_sid and client_info['public_key'] is not None
            }
            sio.emit('distribute_public_keys', {'public_keys': other_keys}, to=target_sid)

@sio.event
def relay_encrypted_des_key(sid, data):
    # Simply relay the encrypted DES key to the target client
    target_sid = data['target_sid']
    encrypted_des_key = data['encrypted_des_key']
    sio.emit('receive_encrypted_des_key', {
        'encrypted_des_key': encrypted_des_key,
        'from_sid': sid
    }, to=target_sid)

@sio.event
def message(sid, data):
    # Server just relays the encrypted message
    encrypted_message = data['msg']
    sio.emit('message', {'msg': f'{sid}: {encrypted_message}'}, skip_sid=sid)

@sio.event
def disconnect(sid):
    if sid in clients:
        del clients[sid]
    print(f'User disconnected: {sid}')
    sio.emit('message', {'msg': f'User {sid} has left the chat.'})

if __name__ == '__main__':
    print("Secure chat server started on http://localhost:5000")
    wsgi.server(eventlet.listen(('', 5000)), app)