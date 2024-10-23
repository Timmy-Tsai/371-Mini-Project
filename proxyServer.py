import socket
import threading

# Define the host and port for the proxy server
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8888  # Proxy server running on port 8888

# Create a socket object for the proxy server
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
try:
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
except socket.error as e:
    print(f"Error binding to port {PROXY_PORT}: {e}")
    exit(1)

# Listen for incoming connections
proxy_socket.listen(5)
print(f"Proxy server is listening on {PROXY_HOST}:{PROXY_PORT}")

# Function to handle proxy behavior and interact with the web server
def proxy_server(client_socket):
    try:
        # Receive the client's request
        request = client_socket.recv(1024)
        print(f"Proxy received request:\n{request.decode('utf-8')}")

        # Connect to the local web server (127.0.0.1:8080)
        web_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        web_server_host = '127.0.0.1'
        web_server_port = 8080
        
        try:
            # Forward the request to the web server
            web_server_socket.connect((web_server_host, web_server_port))
            web_server_socket.sendall(request)
            print(f"Forwarded request to web server at {web_server_host}:{web_server_port}")

            # Receive the response from the web server
            web_server_response = web_server_socket.recv(4096)
            print(f"Received response from web server")

            # Forward the response back to the client
            client_socket.sendall(web_server_response)
            print("Forwarded web server's response back to client")
        
        except socket.error as e:
            print(f"Error connecting to web server: {e}")
            response = "HTTP/1.1 502 Bad Gateway\r\n\r\n"
            client_socket.sendall(response.encode('utf-8'))
        
        finally:
            web_server_socket.close()

    except Exception as e:
        print(f"Error handling proxy request: {e}")
    finally:
        client_socket.close()

# Main server loop to accept and handle client requests
while True:
    client_socket, client_address = proxy_socket.accept()
    print(f"Connection established with {client_address}")
    proxy_thread = threading.Thread(target=proxy_server, args=(client_socket,))
    proxy_thread.start()