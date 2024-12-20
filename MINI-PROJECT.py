#MINI PROJECT
#Author Timmy Tsai 301456611
#

import socket
import threading
import os
import time
from email.utils import formatdate, parsedate_to_datetime

# Define the host and port number
HOST = '127.0.0.1'
PORT = 8080

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
try:
    server_socket.bind((HOST, PORT))
except socket.error as e:
    print(f"Error binding to port {PORT}: {e}")
    exit(1)

# Listen for incoming connections
server_socket.listen(5)
print(f"Server is listening on {HOST}:{PORT}")

def handle_request(client_connection):
    try:
        request = client_connection.recv(1024).decode('utf-8')
        print(f"Request received:\n{request}")

        request_lines = request.splitlines()
        if request_lines:
            print(f"Request line: {request_lines[0]}")
            try:
                method, path, _ = request_lines[0].split()
                print(f"Method received: {method} | Path: {path}")
            except ValueError:
                print("Request parsing failed: Malformed request.")
                print(" Status: 400 Bad Request") 
                status_code = "400 Bad Request"
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"
                client_connection.sendall(response.encode('utf-8'))
                return

            # Check for the If-Modified-Since header
            if_modified_since = None
            for line in request_lines[1:]:
                if line.startswith('If-Modified-Since'):
                    if_modified_since = line.split(":", 1)[1].strip()
                    print(f"If-Modified-Since: {if_modified_since}")
                    break

            supported_methods = ['GET']
            if method not in supported_methods:
                status_code = "501 Not Implemented"
                response = "HTTP/1.1 501 Not Implemented\r\n\r\n"
            elif method == 'GET':
                if path == '/test.html':
                    try:
                        # Get the last modified time of the file
                        last_modified = os.path.getmtime('test.html')
                        last_modified_str = formatdate(last_modified, usegmt=True)
                        print(f"File last modified: {last_modified_str}")

                        # Check if the file has been modified since the provided date
                        if if_modified_since:
                            since_time = parsedate_to_datetime(if_modified_since).timestamp()
                            if last_modified <= since_time:
                                # File not modified since the provided date, send 304 Not Modified
                                status_code = "304 Not Modified"
                                response = (
                                    "HTTP/1.1 304 Not Modified\r\n\r\n"
                                )
                                print("304 Not Modified, no need to send file.")
                                client_connection.sendall(response.encode('utf-8'))
                                return

                        # Read and serve the file
                        with open('test.html', 'r') as file:
                            response_body = file.read()
                        content_length = len(response_body)
                        status_code = "200 OK"
                        response = (
                            "HTTP/1.1 200 OK\r\n"
                            f"Content-Type: text/html\r\n"
                            f"Content-Length: {content_length}\r\n"
                            f"Last-Modified: {last_modified_str}\r\n\r\n" +
                            response_body
                        )
                        print("Serving test.html")
                    except FileNotFoundError:
                        status_code = "404 Not Found"
                        response = "HTTP/1.1 404 Not Found\r\n\r\nResource not found."
                else:
                    status_code = "404 Not Found"
                    response = "HTTP/1.1 404 Not Found\r\n\r\nResource not found."
                    print(f"Invalid path requested: {path}")
            else:
                status_code = "400 Bad Request"
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"

            print(f"Status: {status_code}")
            client_connection.sendall(response.encode('utf-8'))
    finally:
        client_connection.close()

# Main server loop to accept and handle requests
while True:
    client_connection, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    thread = threading.Thread(target=handle_request, args=(client_connection,))
    thread.start()
