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
            pubkey = self.crypto.handshake_part1()
            self.conn.send(pubkey)
            b_repr = self.conn.recv(MESSAGE_SIZE_BYTES)
            self.crypto.handshake_part2(b_repr)
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

    def send_all(self, msg):
        for client_addr, client_data in self.clients.items():
            client_data["client"].send_message(msg)

    def handle_msg(self, client, msg):
        if len(msg) == 0:
            return
        if msg[0] == "/":
            msg = msg.strip()
            if msg == "/quit":
                self.close_connection(client)
                return
            elif msg == "/list":
                client.send_message("\n".join(self.username_list) + "\n")
                return
            elif msg == "/help":
                client.send_message("""
/quit - quit the chat
/list - list usernames
/help - show this help message
""")
                return
            else:
                client.send_message("Invalid command. Type /help for help.")
                return
        else:
            for client_addr, client_data in self.clients.items():
                if client_addr != client.addr:
                    client_data["client"].send_message("{}: {}".format(client.username, msg))


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
            self.send_all("Welcome {}!\n".format(username))
            while True:
                got = client.conn.recv(MESSAGE_SIZE_BYTES)
                msg = client.decrypt_msg(got)
                if msg is None:
                    self.close_connection(client)
                    return
                self.handle_msg(client, msg)
        except ConnectionError:
            self.close_connection(client)
            return
        except OSError:
            return

if __name__ == '__main__':
    main()
