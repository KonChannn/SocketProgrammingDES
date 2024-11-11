import socketio
import eventlet
from eventlet import wsgi
from PKA.utils import *  # Assuming this contains the logic to generate server keys

sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Generate the server's public/private key pair
server_public_key, server_private_key = generate_key_pair()

# Store public keys for each client (by ID)
public_keys = {}

@sio.event
def connect(sid, environ):
    print(f'User connected: {sid}')
    sio.emit('message', {'msg': f'User {sid} has entered the chat!'}, to=sid)

@sio.event
def register_key(sid, data):
    # Store the client's public key
    public_key = data['public_key']
    public_keys[sid] = public_key
    sio.emit('registration_success', {'msg': f'Public key registered for {sid}'}, to=sid)

@sio.event
def request_key(sid, data):
    target_sid = data['target_id']
    if target_sid in public_keys:
        sio.emit('public_key', {'public_key': public_keys[target_sid]}, to=sid)
    else:
        sio.emit('public_key_error', {'msg': 'Target public key not found'}, to=sid)

@sio.event
def message(sid, data):
    try:
        encrypted_message = data['msg']
        print(f"Received encrypted message from {sid}: {encrypted_message}")
        print(f"Server private key: {server_private_key}")
        decrypted_message = decrypt_message(encrypted_message, server_private_key)
        print(f"Decrypted message: {decrypted_message}")
        sio.emit('message', {'msg': f'{sid}: {decrypted_message}'}, skip_sid=sid)
    except Exception as e:
        print(f"Error decrypting message: {e}")
        sio.emit('message', {'msg': 'Error decrypting message!'}, to=sid)


@sio.event
def disconnect(sid):
    print(f'User disconnected: {sid}')
    sio.emit('message', {'msg': f'User {sid} has left the chat.'})

# This event will handle sending the server's public key when requested
@sio.event
def get_server_public_key(sid, data):
    sio.emit('public_key', {'public_key': str(server_public_key)}, to=sid)


if __name__ == '__main__':
    print("Chat and PKA server started on http://localhost:5000")
    wsgi.server(eventlet.listen(('', 5000)), app)
