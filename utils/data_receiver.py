import socket
import random
import struct


# Helper function to introduce packet loss and corruption
def simulate_network_conditions(
    data, LOSS_PROBABILITY=0.1, CORRUPTION_PROBABILITY=0.1
):
    """Simulate network conditions by introducing packet loss and corruption.
       (only refered in the receiver side)
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


# Reliable receiver class
class ReliableReceiver:
    """ReliableReceiver class for receiving
    data over UDP with reliability.
    Args:
        ip (str): The IP address to bind the receiver to.
        port (int): The port number to bind the receiver to.
    """
    def __init__(
        self, ip, port,
        packet_size=1024,
        loss_probability=0.1,
        corruption_probability=0.1
    ):
        """Initialize the receiver with the given IP and port.
        Args:
            ip (str): The IP address to bind to.
            port (int): The port number to bind to.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.expected_seq_num = 0
        self.packet_size = packet_size
        self.loss_probability = loss_probability
        self.corruption_probability = corruption_probability

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
                packet, addr = self.sock.recvfrom(self.packet_size)

                # simulate network conditions
                modified_packet = simulate_network_conditions(
                    packet,
                    self.loss_probability,
                    self.corruption_probability
                )
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

                # receive EOF packet
                if not data:
                    print("[Receiver] EOF packet received")
                    key = False
                    self.sock.sendto(struct.pack('!I', seq_num), addr)  # send final ACK
        self.sock.close()
        print("[Receiver] File received successfully")
        print("[Receiver] Closing socket")
        print("[Receiver] Exiting")
        return
