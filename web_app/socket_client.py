import socket
import time

# Number of connections you want to test
num_connections = 1

def create_connection():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_socket.connect(('104.21.80.1', '443'))
        # file_data = client_socket.recv(1024 * 1024)  
        # print(f"Received data: {file_data}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Connection closed")

def test_connections():
    for i in range(num_connections):
        print(f"Connecting to the server - Connection {i + 1}")
        create_connection()
        time.sleep(1)  


if __name__ == "__main__":
    test_connections()
