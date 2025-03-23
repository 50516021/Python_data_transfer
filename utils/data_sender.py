import socket
import threading
import struct


# Reliable sender class
class ReliableSender:
    """ReliableSender class for sending
    data over UDP with reliability.
    Args:
        ip (str): The IP address of the receiver.
        port (int): The port number of the receiver.    
    """
    def __init__(self, ip, port, timeout=2, packet_size=1024):
        """Initialize the sender with the given IP and port.
        Args:
            ip (str): The IP address of the receiver.
            port (int): The port number of the receiver.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        self.seq_num = 0
        self.ack_received = threading.Event()
        self.lock = threading.Lock()
        self.timeout = timeout
        self.packetsize = packet_size
        self.running = True

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
                if self.ack_received.wait(self.timeout):  # wait for ACK or timeout
                    print(f"[Sender] ACK received for packet {self.seq_num}")
                    break
                else:
                    print(f"[Sender] Timeout, retransmitting {self.seq_num}")
            except Exception as e:
                print(f"[Sender] Error during retransmission: {e}")

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

    def receive_acks(self):
        """Receive ACKs from the receiver and update the sequence number.
        Returns:
            None
        """
        while self.running:  # check if the sender is still running
            try:
                ack, _ = self.sock.recvfrom(4)
                ack_num = struct.unpack('!I', ack)[0]
                print(f"[Sender] Received ACK {ack_num}")
                if ack_num == self.seq_num:
                    self.ack_received.set()
                    self.seq_num += 1
            except Exception as e:
                if self.running:  # only print if the sender is still running
                    print(f"[Sender] Error occurred: {e}")

    def start(self, filename):
        """Start the sender and send the file.
        Args:
            filename (str): The name of the file to send.
        Returns:
            None
        """
        ack_thread = threading.Thread(target=self.receive_acks)
        ack_thread.start()  # start the ACK receiving thread
        with open(filename, 'rb') as file:
            while chunk := file.read(self.packetsize - 4):
                self.send_packet(chunk)

            # send EOF packet
            self.send_packet(b'')

        # finish sending
        self.running = False
        ack_thread.join()  # wait for the ACK thread to finish
        print("[Sender] Closing socket")
        self.sock.close()
        print("[Sender] File transfer complete")
