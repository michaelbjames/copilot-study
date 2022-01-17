use std::io::Write;
use std::thread;
use std::net::{Shutdown, SocketAddr, TcpStream};
use std::time::Duration;
extern crate openssl;
extern crate rand;
extern crate rustc_serialize;
use crypto_utils::Crypto;
use std::io::*;
const LOCAL: &str = "127.0.0.1:6000";

pub struct Chat {
    socket: TcpStream,
    crypto: crypto_utils::PrimeDiffieHellman,
}

impl Chat {
    pub fn new(socket: TcpStream) -> Chat {
        Chat {
            socket,
            crypto: crypto_utils::PrimeDiffieHellman::new(),
        }
    }

    pub fn receive_message(&mut self) -> [u8; 256] {
        let mut data = [0 as u8; 256]; // using 256 byte buffer
        match self.socket.read(&mut data) {
            Ok(_) => {
                return data;
            }
            Err(e) => {
                println!("Failed to receive data: {}", e);
                return data;
            }
        }
    }

    pub fn decrypt_msg(&self, ciphertext: &[u8]) -> String {
        let message = self.crypto.decrypt(ciphertext);
        let mut output = std::str::from_utf8(&message).unwrap();
        return output.to_string();
    }

    pub fn receive(&mut self) {
        let mut data = [0 as u8; 256]; // using 256 byte buffer
        match self.socket.read(&mut data) {
            Ok(_) => {
                let message = self.decrypt_msg(&data);
                println!("Client Received: {}", &message.to_string());
                let mut line = String::new();
                match std::io::stdin().read_line(&mut line).unwrap() {
                    0 => assert!(true),
                    _ => {
                        println!("Client Sent: {}", &line);
                        self.send(&line);
                    }
                }
            }
            Err(e) => {
                println!("Failed to receive data: {}", e);
            }
        }
    }

    pub fn send(&mut self, line: &str) {
        let mut msg_bytes: Vec<u8> = line.as_bytes().to_vec();
        msg_bytes.push(line.len() as u8); // add data length
        let encrypted_msg = self.crypto.encrypt(&msg_bytes);
        self.socket.write(&encrypted_msg).unwrap();
        return;
    }

    pub fn dh_handshake(&mut self) {
        let mut ga_wire = {
            let mut data = [0 as u8; 16]; // using 16 byte buffer
            self.socket.read(&mut data);
            data
        };
        let ga = self.crypto.deserialize(&ga_wire);
        let (mut priv_key, pubkey) = self.crypto.generate_keys();
        self.socket.write(&pubkey.to_vec()).unwrap();
        self.crypto.handshake(&mut priv_key, &ga);
        println!("Handshake complete!");
    }
}

fn main() {
    let stream = TcpStream::connect(LOCAL).expect("Could not connect to server");
    let mut client = Chat::new(stream.try_clone().unwrap());

    client.dh_handshake();
    loop {
        client.receive();
    }
}
