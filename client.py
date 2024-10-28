import socket
import threading
from DES.des import *  # Import fungsi enkripsi dan dekripsi dari implementasi DES Anda

KEY = "12345678"  # Hardcoded DES key

def receive_messages(client_socket):
    while True:
        try:
            encrypted_data = client_socket.recv(1024)
            if encrypted_data:
                decrypted_text = decryption(ciphertext, KEY)
                print(f"Client1 menerima (didekripsi): {decrypted_message}")
        except Exception as e:
            print(f"Error: {e}")
            break

def send_messages(client_socket):
    while True:
        message = input("Client1 ketik pesan: ")
        padded_plaintext = pad_string(message)  # Pad pesan sebelum enkripsi
        encrypted_data = encryption(padded_plaintext, KEY)
        print(encrypted_data)
        client_socket.sendall(encrypted_data)

def start_client1():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9999))

    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    threading.Thread(target=send_messages, args=(client_socket,)).start()

if __name__ == "__main__":
    start_client1()
