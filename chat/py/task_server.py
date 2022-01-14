#!/usr/bin/env python3

import socket
import sys
import threading

import crypto

PORT_NUMBER = 4040
MESSAGE_SIZE_BYTES = 2048

def main():
    server = Server()
    server.run()

class Client(object):
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.username = None
        self.crypto = crypto.Crypto()

    def do_dh_handshake(self):
        try:
            pubkey = self.crypto.init_keys()
            self.conn.send(pubkey)
            b_repr = self.conn.recv(MESSAGE_SIZE_BYTES)
            self.crypto.handshake(b_repr)
        except ValueError as e:
            print("Error in DH handshake: {}".format(e))
            self.conn.close()
            return
        except TypeError as e:
            print("Error in DH handshake: {}".format(e))
            self.conn.close()
            return

    def send_message(self, msg:str):
        msg_bytes = msg.encode()
        self.conn.send(self.crypto.encrypt(msg_bytes))

    def decrypt_msg(self, ciphertext):
        try:
            message = self.crypto.decrypt(ciphertext)
            if message is None:
                return None
            return message.decode()
        except ValueError as e:
            print("Error decrypting message: {}".format(e))
            return None


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

    def close_connection(self, client):
        print("Connection closed from {}".format(client.addr))
        client.conn.close()
        if client.username in self.username_list:
            self.username_list.remove(client.username)
        del self.clients[client.addr]



if __name__ == '__main__':
    main()
