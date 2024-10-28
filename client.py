import socketio
import threading
import json
import base64
from DES.des import encryption, decryption
from DES.util import pad_string,remove_padding

# Connect to the Socket.IO server
sio = socketio.Client()
ENCRYPTION_KEY = "29102842"  # DES keys should be exactly 8 bytes

def listen_for_messages():
    @sio.event
    def message(data):
        try:
            message_received = data['msg']
            print (f"Received message: {message_received}")
            if ':' in message_received:
                sender, msg = message_received.split(':',1)
                stripped_msg = msg.strip()
                decrypted_msg = decryption(stripped_msg, ENCRYPTION_KEY)
                print(f"Message from {sender}: {remove_padding(decrypted_msg)}")

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

# Connect to the server
@sio.event
def connect():
    print("Connected to the chat server!")
    threading.Thread(target=send_messages).start()

# Disconnect from the server
@sio.event
def disconnect():
    print("Disconnected from the chat server.")

# Connect and start listening
if __name__ == '__main__':
    listen_for_messages()
    sio.connect('http://localhost:5000')
    sio.wait()
