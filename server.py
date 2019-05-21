# Author: James Haller

import tftpy
import argparse
import socket
import os
import threading


# Parse args
# =============================================================================
parser = argparse.ArgumentParser()

parser.add_argument('-r', '--root', help="TFTP root directory", default="/tftproot")
parser.add_argument('-p', '--port', help="Listen port", default=tftpy.DEF_TFTP_PORT)

args = parser.parse_args()


# Start server thread
# =============================================================================
serv = tftpy.TftpServer(tftproot=args.root)
serv_thread = threading.Thread(target=serv.listen, kwargs={'listenport': args.port})
# serv.listen(listenport=args.port)
serv_thread.start()


# Send all files
# =============================================================================
blknum = 0


def sendto_ack(sock: socket.socket, pkt_data, addr: (str, int)):
    global blknum

    ack_received = False
    while not ack_received:
        sock.sendto(pkt_data, addr)

        rx_blknum = sock.recv(1)[0]
        if rx_blknum == blknum:
            ack_received = True
            blknum = (blknum + 1) % 0x100


dir_queue = []
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(('0.0.0.0', 1069))

    raw_data, addr = sock.recvfrom(2048)
    dir_queue.append(os.path.join(args.root, raw_data.decode('utf-8')))
    print("Searching for files in {}".format(dir_queue[0]))

    while len(dir_queue) > 0:
        for dirpath, dirnames, filenames in os.walk(dir_queue.pop(0)):
            for fname in filenames:
                path = os.path.join(dirpath, fname)
                path = path[path.index(args.root) + len(args.root) + 2:]
                sendto_ack(sock, path.encode('utf-8'), addr)

            dir_queue.extend(dirnames)

    sendto_ack(sock, b'', addr)

print("Closing server")
serv.stop()
serv_thread.join()
