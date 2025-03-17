import socket
import threading
import time
import random
import struct

# Constants
PACKET_SIZE = 1024
TIMEOUT = 2  # Timeout in seconds
WINDOW_SIZE = 4  # Sliding window size
LOSS_PROBABILITY = 0  # Probability of packet loss
CORRUPTION_PROBABILITY = 0.1  # Probability of packet corruption

# Helper function to introduce packet loss and corruption
def simulate_network_conditions(data):
    if random.random() < LOSS_PROBABILITY:
        print("[Simulator] Packet lost!")
        return None
    if random.random() < CORRUPTION_PROBABILITY:
        corrupted_data = bytearray(data)
        corrupted_data[random.randint(0, len(data) - 1)] ^= 0xFF
        print("[Simulator] Packet corrupted!")
        return bytes(corrupted_data)
    return data

# Reliable sender class
class ReliableSender:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        self.seq_num = 0
        self.ack_received = threading.Event()
        self.lock = threading.Lock()

    def send_packet(self, data):
        while True:
            packet = struct.pack('!I', self.seq_num) + data
            self.sock.sendto(packet, self.addr)
            print(f"[Sender] Sent packet {self.seq_num}")

            self.ack_received.clear()
            try:
                self.ack_received.wait(TIMEOUT)
                break
            except:
                print(f"[Sender] Timeout, retransmitting {self.seq_num}")

    def receive_acks(self):
        while True:
            try:
                ack, _ = self.sock.recvfrom(4)
                ack_num = struct.unpack('!I', ack)[0]
                print(f"[Sender] Received ACK {ack_num}")
                if ack_num == self.seq_num:
                    self.ack_received.set()
                    self.seq_num += 1
            except:
                pass

    def start(self, filename):
        threading.Thread(target=self.receive_acks, daemon=True).start()
        with open(filename, 'rb') as file:
            while chunk := file.read(PACKET_SIZE - 4):
                self.send_packet(chunk)
        print("[Sender] File transfer complete")

# Reliable receiver class
class ReliableReceiver:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.expected_seq_num = 0

    def receive(self, filename):
        with open(filename, 'wb') as file:
            while True:
                packet, addr = self.sock.recvfrom(PACKET_SIZE)
                modified_packet = simulate_network_conditions(packet)
                if modified_packet is None:
                    continue
                seq_num = struct.unpack('!I', modified_packet[:4])[0]
                data = modified_packet[4:]

                if seq_num == self.expected_seq_num:
                    file.write(data)
                    print(f"[Receiver] Received packet {seq_num}, sending ACK")
                    self.sock.sendto(struct.pack('!I', seq_num), addr)
                    self.expected_seq_num += 1
                else:
                    print(f"[Receiver] Out-of-order packet {seq_num}, resending ACK {self.expected_seq_num - 1}")
                    self.sock.sendto(struct.pack('!I', self.expected_seq_num - 1), addr)
        print("[Receiver] File received successfully")

# Network simulator class
class NetworkSimulator:
    def __init__(self, recv_ip, recv_port, send_ip, send_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((recv_ip, recv_port))
        self.send_addr = (send_ip, send_port)

    def run(self):
        while True:
            packet, addr = self.sock.recvfrom(PACKET_SIZE)
            modified_packet = simulate_network_conditions(packet)
            if modified_packet:
                self.sock.sendto(modified_packet, self.send_addr)
                print("[Simulator] Packet forwarded")

# Example usage
if __name__ == "__main__":
    role = input("Enter role (sender/receiver/simulator): ").strip().lower()
    if role == "sender":
        sender = ReliableSender("127.0.0.1", 5001)
        sender.start("test.txt")
    elif role == "receiver":
        receiver = ReliableReceiver("127.0.0.1", 5001)
        receiver.receive("received_file.txt")
    elif role == "simulator":
        simulator = NetworkSimulator("127.0.0.1", 5001, "127.0.0.1", 5002)
        simulator.run()
