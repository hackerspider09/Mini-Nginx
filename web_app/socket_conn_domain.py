import socket

def send_http_request(host, path):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        port = 80 
        client_socket.connect((host, int(port)))

        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        client_socket.sendall(request.encode())

        response = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            response += chunk

        print(response.decode())

    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    host = "jsonplaceholder.typicode.com"
    path = "/todos/"
    send_http_request(host, path)