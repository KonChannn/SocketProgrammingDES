import socketio
from DES.des import encryption, decryption
from DES.util import pad_string, remove_padding
from PKA.utils import generate_key_pair, encrypt_message, sign_data
import secrets

sio = socketio.Client()
ENCRYPTION_KEY = '12345678'  

# Generate key pair
public_key, private_key = generate_key_pair()

# Define the global target_public_key and target_sid
target_public_key = None
target_sid = None

@sio.event
def connect():
    print("Connected to the PKA and Chat server!")
    public_key_str = str(public_key) 
    sio.emit('register_key', {'public_key': public_key_str})
    
    # Request the server's public key
    sio.emit('get_server_public_key', {})

    # Request public key of another client (example: Client 2)
    if target_sid:
        sio.emit('request_key', {'target_id': target_sid})

@sio.event
def public_key(data):
    global target_public_key
    # Server has sent the public key
    target_public_key = eval(data['public_key'])
    
    # Encrypt and send the session key to the server
    encrypted_session_key = encrypt_message(str(ENCRYPTION_KEY), target_public_key)
    sio.emit('session_key', {'key': encrypted_session_key}) 

    print("Session key securely sent to server. Ready to send messages.")
    send_messages()

@sio.event
def get_server_public_key(data):
    print(f"Received server public key: {data['public_key']}")
    # This part is unnecessary if not sending a DES key to another client

@sio.event
def message(data):
    try:
        message_received = data['msg']
        if ':' in message_received:
            sender, msg = message_received.split(':', 1)
            stripped_msg = msg.strip()
            print(f"{sender}: {remove_padding(stripped_msg)}")
    except Exception as e:
        print(f"Error decrypting message: {e}")

def send_messages():
    print("Type your messages below. Type 'exit' to leave the chat.")
    while True:
        msg = input("> ")
        if msg.lower() == 'exit':
            sio.disconnect()
            break
        try:
            padded_string = pad_string(msg)
            encrypted_msg = encryption(padded_string, ENCRYPTION_KEY)
            print(f"Encrypted message: {encrypted_msg}")
            sio.emit('message', {'msg': encrypted_msg})
        except Exception as e:
            print(f"Error encrypting message: {e}")

if __name__ == '__main__':
    sio.connect('http://localhost:5000') 
    sio.wait()
