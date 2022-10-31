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

class ClientConnection(object):
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
        """
        Sends an encrypted message to the connected client.
        """
        msg_bytes = msg.encode()
        self.conn.send(self.crypto.encrypt(msg_bytes))

    def recv_message(self):
        """
        Returns a decrypted message string or None if the decryption failed.
        """
        try:
            ciphertext = self.conn.recv(MESSAGE_SIZE_BYTES)
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
            self.client_conns = {}
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
                client_conn = ClientConnection(connection, src)
                self.client_conns[src] = {
                    "client": client_conn,
                    "thread": threading.Thread(target=self.handle_client, args=(client_conn,))
                }
                self.client_conns[src]["thread"].start()
            except Exception as e:
                print(e)
                connection.close()
                del self.client_conns[src]

    def negotiate_username(self, client_conn):
        client_conn.send_message("Enter username: ")
        username = client_conn.recv_message()
        if username is None:
            return None
        username = username.strip()
        for _, client_data in self.client_conns.items():
            if username == client_data["client"].username:
                client_conn.send_message("Username already taken. Try again.")
                return self.negotiate_username(client_conn)
        else:
            client_conn.username = username
            return username

    def close_connection(self, client_conn):
        print("Connection closed from {}".format(client_conn.addr))
        client_conn.conn.close()
        del self.client_conns[client_conn.addr]

    def send_all(self, msg):
        for client_addr, client_data in self.client_conns.items():
            client_data["client"].send_message(msg)

    def handle_msg(self, client_conn, msg):
        if len(msg) == 0:
            return
        if msg[0] == "/":
            msg = msg.strip()
            if msg == "/quit":
                self.close_connection(client_conn)
                return
            elif msg == "/list":
                username_list = [client['client'].username for client in self.client_conns.values()]
                client_conn.send_message("\n".join(username_list) + "\n")
                return
            elif msg == "/help":
                client_conn.send_message("""
/quit - quit the chat
/list - list usernames
/help - show this help message
""")
                return
            else:
                client_conn.send_message("Invalid command. Type /help for help.")
                return
        else:
            for client_addr, client_data in self.client_conns.items():
                if client_addr != client_conn.addr:
                    client_data["client"].send_message("{}: {}".format(client_conn.username, msg))


    def handle_client(self, client_conn):
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
            client_conn.do_dh_handshake()
            username = self.negotiate_username(client_conn)
            if username is None:
                self.close_connection(client_conn)
                return
            client_conn.username = username
            self.send_all("Welcome {}!\n".format(username))
            while True:
                msg = client_conn.recv_message()
                if msg is None:
                    self.close_connection(client_conn)
                    return
                self.handle_msg(client_conn, msg)
        except ConnectionError:
            self.close_connection(client_conn)
            return
        except OSError:
            return

if __name__ == '__main__':
    main()
