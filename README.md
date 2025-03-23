# Python Data transfer simulator

Python-based UDP data transfer simulator

## 1- How to compile and run your code

### Clone repository

```
git clone https://github.com/50516021/Python_data_transfer.git
```

### Environment setting

Use `requirements.txt` to install necessary packages:

```
pip install -r requirements.txt
```

### [ping] - Running main code

The main script `UDP_data_transfer.py` will behave as both receiver/sender.<br>
(replace `<python>` depending your python environment):

> Note: **Open two separated terminal to excecute both receiver/sender.**

In your terminal 1, excecute

```
sudo <python> my_ping.py <host address>

```

### [traceroute] - Running main code

The main script `my_traceroute.py` will check your network routing to the network host.<br>
(replace `<python>` depending your python environment):

> Note: **You need to use `sudo` command to operate this to use raw sockets to compose ICMP packets.**

```
sudo <python> my_traceroute.py <host address>
```

### Windows operation:

If using Windows, ensure Windows Defender Firewall allows ICMP traffic:

- Turn Firewall off (not recommended, turn it back on after testing).
- Create an Inbound ICMP Rule. (see this link: [Link](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/configure))
- Enable existing inbound ICMP rule. Look for advanced setting in printer and sharing settings and find inbound ICMP echo request.
- Use the argparse module in Python to parse command-line arguments.

## 2- Examples of command-line usage

### 2.1- Ping options

`-c count`: Stop after sending (and receiving) count ECHO_RESPONSE packets. If this option is not specified, ping will operate until interrupted.<br>
`-i wait`: Wait for 'wait' seconds between sending each packet. Default is one second.<br>
`-s packetsize`: Specify the number of data bytes to be sent. Default is 56 (64 ICMP data bytes including the header).<br>
`-t timeout`: Specify a timeout in seconds before ping exits regardless of how many packets have been received.<br>

Example usage:

```
sudo <python> my_ping.py -c 5   <host address> # stop at 5 packets
sudo <python> my_ping.py -i 2   <host address> # wait for 2 seconds to send another packet
sudo <python> my_ping.py -s 112 <host address> # specify the packet size as 112 bytes
sudo <python> my_ping.py -t 2   <host address> # set 2 seconds time limit for receiving packets
```

### 2.2- Traceroute options

`-n`: Print hop addresses numerically rather than symbolically and numerically. <br>
`-q nqueries`: Set the number of probes per TTL to nqueries. <br>
`-S`: Print a summary of how many probes were not answered for each hop. <br>

Example usage:

```
sudo <python> my_traceroute.py -n   <host address> # print hop addresses numerically
sudo <python> my_traceroute.py -q 2 <host address> # set 2 quesries per TTL
sudo <python> my_traceroute.py -S   <host address> # print out summary of percentage of probes
```

## 3- Reference

- [ping(8) - Linux man page](https://linux.die.net/man/8/ping) <br>
  https://linux.die.net/man/8/ping
- [traceroute(8) - Linux man page](https://linux.die.net/man/8/traceroute) <br>
  https://linux.die.net/man/8/traceroute

### Author

**Akira Takeuchi**

- [github/50516021s](https://github.com/50516021)
- [Official Homepage](https://akiratakeuchi.com/)

### License

Copyright © 2025, [Akira Takeuchi](https://github.com/50516021).
Released under the [MIT License](LICENSE).
