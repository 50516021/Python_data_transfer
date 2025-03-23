import socket
import threading
import struct
import random
import time


# Reliable sender class
class ReliableSender:
    """ReliableSender class for sending
    data over UDP with reliability.
    Args:
        ip (str): The IP address of the receiver.
        port (int): The port number of the receiver.    
    """
    def __init__(self, ip, port, timeout=2, packet_size=1024, max_retries=5, 
                 reorder_chance=0.0):
        """Initialize the sender with the given IP and port.
        Args:
            ip (str): The IP address of the receiver.
            port (int): The port number of the receiver.
            timeout (int): Timeout for ACK in seconds.
            packet_size (int): Size of each packet in bytes.
            max_retries (int): Maximum retries for sending packets.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        self.seq_num = 0
        self.ack_received = threading.Event()
        self.lock = threading.Lock()
        self.timeout = timeout
        self.packetsize = packet_size
        self.running = True
        self.max_retries = max_retries
        self.sock.settimeout(self.timeout)
        self.reorder_chance = reorder_chance
        self.reorder_buffer = []

    def _simulate_reorder(self, packet):
        """Simulate packet reordering based on the reorder chance.
        Args:
            packet (bytes): The packet to potentially reorder.
        Returns:
            bytes: The packet if not reordered, or None if reordered.
        """
        if random.random() < self.reorder_chance:
            print(f"[Sender] Reordering packet {self.seq_num}, buffering...")
            self.reorder_buffer.append(packet)
            return None
        else:
            return packet

    def _flush_reorder_buffer(self):
        """
        _summary_ Flush the reorder buffer by sending all buffered packets.
        Returns:
            None
        """
        if self.reorder_buffer:
            time.sleep(0.1)  # simulate delay
            for pkt in self.reorder_buffer:
                self.sock.sendto(pkt, self.addr)
                print(f"[Sender] Flushed reordered packet")
            self.reorder_buffer.clear()

    def _send_with_retransmission(self, data):
        """Send a packet with retransmission logic.
        Args:
            data (bytes): The data to send in the packet.
        Returns:
            None
        """
        retries = 0

        while retries < self.max_retries:
            pkt_to_send = self._simulate_reorder(data)
            if pkt_to_send:
                self.sock.sendto(pkt_to_send, self.addr)
                print(f"[Sender] Sent packet {self.seq_num}")
            self.ack_received.clear()
            if self.ack_received.wait(self.timeout):
                print(f"[Sender] ACK received for packet {self.seq_num}")
                self._flush_reorder_buffer()
                return
            else:
                print(f"[Sender] Timeout, retransmitting {self.seq_num}")
                retries += 1
        print(f"[Sender] Max retries reached for packet {self.seq_num}, giving up")

    def send_packet(self, data, is_eof=False):
        """Send a packet with the given data and handle retransmissions.
        Args:
            data (bytes): The data to send in the packet.
            is_eof (bool): True if this packet is the end of file (EOF) packet, False otherwise.
        Returns:
            None
        """
        flag = 1 if is_eof else 0  # 0 for normal packet, 1 for EOF
        with self.lock:
            packet = struct.pack('!B I', flag, self.seq_num) + data
            self._send_with_retransmission(packet)
            if is_eof:
                print("[Sender] -- Sent EOF packet --")

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
            except socket.timeout:
                print("[Sender] ACK receive timeout, continuing")
                continue
            except Exception as e:
                if self.running:  # only print if the sender is still running
                    print(f"[Sender] Error occurred: {e}")

        print("[Sender] ACK receiving thread exiting")

    def start(self, filename):
        """Start the sender and send the file.
        Args:
            filename (str): The name of the file to send.
        Returns:
            None
        """
        ack_thread = threading.Thread(target=self.receive_acks, daemon=True)
        ack_thread.start()
        with open(filename, 'rb') as file:
            while chunk := file.read(self.packetsize - 5):
                self.send_packet(chunk)

            # send EOF packet
            print("[Sender] Sending EOF packet")
            self.send_packet(b'', is_eof=True)
            self.running = False 

        # finish sending
        # self.running = False
        print("[Sender] Closing socket")
        self.sock.close()
        ack_thread.join()  # wait for the ACK thread to finish
        print("[Sender] File transfer complete")
