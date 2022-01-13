#!/usr/bin/env python3

import socket
import sys
import select

import crypto

BYTE_ORDER = "big"
MESSAGE_SIZE_BYTES = 2048


class Chat(object):
    def __init__(self, sock):
        self.sock = sock
        self.crypto = crypto.Crypto()

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
        ciphertext = self.crypto.encrypt(msg_bytes)
        self.sock.send(ciphertext)

    def recv_msg(self):
        """
        Receive a message.
        """
        message_bytes = self.sock.recv(MESSAGE_SIZE_BYTES)
        message = self.crypto.decrypt(message_bytes)
        if message is None:
            return
        # Decode the message and print without a newline
        print(message.decode(), end="", flush=True)

    def dh_handshake(self):
        """
        Complete the Diffie-Hellman handshake
        Return the key as bytes.
        Output must be 32 bytes long. (for a 256-bit AES key)
        """
        ga_repr = self.sock.recv(MESSAGE_SIZE_BYTES)
        pubkey = self.crypto.handshake_part1()
        self.crypto.handshake_part2(ga_repr)
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