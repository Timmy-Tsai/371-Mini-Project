import socket
import struct
import random

# Packet Structure: Seq Num, ACK Num, Window Size, Checksum, Data
HEADER_FORMAT = "IIIH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
MAX_PACKET_SIZE = 1024
DATA_SIZE = MAX_PACKET_SIZE - HEADER_SIZE

def calculate_checksum(data):
    return sum(data.encode()) % 65536

def create_packet(seq_num, ack_num, window_size, data):
    checksum = calculate_checksum(data)
    header = struct.pack(HEADER_FORMAT, seq_num, ack_num, window_size, checksum)
    return header + data.encode()

def parse_packet(packet):
    header = packet[:HEADER_SIZE]
    seq_num, ack_num, window_size, checksum = struct.unpack(HEADER_FORMAT, header)
    data = packet[HEADER_SIZE:].decode()
    return seq_num, ack_num, window_size, checksum, data

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", 12345))
    print("Server is ready to receive...")

    expected_seq_num = 0
    receiver_window_size = 5  # Example window size
    received_data = []

    while True:
        packet, client_address = server_socket.recvfrom(MAX_PACKET_SIZE)
        seq_num, _, _, checksum, data = parse_packet(packet)

        # Verify checksum
        if checksum != calculate_checksum(data):
            print(f"Checksum error for packet {seq_num}")
            continue

        # Handle correct sequence number
        if seq_num == expected_seq_num:
            print(f"Received packet: {seq_num}, data: {data}")
            received_data.append(data)
            expected_seq_num += 1

        # Send ACK
        ack_packet = create_packet(0, expected_seq_num - 1, receiver_window_size, "")
        server_socket.sendto(ack_packet, client_address)

        if data == "END":
            print("End of transmission.")
            break

    print("Received data:", "".join(received_data))
    server_socket.close()

if __name__ == "__main__":
    main()
