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
import select

import crypto

BYTE_ORDER = "big"
MESSAGE_SIZE_BYTES = 2048


class Chat(object):
    def __init__(self, sock):
        self.sock = sock
        self.crypto = crypto.ECDiffieHellman()

    def start(self):
        self.dh_handshake()
        # self.cipher = AES.new(self.key_bytes, AES.MODE_ECB)

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
                if len(message) == 0 or message == "/quit\n":
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
        ciphertext = self.crypto.cipher.encrypt(msg_padded)
        self.sock.send(ciphertext)

    def recv_msg(self):
        """
        Receive a message.
        """
        message = self.sock.recv(4096)
        message = self.crypto.cipher.decrypt(message)
        if len(message) == 0:
            return
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
        ga_wire = self.sock.recv(MESSAGE_SIZE_BYTES)
        ga = self.crypto.deserialize_key(ga_wire)
        pubkey, complete_handshake = self.crypto.handshake()
        complete_handshake(ga)
        self.sock.send(pubkey)


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