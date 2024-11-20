import socketio
from DES.des import encryption, decryption
from DES.util import pad_string, remove_padding
from PKA.utils import generate_key_pair, encrypt_message, decrypt_message
import secrets
import threading

class SecureChatClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.public_key, self.private_key = generate_key_pair()
        self.des_key = secrets.token_hex(8)  # Generate random DES key
        self.server_public_key = None
        self.chat_ready = False
        self.setup_events()

    def setup_events(self):
        @self.sio.event
        def connect():
            print("Connected to server!")
            # Register our public key
            self.sio.emit('register_key', {'public_key': str(self.public_key)})

        @self.sio.event
        def server_public_key(data):
            self.server_public_key = eval(data['public_key'])
            print("Received server public key")
            # Encrypt DES key with server's public key and send it
            encrypted_des_key = encrypt_message(self.des_key, self.server_public_key)
            self.sio.emit('submit_des_key', {'encrypted_des_key': encrypted_des_key})
            print("DES key submitted to server")
            # Start the chat immediately after submitting DES key
            self.chat_ready = True
            self.start_chat()

        @self.sio.event
        def receive_des_key(data):
            encrypted_des_key = data['encrypted_des_key']
            from_sid = data['from_sid']
            # Decrypt DES key using our private key
            self.des_key = decrypt_message(encrypted_des_key, self.private_key)
            print(f"Received new DES key from user {from_sid}")
            if not self.chat_ready:
                self.chat_ready = True
                self.start_chat()

        @self.sio.event
        def message(data):
            try:
                if ':' in data['msg']:
                    sender, encrypted_msg = data['msg'].split(':', 1)
                    # Only decrypt messages from others
                    if sender.strip() != self.sio.get_sid():
                        decrypted_msg = decryption(encrypted_msg.strip(), self.des_key)
                        unpadded_msg = remove_padding(decrypted_msg)
                        print(f"\n{sender}: {unpadded_msg}")
                        print("> ", end='', flush=True)  # Reprint the prompt
            except Exception as e:
                print(f"Error processing message: {e}")

    def send_message(self, message):
        try:
            padded_msg = pad_string(message)
            encrypted_msg = encryption(padded_msg, self.des_key)
            self.sio.emit('message', {'msg': encrypted_msg})
        except Exception as e:
            print(f"Error sending message: {e}")

    def start_chat(self):
        print("\nChat is ready! Type your messages (type 'exit' to quit):")
        while True:
            try:
                message = input("> ")
                if message.lower() == 'exit':
                    self.sio.disconnect()
                    break
                self.send_message(message)
            except KeyboardInterrupt:
                print("\nExiting chat...")
                self.sio.disconnect()
                break
            except Exception as e:
                print(f"Error in chat: {e}")

    def connect_to_server(self, server_url='http://localhost:5000'):
        try:
            self.sio.connect(server_url)
            self.sio.wait()
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == '__main__':
    client = SecureChatClient()
    client.connect_to_server()