import socket
import threading
import random
import struct

# Constants for the simulation
PACKET_SIZE = 1024
TIMEOUT = 2  # Timeout in seconds
WINDOW_SIZE = 4  # Sliding window size
LOSS_PROBABILITY = 0  # Probability of packet loss
CORRUPTION_PROBABILITY = 0  # Probability of packet corruption

original_filename = "test.jpg"
received_filename = "received_file.jpg"

# Helper function to introduce packet loss and corruption
def simulate_network_conditions(data):
    """Simulate network conditions by introducing packet loss and corruption.
    Args:
        data (bytes): The packet data to simulate conditions on.
    Returns:
        bytes: The modified packet data, or None if the packet is lost. 
    """
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
    """ReliableSender class for sending
    data over UDP with reliability.
    Args:
        ip (str): The IP address of the receiver.
        port (int): The port number of the receiver.    
    """
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        self.seq_num = 0
        self.ack_received = threading.Event()
        self.lock = threading.Lock()

    def _send_with_retransmission(self, data):
        """Send a packet with retransmission logic.
        Args:
            data (bytes): The data to send in the
            packet.
        Returns:
            None
        """
        while True:
            self.sock.sendto(data, self.addr)
            print(f"[Sender] Sent packet {self.seq_num}")

            self.ack_received.clear()
            try:
                self.ack_received.wait(TIMEOUT)
                break
            except:
                print(f"[Sender] Timeout, retransmitting {self.seq_num}")
                
    def send_packet(self, data):
        """Send a packet with the given data and handle retransmissions.
        Args:
            data (bytes): The data to send in the packet.
        Returns:
            None
        """
        with self.lock:
            data = struct.pack('!I', self.seq_num) + data
            self._send_with_retransmission(data)
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
        """Receive ACKs from the receiver and update the sequence number.
        Returns:
            None
        """
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
        """Start the sender and send the file.
        Args:
            filename (str): The name of the file to send.
        Returns:
            None
        """
        threading.Thread(target=self.receive_acks, daemon=True).start()
        with open(filename, 'rb') as file:
            while chunk := file.read(PACKET_SIZE - 4):
                self.send_packet(chunk)
        print("[Sender] File transfer complete")


# Reliable receiver class
class ReliableReceiver:
    """ReliableReceiver class for receiving
    data over UDP with reliability.
    Args:
        ip (str): The IP address to bind the receiver to.
        port (int): The port number to bind the receiver to.
    """
    def __init__(self, ip, port):
        """Initialize the receiver with the given IP and port.
        Args:
            ip (str): The IP address to bind to.
            port (int): The port number to bind to.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.expected_seq_num = 0

    def receive(self, filename):
        """Receive data and write it to a file.
        Args:
            filename (str): The name of the file to write the received data to.
        Returns:
            None
        """
        print("[Receiver] Waiting for packets...")
        with open(filename, 'wb') as file:
            key = True
            while key:
                packet, addr = self.sock.recvfrom(PACKET_SIZE)
                modified_packet = simulate_network_conditions(packet)
                if modified_packet is None:
                    continue
                seq_num = struct.unpack('!I', modified_packet[:4])[0]
                data = modified_packet[4:]

                if seq_num == self.expected_seq_num:
                    file.write(data)
                    print(f"[Receiver] Received packet {seq_num}, sending ACK")
                    # file.flush()
                    self.sock.sendto(struct.pack('!I', seq_num), addr)
                    self.expected_seq_num += 1
                else:
                    print(f"[Receiver] Out-of-order packet {seq_num}, resending ACK {self.expected_seq_num - 1}")
                    self.sock.sendto(struct.pack('!I', self.expected_seq_num - 1), addr)
                    
                if len(data) < PACKET_SIZE - 4:
                    key = False
        print("[Receiver] File received successfully")


# Main function to run the sender or receiver
if __name__ == "__main__":
    """Main function to run the sender or receiver based on user input.
    The user can choose to run as a sender or receiver.
    """
    role = input("Enter role (1:sender/2:receiver): ").strip().lower()
    if role == "1" or role == "sender":
        sender = ReliableSender("127.0.0.1", 5001)
        sender.start(original_filename)
    elif role == "2" or role == "receiver":
        receiver = ReliableReceiver("127.0.0.1", 5001)
        receiver.receive(received_filename)

