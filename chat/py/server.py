#!/usr/bin/env python3

"""
MyRC Server.

MyRC is a chat server only allowing authorized clients to connect.

Connecting:
1. Server listens for incoming TCP connections on port 4040.
2. Client connects and initiates a diffie-hellman exchange.
    a. Client & Server independently generate random numbers a & b.
    b. Client sends g ** a mod p to the server.
    c. Server sends g ** b mod p to the client.
    The shared secret is g ** (a * b) mod p.
    All communication is now over AES-256-ECB with the shared secret as the key.
Handshake is complete.
3. Client sends a username to the server.
4. Server checks if the username is available.
    a. If available, the server sends a confirmation to the client.
    b. If unavailable, the server sends a rejection to the client.
5. Client can send a message to the server.
6. Server sends the message to all other clients.
"""
import socket
import sys
import threading
import time
import random
import os
from Crypto.Cipher import AES
from Crypto.Util import Padding

PORT_NUMBER = 4040
G = 2
P = 97
BYTE_ORDER = "big"
DH_MESSAGE_SIZE_BYTES = 32
MESSAGE_SIZE_BYTES = 2048

def main():
    server = Server()
    server.run()

class Client(object):
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.username = None
        self.cipher = None

    def do_dh_handshake(self):
        a = random.randint(2, P - 1)
        ga = G ** a % P
        ga_wire = ga.to_bytes(DH_MESSAGE_SIZE_BYTES, BYTE_ORDER)
        self.conn.send(ga_wire)

        b_bytes = self.conn.recv(DH_MESSAGE_SIZE_BYTES)
        gb = int.from_bytes(b_bytes, byteorder=BYTE_ORDER)
        shared_secret = gb ** a % P
        print("Shared secret: {}".format(shared_secret))
        shared_secret_bytes = shared_secret.to_bytes(DH_MESSAGE_SIZE_BYTES, BYTE_ORDER)
        print("Shared secret bytes: {}".format(shared_secret_bytes.hex()))
        self.cipher = AES.new(shared_secret_bytes, AES.MODE_ECB)

    def send_message(self, msg:str):
        msg_bytes = msg.encode()
        msg_data = Padding.pad(msg_bytes, AES.block_size)
        self.conn.send(self.cipher.encrypt(msg_data))

    def decrypt_msg(self, ciphertext):
        message_padded = self.cipher.decrypt(ciphertext)
        if len(message_padded) == 0:
            return None
        return Padding.unpad(message_padded, AES.block_size).decode()


class Server(object):
    def __init__(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('localhost', PORT_NUMBER))
            self.sock.listen(1)
            self.clients = {}
            self.username_list = set()
        except OSError as e:
            print("Could not create socket: {}".format(e))
            sys.exit(1)

    def run(self):
        while True:
            # Wait for a connection, add it to a list of connections.
            # Select between existing sockets and handle that socket.
            # if it is a new socket, do the handshake, negotiate username,
            # and add it to the list of connections.
            (connection,src) = self.sock.accept()
            try:
                client = Client(connection, src)
                self.clients[src] = {
                    "client": client,
                    "thread": threading.Thread(target=self.handle_client, args=(client,))
                }
                self.clients[src]["thread"].start()
            except Exception as e:
                print(e)
                connection.close()
                del self.clients[src]

    def negotiate_username(self, client):
        client.send_message("Enter username: ")
        username = client.decrypt_msg(client.conn.recv(MESSAGE_SIZE_BYTES))
        if username is None:
            return None
        username = username.strip()
        if username in self.username_list:
            client.send_message("Username already taken. Try again.")
            return self.negotiate_username(client)
        else:
            client.username = username
            self.username_list.add(username)
            return username

    def close_connection(self, client):
        print("Connection closed from {}".format(client.addr))
        client.conn.close()
        if client.username in self.username_list:
            self.username_list.remove(client.username)
        del self.clients[client.addr]

    def handle_client(self, client):
        """
        Handle a client connection:
            1. Initiate the diffie-hellman exchange.
            2. Receive a username.
            3. Check if username is available.
            4. If available, send a confirmation to the client.
            5. If unavailable, send a rejection to the client.
            6. Receive a message.
            7. Send the message to all other clients.
        """
        try:
            client.do_dh_handshake()
            username = self.negotiate_username(client)
            if username is None:
                self.close_connection(client)
                return
            client.username = username
            client.send_message("Welcome {}!\n".format(username))
            while True:
                got = client.conn.recv(MESSAGE_SIZE_BYTES)
                msg = client.decrypt_msg(got)
                if msg is None:
                    self.close_connection(client)
                    return
                print("Received message: {}".format(msg))
                for src in self.clients:
                    c = self.clients[src]["client"]
                    if c.conn != client.conn:
                        attributed_msg = "{}: {}".format(client.username, msg)
                        c.send_message(attributed_msg)

        except ConnectionError:
            self.close_connection(client)
            return


if __name__ == '__main__':
    main()
