import socketio
import eventlet
from eventlet import wsgi
from PKA.utils import generate_key_pair, decrypt_message  # Assuming this contains the logic to generate server keys
from DES.des import decryption  # Import your DES decryption function

sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Generate the server's public/private key pair
server_public_key, server_private_key = generate_key_pair()

# Store public keys for each client (by ID)
public_keys = {}  # This will hold the DES keys as well

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
        des_key = public_keys.get(sid)  # Retrieve the stored DES key for this sid

        if des_key is None:
            raise ValueError("DES key not found for this client session.")
        
        decrypted_message = decryption(encrypted_message, des_key)
        print(f"Decrypted message from {sid}: {decrypted_message}")
        
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

@sio.event
def session_key(sid, data):
    try:
        encrypted_key = data['key']
        # Decrypt the DES key with the server's private key
        decrypted_key = decrypt_message(encrypted_key, server_private_key)
        print(f"Received and decrypted session key from {sid}: {decrypted_key}")

        # Store the decrypted DES key for this sid
        public_keys[sid] = decrypted_key
    except Exception as e:
        print(f"Error processing session key from {sid}: {e}")

if __name__ == '__main__':
    print("Chat and PKA server started on http://localhost:5000")
    wsgi.server(eventlet.listen(('', 5000)), app)
