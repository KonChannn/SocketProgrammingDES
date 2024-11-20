
import socketio
import eventlet
from eventlet import wsgi
from PKA.utils import generate_key_pair, encrypt_message, decrypt_message

sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Generate the server's public/private key pair
server_public_key, server_private_key = generate_key_pair()

# Store client information
clients = {}  # Dictionary to store client public keys and encrypted DES keys

@sio.event
def connect(sid, environ):
    print(f'User connected: {sid}')
    clients[sid] = {'public_key': None, 'encrypted_des_key': None}
    sio.emit('message', {'msg': f'User {sid} has entered the chat!'})

@sio.event
def register_key(sid, data):
    # Store the client's public key
    public_key = eval(data['public_key'])  # Convert string representation back to key
    clients[sid]['public_key'] = public_key
    print(f"Registered public key for client {sid}")
    # Send server's public key back to client
    sio.emit('server_public_key', {'public_key': str(server_public_key)}, to=sid)

@sio.event
def submit_des_key(sid, data):
    # Receive encrypted DES key from client
    encrypted_des_key = data['encrypted_des_key']
    clients[sid]['encrypted_des_key'] = encrypted_des_key
    
    # Decrypt DES key using server's private key
    des_key = decrypt_message(encrypted_des_key, server_private_key)
    print(f"Received and decrypted DES key from client {sid}")
    
    # Re-encrypt DES key with each other client's public key and distribute
    for other_sid, other_client in clients.items():
        if other_sid != sid and other_client['public_key']:
            encrypted_des_key_for_other = encrypt_message(des_key, other_client['public_key'])
            sio.emit('receive_des_key', {
                'encrypted_des_key': encrypted_des_key_for_other,
                'from_sid': sid
            }, to=other_sid)

@sio.event
def message(sid, data):
    # Server just relays the encrypted message without decrypting
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