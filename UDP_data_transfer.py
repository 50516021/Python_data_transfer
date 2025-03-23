"""Main function to run the sender or receiver based on user input.
The user can choose to run as a sender or receiver.
The user can specify the IP address, port number, and other parameters.
"""

import argparse
from utils.data_sender import ReliableSender
from utils.data_receiver import ReliableReceiver


def main():
    """Main function to run the sender or receiver based on user input.
    The user can choose to run as a sender or receiver.
    """

    parser = argparse.ArgumentParser(description="Reliable UDP File Transfer")
    parser.add_argument(
        "-role", required=True, help="Role of the node (sender/receiver)")
    parser.add_argument(
        "-ip", default="127.0.0.1", help="IP address of the sender/receiver")
    parser.add_argument(
        "-port", type=int, default=5001, help="Port number for communication")
    parser.add_argument(
        "-frcv", default="received_file.txt", help="File name to save received data")
    parser.add_argument(
        "-fsnd", default="test.txt", help="File name to send")
    parser.add_argument(
        "-loss", type=float, default=0.1, help="Probability of packet loss")
    parser.add_argument(
        "-corr", type=float, default=0.1, help="Probability of packet corruption")
    parser.add_argument(
        "-size", type=int, default=1024, help="Size of each packet in bytes")
    parser.add_argument(
        "-timeout", type=int, default=2, help="Timeout for ACK in seconds")
    parser.add_argument(
        "-max_retries", type=int, default=5, help="Maximum retries for sending packets")
    parser.add_argument(
        "-reorder", type=float, default=0.0, help="Probability of packet reordering")

    # Parse the command-line arguments
    args = parser.parse_args()
    role = args.role
    IPadd = args.ip
    port_num = args.port
    received_filename = args.frcv
    original_filename = args.fsnd

    loss_prob = args.loss
    corruption_prob = args.corr
    packet_size = args.size
    timeout = args.timeout
    max_retries = args.max_retries
    reorder_chance = args.reorder

    # role = input("Enter role (1:sender/2:receiver): ").strip().lower()

    if role == "1" or role == "sender":
        sender = ReliableSender(
            IPadd,
            port_num,
            timeout,
            packet_size,
            max_retries,
            reorder_chance
        )
        sender.start(original_filename)
    elif role == "2" or role == "receiver":
        receiver = ReliableReceiver(
            IPadd,
            port_num,
            packet_size,
            loss_prob,
            corruption_prob
        )
        receiver.receive(received_filename)


# Main function to run the sender or receiver
if __name__ == "__main__":
    main()
