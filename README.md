# Python Data Transfer Simulator

Python-based UDP data transfer simulator for reliable file transfer over UDP.

---

## 1. How to Compile and Run the Code

### Clone the Repository

```
git clone https://github.com/50516021/Python_data_transfer.git
```

### Environment Setup

Use `requirements.txt` to install necessary packages:

```
pip install -r requirements.txt
```

---

## 2. Running the Main Code

The main script `UDP_data_transfer.py` can be used to run both the sender and receiver.  
**Note:** Open two separate terminals to execute the sender and receiver.

### 2.1 Running the Receiver

In one terminal, execute the following command to start the receiver:

```
python UDP_data_transfer.py -role receiver -ip <receiver_ip> -port <receiver_port> -frcv <output_file>
```

#### Receiver Options:

- `-role receiver`: Specifies the role as the receiver.
- `-ip`: The IP address to bind the receiver to (default: `127.0.0.1`).
- `-port`: The port number to bind the receiver to (default: `5001`).
- `-frcv`: The name of the file to save the received data (default: `received_file.txt`).
- `-loss`: Probability of packet loss (default: `0.1`).
- `-corr`: Probability of packet corruption (default: `0.1`).
- `-size`: Size of each packet in bytes (default: `1024`).

#### Example:

```
python UDP_data_transfer.py -role receiver -ip 127.0.0.1 -port 5001 -frcv received_file.txt
```

---

### 2.2 Running the Sender

In another terminal, execute the following command to start the sender:

```
python UDP_data_transfer.py -role sender -ip <receiver_ip> -port <receiver_port> -fsnd <input_file>
```

#### Sender Options:

- `-role sender`: Specifies the role as the sender.
- `-ip`: The IP address of the receiver (default: `127.0.0.1`).
- `-port`: The port number of the receiver (default: `5001`).
- `-fsnd`: The name of the file to send (default: `test.txt`).
- `-timeout`: Timeout for ACK in seconds (default: `2`).
- `-max_retries`: Maximum retries for sending packets (default: `5`).
- `-reorder`: Probability of packet reordering (default: `0.0`).

#### Example:

```
python UDP_data_transfer.py -role sender -ip 127.0.0.1 -port 5001 -fsnd test.txt
```

---

## 3. Features of the Protocol

### 3.1 Reliable Data Transfer

- Implements retransmission logic with a maximum retry limit (`-max_retries`).
- Uses ACKs to confirm successful packet delivery.

### 3.2 EOF Handling

- The sender sends a special EOF packet with a flag to indicate the end of the file.
- The receiver identifies the EOF packet using the flag and terminates the transfer process.

### 3.3 Simulated Network Conditions

- Simulates packet loss and corruption using the `simulate_network_conditions` function.
- Configurable via `-loss` (packet loss probability) and `-corr` (packet corruption probability).

### 3.4 Packet Reordering

- Simulates packet reordering with the `-reorder` option.

---

## 4. Example Usage

### 4.1 Receiver

Start the receiver to listen for incoming packets:

```
python UDP_data_transfer.py -role receiver -ip 127.0.0.1 -port 5001 -frcv output.txt
```

### 4.2 Sender

Send a file to the receiver:

```
python UDP_data_transfer.py -role sender -ip 127.0.0.1 -port 5001 -fsnd input.txt
```

### 4.3 Simulating Network Conditions

To simulate packet loss and corruption:

```
python UDP_data_transfer.py -role sender -ip 127.0.0.1 -port 5001 -fsnd input.txt -loss 0.2 -corr 0.1
```

---

## 5. Notes

- Ensure that the sender and receiver use the same IP address and port number.
- Use separate terminals for the sender and receiver.
- For testing, you can use `127.0.0.1` as the IP address to simulate communication on the same machine.

---

## 6. Author

**Akira Takeuchi**

- [GitHub](https://github.com/50516021)
- [Official Homepage](https://akiratakeuchi.com/)

---

## 7. License

Released under the [MIT License](LICENSE).
