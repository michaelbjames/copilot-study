use crypto_utils::{Crypto, PrimeDiffieHellman};
use std::io::Write;
use std::io::{self, *};
use std::net::TcpStream;
use std::sync::mpsc::{channel, Receiver};
use std::thread;
use std::env;

pub struct ChatServer {
    socket: TcpStream,
    crypto: crypto_utils::PrimeDiffieHellman,
}

impl ChatServer {
    pub fn new(address: &str) -> Self {
        let socket = match TcpStream::connect(address) {
            Ok(socket) => socket,
            Err(e) => panic!("could not connect to server: {}", e),
        };
        let crypto = PrimeDiffieHellman::new();
        ChatServer { socket, crypto }
    }

    /* Encrypt and send a message to the server */
    pub fn send(&mut self, msg: &str) -> io::Result<()> {
        let msg_bytes: Vec<u8> = msg.trim().as_bytes().to_vec();
        let encrypted_msg = self.crypto.encrypt(&msg_bytes);
        self.socket.write(&encrypted_msg)?;
        Ok(())
    }

    /* Receive a message from the server and decrypt */

    pub fn receive(&mut self) -> io::Result<()> {
        let raw = self.receive_raw()?;
        let message = self.crypto.decrypt(&raw);
        let txt = std::str::from_utf8(&message);
        println!("{:?}", &txt.unwrap());
        Ok(())
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
        match chat.receive() {
            Ok(_) => {
                println!("received");
            }
            Err(_) => {
                println!("disconnected\n");
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
    let args: Vec<String> = env::args().collect();
    let ip = &args[1];
    let port = &args[2];
    let address = format!("{}:{}", ip, port);

    let mut chat = ChatServer::new(&address);
    chat.dh_handshake().expect("Error in DH handshake");

    thread::spawn(move || connect(chat));
    loop {
        recv.recv().expect_err("Error receiving message");
    }
}
