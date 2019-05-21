# Author: James Haller

import tftpy
import argparse
import socket
import os


# Parse args
# =============================================================================
parser = argparse.ArgumentParser()


def s2ip4(addr: str, port: int = tftpy.DEF_TFTP_PORT) -> (str, int):
    if ":" in addr:
        addr = addr.split(":")
        addr, port = addr[0], addr[1]

    octets = tuple(addr.split("."))
    if len(octets) != 4:
        raise argparse.ArgumentError("IPv4 must have 4 octets")

    for octet in octets:
        try:
            if not (0 <= int(octet) <= 255):
                raise argparse.ArgumentError("IPv4 octets must be in the range [0-255]")
        except ValueError:
            raise argparse.ArgumentError("IPv4 octets must be valid, base10 integers")

    return addr, port


parser.add_argument("addr", type=s2ip4, help="TFTP server IPv4 address w/ optional port", default="localhost")
parser.add_argument("-p", "--path", help="Path to files to transmit", default=".")
parser.add_argument('-d', '--dest', help="TFTP destination directory (default=<path>)", default="./")

args = parser.parse_args()

if args.dest[0].isalnum():
    args.dest = os.path.join(".", args.dest)


# Start transfer
# =============================================================================
blknum = 0


def ack(sock: socket.socket, addr: (str, int)) -> None:
    global blknum

    ack_pkt = bytearray()
    ack_pkt.append(blknum)
    sock.sendto(ack_pkt, addr)
    blknum = (blknum + 1) % 0x100


def recv_ack(sock: socket.socket, addr: (str, int)) -> bytes:
    data = sock.recv(1024)

    ack(sock, addr)

    return data


client = tftpy.TftpClient(*args.addr)

name_serv_addr = (args.addr[0], 1069)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(('0.0.0.0', 1069))

    print("Searching for {} on {}:{}".format(args.path, *name_serv_addr))
    sock.sendto(args.path.encode('utf-8'), name_serv_addr)

    rx_dat = recv_ack(sock, name_serv_addr)
    while len(rx_dat) > 0:
        path = rx_dat.decode('utf-8')
        dst = os.path.join(args.dest, path)
        print("Downloading '{}' to '{}'".format(path, dst))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        client.download(path, dst)

        rx_dat = recv_ack(sock, name_serv_addr)

    ack(sock, name_serv_addr)
    print("End of transfer")
