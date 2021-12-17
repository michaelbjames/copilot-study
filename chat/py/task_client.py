#!/usr/bin/env python3

import sys

import crypto

BYTE_ORDER = "big"
MESSAGE_SIZE_BYTES = 2048


def main():
    # Get the server's IP address and port number from the arguments.
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <IP> <port>")
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2])


if __name__ == '__main__':
    main()