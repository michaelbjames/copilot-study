use crypto_utils::{Crypto, PrimeDiffieHellman};
use std::io::Write;
use std::io::{self, *};
use std::net::TcpStream;
use std::sync::mpsc::{channel, Receiver, Sender};
use std::thread;
const LOCAL: &str = "127.0.0.1:4040";

pub struct ChatServer {
    socket: TcpStream,
    crypto: crypto_utils::PrimeDiffieHellman,
}

impl ChatServer {
    pub fn new() -> Self {
        let socket = match TcpStream::connect(LOCAL) {
            Ok(socket) => socket,
            Err(e) => panic!("could not connect to server: {}", e),
        };
        let crypto = PrimeDiffieHellman::new();
        ChatServer { socket, crypto }
    }

    /* Encrypt and send a message to the server */
    pub fn send(&mut self, msg: &str) -> io::Result<()> {
        let mut msg_bytes: Vec<u8> = msg.trim().as_bytes().to_vec();
        msg_bytes.push(msg_bytes.len() as u8); // add data length
        let encrypted_msg = self.crypto.encrypt(&msg_bytes);
        self.socket.write(&encrypted_msg)?;
        Ok(())
    }

    /* Receive a message from the server and decrypt */

    pub fn receive(&mut self) -> io::Result<Option<String>> {
        let raw = self.receive_raw()?;
        let message = self.crypto.decrypt(&raw);
        let txt = std::str::from_utf8(&message)
            .ok()
            .map(str::trim)
            .map(String::from);
        println!("Received: {:?}", &txt);
        Ok(txt)
    }

    fn receive_raw(&mut self) -> io::Result<Vec<u8>> {
        let mut data = vec![0_u8; 256]; // using 256 byte buffer
        self.socket.read(&mut data).map(|_| data)
    }

    fn try_clone(&self) -> io::Result<Self> {
        Ok(Self {
            socket: self.socket.try_clone()?,
            crypto: self.crypto.clone(),
        })
    }

    /** Complete the Diffie-Hellman handshake
        Return the key as bytes.
        Output must be 16 bytes long. (for a 128-bit AES key)
    */
    pub fn dh_handshake(&mut self) -> io::Result<()> {
        let b_bytes = {
            let mut data = [0_u8; 16]; // using 16 byte buffer
            self.socket.read(&mut data)?;
            data
        };

        let other_pub_key = self.crypto.deserialize(&b_bytes);
        let pubkey = self.crypto.init_keys();
        self.socket.write_all(&pubkey.to_vec())?;

        self.crypto.handshake(&other_pub_key);
        println!("Handshake complete!");
        Ok(())
    }
}

/* Spawn two threads for input from either stdin or the server */

fn connect(chat: ChatServer) -> io::Result<()> {
    let stream_clone1 = chat.try_clone()?;
    let stream_clone2 = chat.try_clone()?;
    thread::spawn(move || handle_stream_server(stream_clone1));
    thread::spawn(move || handle_stream_stdin(stream_clone2));

    Ok(())
}

fn handle_stream_server(mut chat: ChatServer) -> io::Result<()> {
    loop {
        let msg = match chat.receive() {
            Ok(Some(txt)) => {
                println!("received: {}", txt);
            }
            Err(_) => {
                println!("disconnected\n");
            }
            _ => {
                // ignored
                continue;
            }
        };
    }
}

fn handle_stream_stdin(mut chat: ChatServer) -> io::Result<()> {
    loop {
        let mut line = String::new();
        match std::io::stdin().read_line(&mut line).unwrap() {
            0 => continue,
            _ => {
                if let Err(e) = chat.send(&line) {
                    eprintln!("Error sending message to server: {:?}", e);
                }
                println!("Client Sent! {:?}", &line);
            }
        };
    }
}

fn main() {
    let (_, recv): (_, Receiver<Vec<u8>>) = channel();
    let mut chat = ChatServer::new();
    chat.dh_handshake();

    thread::spawn(move || connect(chat));
    loop {
        recv.recv();
    }
}
