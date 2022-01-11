use std::net::{TcpListener, TcpStream, SocketAddr};
use std::io::{Write};
use std::collections::HashMap; 
use std::collections::HashSet; 
pub use bp256::r1::BrainpoolP256r1;
extern crate crypto_utils;
extern crate openssl;
extern crate rustc_serialize;
extern crate rand;
use crypto_utils::Crypto;
use num::BigInt;
use rustc_serialize::hex::ToHex;
use std::thread;
use std::io::*;

const LOCAL: &str = "127.0.0.1:6000";

pub struct Client {
    conn: TcpStream,
    addr: SocketAddr,
    username: Option<String>,
    crypto: crypto_utils::PrimeDiffieHellman
}

impl Client {
    pub fn new(socket: TcpStream, address: SocketAddr) -> Client {
        let conn = socket;
        let addr = address;
        let username = None;
        let crypto = crypto_utils::PrimeDiffieHellman::new();
        Client {
            conn,
            addr,
            username,
            crypto
        }
    }

    pub fn decrypt_msg(&self, ciphertext: &[u8]) -> String {
        let message = self.crypto.decrypt(ciphertext);
        let text = std::str::from_utf8(&message).expect("Error decrypting message!");
        println!("Decrypted message: {}", &text.to_string());
        return text.to_string();
    }

    pub fn send_message(&mut self, msg: String) {
        let msg_bytes = msg.as_bytes();
        let encrypted_msg = self.crypto.encrypt(msg_bytes);
        println!("Server Sent: {}", &encrypted_msg.to_hex());
        self.conn.write(&encrypted_msg).unwrap();
        return;
    }
    
    pub fn receive_message(&mut self) -> [u8; 16] {
        let mut data = [0 as u8; 16]; // using 16 byte buffer
        match self.conn.read(&mut data) {
            Ok(_) => {
                //let text = String::from_utf8(data.to_vec());
                //println!("Server Received: {}", &text.unwrap());
                return data;
            },
            Err(e) => {
                println!("Failed to receive data: {}", e);
                return data;
            }
        }
    }

    fn do_dh_handshake(&mut self) {
        let (mut priv_key, pubkey) = self.crypto.generate_keys();
        println!("Public Key: {}", &pubkey.to_hex());
        self.conn.write(&pubkey.to_vec()).unwrap();
        println!("Server sent the public key!");
        let b_bytes = self.receive_message();
        let other_pub_key = self.crypto.deserialize(&b_bytes);
        self.crypto.handshake(&mut priv_key, other_pub_key);
    }
}

pub struct Server {
    socket: TcpListener,
    clients: HashMap<SocketAddr, Client>,
    username_list: HashSet<String>,
}
fn main() {   
    //Testing 
    let mut server = Server::new();
    server.run();
}

impl Server {
    pub fn new() -> Server {
        // Start a TCP listener.
	    let socket = match TcpListener::bind(LOCAL) {
		    Ok(socket) => socket,
		    Err(e) => panic!("could not read start TCP listener: {}", e)
	    };
        let clients = HashMap::new();
        let username_list = HashSet::new();
        Server {
            socket,
            clients,
            username_list
        }
    }

    fn run(&mut self) {
        loop {
            // Wait for a connection, add it to a list of connections.
            // Select between existing sockets and handle that socket.
            // if it is a new socket, do the handshake, negotiate username,
            // and add it to the list of connections.
            for stream in self.socket.incoming() {
                match stream {
                    Ok(stream) => {
                        let addr = stream.peer_addr().unwrap();
                        let mut client = Client::new(stream, addr);
                       
                        thread::spawn(move || {
                            //connection succeeded
                            println!("Connection from {}", addr);
                           //self.handle_client(&mut client); //TODO
                       });
                       
                       client.do_dh_handshake();
                       //let encrypted = client.crypto.encrypt("sbarke".as_bytes());
                       //let text = client.crypto.decrypt(&encrypted);
                       //println!("{}", std::str::from_utf8(&text).unwrap().to_string());

                    },
                    Err(e) => {
                        let _ = writeln!(std::io::stderr(), "Connection failed: {}", e);
                    }
                }
            }
        }
    }

    pub fn negotiate_username(&mut self, client: &mut Client) -> Option<String> {
        client.send_message( "Enter username: {}".to_string());
        let username = &client.receive_message();
        //let mut username = Client::decrypt_msg(client.conn.read(&[u8]).unwrap());
        if username.is_empty() {
            return None;
        }
        let username_trimmed = username.to_hex().trim().to_string(); // TODO: remove to_hex
        if self.username_list.contains(&username_trimmed) {
            client.send_message("Username already taken!".to_string());
            self.negotiate_username(client);

        } else {
            client.username = Some(username_trimmed.clone());
            self.username_list.insert(username_trimmed.clone());
        }
        return Some(username_trimmed);
    }

    pub fn handle_client(&mut self, client: &mut Client) {
        // 1. Initiate the diffie-hellman exchange.
        client.do_dh_handshake();
        // 2. Receive a username.
        let username = self.negotiate_username(client);
        // 3. Check if username is available.
        if username.unwrap().is_empty() {
            self.close_connection(client);
            return;
        }
        //TODO
    }

    pub fn close_connection(&mut self, client: &mut Client) {
        println!("Closing connection {}", client.addr);
        match client.conn.shutdown(std::net::Shutdown::Both) {
            Ok(_) => {},
            Err(e) => {
                println!("Failed to close connection: {}", e);
            }
        }
        if self.username_list.contains(client.username.as_ref().unwrap()) {
            self.username_list.remove(client.username.as_ref().unwrap());
        }
        self.clients.remove(&client.addr);
    }

    pub fn handle_msg(&mut self, client: &mut Client, msg: String) {
        if msg.len() == 0 {
            return;
        } else if msg.starts_with('/'){
            let msg = msg.trim();
            if msg == "/quit" {
                self.close_connection(client);
                return;
            } else if msg == "/list" {
                client.send_message(
                    format!("Invalid command. Type /help for help.\n"));
                return;
            } else if msg == "/help" {
                client.send_message(
                    "
                    /quit - quit the chat
                    /list - list usernames
                    /help - show this help message".to_string()
                );
                return;
            } else {
                client.send_message("Invalid command! Type /help for help.\n".to_string());
            }
        } else {
            for (client_addr, _) in self.clients.iter() {
              if client_addr != &client.addr {
                    client.send_message(format!("{}: {}", client.username.as_ref().unwrap(), msg));
                }
            }    
        }
    }   
}