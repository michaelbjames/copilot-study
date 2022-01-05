use std::net::TcpStream;
use std::io::{Write};
use std::time::{Duration};
use std::thread;
pub use bp256::r1::BrainpoolP256r1;
extern crate openssl;
extern crate rustc_serialize;
extern crate rand;
use std::io::*;
const LOCAL: &str = "127.0.0.1:6000";

pub struct Chat {
    socket: TcpStream,
}

impl Chat {

    pub fn new(socket: TcpStream) -> Chat {
        Chat { socket }
    }
    
    pub fn receive(&mut self) {
        //let mut data: Vec<u8> = Vec::new();
        let mut data = [0 as u8; 16]; // using 6 byte buffer
        match self.socket.read(&mut data) {
            Ok(_) => {
                let message = crypto_utils::Crypto::decrypt(&data);
                //let text = std::str::from_utf8(&message).expect("Error decrypting message!");
                //println!("Client Received!: {}", &text.to_string());
                let mut line = String::new();
                match std::io::stdin().read_line(&mut line).unwrap() {
                    0 => return,
                    _ => {
                        self.send(line);
                    }
                }
            },
            Err(e) => {
                println!("Failed to receive data: {}", e);
                return;
            }
        }
    }
    pub fn send(&mut self, line: String) {
        let msg = line.trim().to_string();
        println!("Parsed from stdin {}", msg);
        let msg_bytes = msg.as_bytes();
        let encrypted_msg = crypto_utils::Crypto::encrypt(msg_bytes);
        //println!("Client Sent: {}", &encrypted_msg.to_hex());
        self.socket.write(&encrypted_msg).unwrap(); //TODO: fix this!
        return;
    }
}

fn main() {
    let stream = TcpStream::connect(LOCAL).expect("Could not connect to server");
    let mut client = Chat::new(stream.try_clone().unwrap());

    let delay = Duration::from_millis(1000);
    loop {
        client.receive();
        thread::sleep(delay);
    }
}