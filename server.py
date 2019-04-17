# Author: James Haller

import tftpy
import argparse


# Parse args
# =============================================================================
parser = argparse.ArgumentParser()

parser.add_argument('-r', '--root', help="TFTP root directory", default="/tftproot")
parser.add_argument('-p', '--port', help="Listen port", default=tftpy.DEF_TFTP_PORT)

args = parser.parse_args()


# Start server
# =============================================================================
serv = tftpy.TftpServer()
serv.listen(listenport=args.port)

