#!/usr/bin/env python3

"""
MyRC - Client

MyRC is a chat client for the MyRC project.
There are no rooms, but many users in one big room.
Chats are encrypted with AES-256.

Connecting:
1. Open a TCP connection to the server.
2. Complete the Diffie-Hellman handshake.
    1. Accept the server's G**a % P
    2. Choose a randome value of b [2, P-1]
    3. Send your own G**b % P
    4. Your secret key is (G**a % P) ** b % P
3. Seed AES with the secret key.
4. Send your username.
5. Wait for the server to send a message, either accept or reject.
6. If reject, send a new username.
7. If accept, begin sending/receiving messages
"""
from Crypto.Cipher import AES
from Crypto.Util import Padding
import socket
import sys
import os
import random
import select

G = 2
P = 97
BYTE_ORDER = "big"
DH_MESSAGE_SIZE_BYTES = 32


class Chat(object):
    def __init__(self, sock):
        self.sock = sock
        self.key_bytes = None

    def start(self):
        self.dh_handshake()
        self.cipher = AES.new(self.key_bytes, AES.MODE_ECB)

        # Wait for input from either stdin or the server,
        # using the select() system call.
        # This is a blocking call.
        # The select() system call will not return until
        # one of the sockets is ready for reading.
        select_inputs = [sys.stdin, self.sock]
        readable, _, _ = select.select(select_inputs, [], [])
        while readable:
            if readable[0] == sys.stdin:
                # Read from stdin
                message = sys.stdin.readline()
                # Send the message to the server
                if len(message) == 0:
                    # EOF
                    print("disconnecting...")
                    return
                self.send_msg(message)
            elif readable[0] == self.sock:
                self.recv_msg()

            readable, _, _ = select.select(select_inputs, [], [])


    def send_msg(self, msg:str):
        """
        Encrypt and send a message.
        """
        msg_bytes = msg.encode()
        msg_padded = Padding.pad(msg_bytes, AES.block_size)
        ciphertext = self.cipher.encrypt(msg_padded)
        self.sock.send(ciphertext)

    def recv_msg(self):
        """
        Receive a message.
        """
        message = self.sock.recv(4096)
        message = self.cipher.decrypt(message)
        # Remove padding
        message = Padding.unpad(message, AES.block_size)
        # Decode the message and print without a newline
        print(message.decode(), end="", flush=True)

    def dh_handshake(self):
        """
        Complete the Diffie-Hellman handshake
        Return the key as bytes.
        Output must be 32 bytes long. (for a 256-bit AES key)
        """
        # 1. Accept the server's G**a % P
        ga_wire = self.sock.recv(DH_MESSAGE_SIZE_BYTES)
        ga = int.from_bytes(ga_wire, byteorder=BYTE_ORDER)
        # 2. Choose a randome value of b [2, P-1]
        b = random.randint(2, P-1)
        # 3. Send your own G**b % P
        self.sock.send((G**b % P).to_bytes(DH_MESSAGE_SIZE_BYTES, byteorder=BYTE_ORDER))
        # 4. Your secret key is (G**a % P) ** b % P
        key = (ga ** b) % P
        self.key_bytes = key.to_bytes(32, byteorder=BYTE_ORDER)
        return key


def main():
    # Get the server's IP address and port number from the arguments.
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <IP> <port>")
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2])

    # Create a TCP socket.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    chat = Chat(sock)
    chat.start()


if __name__ == '__main__':
    main()