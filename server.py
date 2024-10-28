import socket
import threading

def relay_messages(sender_conn, receiver_conn, sender_name):
    while True:
        try:
            data = sender_conn.recv(1024)  # Menerima pesan dari pengirim
            if not data:
                print(f"{sender_name} terputus.")
                break  # Jika tidak ada data, berarti client terputus

            print(f"{sender_name} mengirim data terenkripsi: {data.decode('utf-8')}")
            receiver_conn.sendall(data)  # Mengirimkan data ke penerima

        except ConnectionResetError:
            print(f"ConnectionResetError: {sender_name} terputus secara tiba-tiba.")
            break
        except Exception as e:
            print(f"Error saat relay pesan dari {sender_name}: {e}")
            break

    # Pembersihan setelah client terputus
    sender_conn.close()
    receiver_conn.close()
    print(f"Koneksi {sender_name} telah ditutup.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(2)
    print("Server siap menerima koneksi dari client1 dan client2...")

    client1_conn, _ = server_socket.accept()
    print("Client1 terhubung.")
    
    client2_conn, _ = server_socket.accept()
    print("Client2 terhubung.")

    # Buat thread untuk meneruskan pesan antara kedua klien
    threading.Thread(target=relay_messages, args=(client1_conn, client2_conn, "Client1")).start()
    threading.Thread(target=relay_messages, args=(client2_conn, client1_conn, "Client2")).start()

if __name__ == "__main__":
    start_server()
