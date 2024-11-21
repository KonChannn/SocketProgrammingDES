import socketio
from DES.des import encryption, decryption
from DES.util import pad_string, remove_padding
from PKA.utils import generate_key_pair, encrypt_message, decrypt_message
import os

class SecureChatClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.public_key, self.private_key = generate_key_pair()
        self.des_key = None
        self.other_clients_public_keys = {}
        self.chat_ready = False
        self.is_key_generator = False 
        self.setup_events()

    def setup_events(self):
        @self.sio.event
        def connect():
            print("Connected to server!")
            # Register our public key
            self.sio.emit('register_key', {'public_key': str(self.public_key)})

        @self.sio.event
        def distribute_public_keys(data):
            # Receive public keys from server
            self.other_clients_public_keys.update(data['public_keys'])
            print("Received public keys:")
            for sid, public_key in self.other_clients_public_keys.items():
                print(f"Client {sid}: {public_key}")
            
            # Determine if this client should generate the DES key
            if self.other_clients_public_keys:
                lowest_sid = min(list(self.other_clients_public_keys.keys()) + [self.sio.get_sid()])
                
                # If this client has the lowest SID, generate and send the DES key
                if lowest_sid == self.sio.get_sid():
                    # Generate exactly 8 random bytes for DES key
                    self.des_key = os.urandom(8).hex()  # 8 bytes converted to hex
                    self.is_key_generator = True
                    self.chat_ready = True  # Allow immediate chat for key generator
                    
                    # Send DES key to the other client
                    target_sid = [sid for sid in self.other_clients_public_keys.keys() if sid != lowest_sid][0]
                    self.send_des_key_to_client(target_sid)
                    
                    # Start chat for the key generator client
                    self.start_chat()

        @self.sio.event
        def receive_encrypted_des_key(data):
            if self.des_key:
                return  # Prevent duplicate key processing
            
            encrypted_des_key = data['encrypted_des_key']
            from_sid = data['from_sid']
            try:
                # Decrypt DES key using our private key
                decrypted_des_key = decrypt_message(encrypted_des_key, self.private_key)
                print(f"Received DES key from {from_sid}")
                
                # Set the DES key
                self.des_key = decrypted_des_key
                self.chat_ready = True
                self.start_chat()
            except Exception as e:
                print(f"Error decrypting DES key: {e}")

        @self.sio.event
        def message(data):
            if not self.des_key:
                print("Waiting for DES key exchange...")
                return
            
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

    def send_des_key_to_client(self, target_sid):
        # Encrypt DES key with target client's public key
        public_key = eval(self.other_clients_public_keys[target_sid])
        encrypted_des_key = encrypt_message(self.des_key, public_key)
        
        # Send encrypted DES key to server to relay
        self.sio.emit('relay_encrypted_des_key', {
            'target_sid': target_sid,
            'encrypted_des_key': encrypted_des_key
        })
        print(f"Sent DES key to client {target_sid}")

    def send_message(self, message):
        if not self.chat_ready:
            print("Chat is not ready. Waiting for DES key exchange.")
            return

        try:
            padded_msg = pad_string(message)
            encrypted_msg = encryption(padded_msg, self.des_key)
            self.sio.emit('message', {'msg': encrypted_msg})
        except Exception as e:
            print(f"Error sending message: {e}")

    def start_chat(self):
        print("\nChat is ready!")
        print("Type your messages (type 'exit' to quit)")

        while self.chat_ready:
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