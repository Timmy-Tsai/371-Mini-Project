import socket
import struct
import time
import random

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

def parse_ack(packet):
    seq_num, ack_num, window_size, _ = struct.unpack(HEADER_FORMAT, packet)
    return seq_num, ack_num, window_size

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("127.0.0.1", 12345)
    client_socket.settimeout(0.5)

    data_chunks = [f"Chunk {i}" for i in range(1, 11)] + ["END"]
    congestion_window = 1
    threshold = 4
    base = 0
    next_seq_num = 0
    sent_packets = {}

    while base < len(data_chunks):
        # Send packets within congestion window
        while next_seq_num < base + congestion_window and next_seq_num < len(data_chunks):
            packet = create_packet(next_seq_num, 0, congestion_window, data_chunks[next_seq_num])

            # Random Aspect: Simulate packet loss
            if random.random() < 0.10:
                print(f"Sent LOST packet: {next_seq_num}")
            else:
                # simulate corruption - bitflip
                if random.random() < 0.10:
                    curropt = bytearray(packet)
                    # bit flip but dont currupot the header
                    curropt[random.randint(0, len(curropt) - 1)] ^= 1

                    client_socket.sendto(curropt, server_address)
                    print(f"Sent CURRUPT packet: {next_seq_num}")

                else:
                    client_socket.sendto(packet, server_address)
                    print(f"Sent packet: {next_seq_num}")


            sent_packets[next_seq_num] = packet
            next_seq_num += 1

        # Wait for ACKs
        try:
            ack_packet, _ = client_socket.recvfrom(HEADER_SIZE)
            _, ack_num, _ = parse_ack(ack_packet)
            print(f"Received ACK: {ack_num}")

            # Slide window and update congestion window
            if ack_num >= base:
                base = ack_num + 1
                if congestion_window < threshold:
                    congestion_window *= 2  # Slow start
                else:
                    congestion_window += 1  # Congestion avoidance

        except socket.timeout:
            # Timeout: reduce congestion window and retransmit
            print("Timeout, retransmitting...")
            threshold = max(1, congestion_window // 2)
            congestion_window = 1
            for seq_num in range(base, next_seq_num):
                client_socket.sendto(sent_packets[seq_num], server_address)
                print(f"Retransmitted packet: {seq_num}")

    print("All packets sent and acknowledged.")
    client_socket.close()

if __name__ == "__main__":
    main()
