# Author: James Haller

import tftpy
import argparse


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


parser.add_argument("addr", help="TFTP server IPv4 address w/ optional port", default="localhost")
parser.add_argument("path", help="Path to files to transmit")
parser.add_argument('-d', '--dest', help="TFTP destination directory (default=<path>)", default=None)

args = parser.parse_args()

if args.dest is None:
    args.dest = args.path


# Start transfer
# =============================================================================
client = tftpy.TftpClient(*args.addr)
client.download(args.path, args.dest)
