#!/usr/bin/env python3

import socket
import sys
from typing import Optional
import threading

import crypto

PORT_NUMBER = 4040

class Server(object):
    def __init__(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('localhost', PORT_NUMBER))
            self.sock.listen(1)
            self.client_conns = {}
        except OSError as e:
            print("Could not create socket: {}".format(e))
            sys.exit(1)

    def run_client(self, client_conn):
        # TODO
        pass

    def run(self):
       while True:
            # Wait for a connection, add it to a dictionary of connections,
            # keyed by the address of the client.
            # Spin that connection off to another thread to do the handshake,
            # negotiate the username, and listen for incoming messages.
            (connection,src) = self.sock.accept()
            try:
                client_conn = ClientConnection(connection, src)
                self.client_conns[src] = {
                    "client": client_conn,
                    "thread": threading.Thread(target=self.run_client, args=(client_conn,))
                }
                self.client_conns[src]["thread"].start()
            except Exception as e:
                print(e)
                connection.close()
                del self.client_conns[src]

    def close_connection(self, client_conn):
        print("Connection closed from {}".format(client_conn.addr))
        client_conn.conn.close()
        if client_conn.username in self.username_list:
            self.username_list.remove(client_conn.username)
        del self.client_conns[client_conn.addr]


def main():
    server = Server()
    server.run()

class ClientConnection(object):
    MESSAGE_SIZE_BYTES = 2048

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.username = None
        self.crypto = crypto.Crypto()

    def do_dh_handshake(self):
        """
        Performs Diffie-Hellman key exchange with the client.
        It establishes the shared secret so that send_message and recv_message
        can be used to securely communicate with the client.
        """
        try:
            pubkey = self.crypto.init_keys()
            self.conn.send(pubkey)
            b_repr = self.conn.recv(ClientConnection.MESSAGE_SIZE_BYTES)
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
        """
        Sends an encrypted message to the connected client.
        """
        msg_bytes = msg.encode()
        self.conn.send(self.crypto.encrypt(msg_bytes))

    def recv_message(self) -> Optional[str]:
        """
        Returns a decrypted message string or None if the decryption failed.
        """
        try:
            ciphertext = self.conn.recv(ClientConnection.MESSAGE_SIZE_BYTES)
            message = self.crypto.decrypt(ciphertext)
            if message is None:
                return None
            return message.decode()
        except ValueError as e:
            print("Error decrypting message: {}".format(e))
            return None


if __name__ == '__main__':
    main()
