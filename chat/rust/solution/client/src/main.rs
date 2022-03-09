use crypto_utils::{Crypto, PrimeDiffieHellman};
use std::env;
use std::io::Write;
use std::io::{self, *};
use std::net::TcpStream;
use std::sync::mpsc::{channel, Receiver};
use std::thread;

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
        println!("Sent: {}", &msg);
        Ok(())
    }

    /* Receive a message from the server and decrypt */

    pub fn receive(&mut self) -> io::Result<Option<String>> {
        let raw = self.receive_raw()?;
        if raw.is_empty() {
            return Ok(None);
        }
        let message = self.crypto.decrypt(&raw);
        let txt = std::str::from_utf8(&message).ok().map(String::from);
        Ok(txt)
    }

    fn receive_raw(&mut self) -> io::Result<Vec<u8>> {
        let mut data = vec![0_u8; 1024];
        let bytes_read = self.socket.read(&mut data)?;
        Ok(data[..bytes_read].to_vec())
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
        let pub_key_bytes = {
            let mut data = [0_u8; 16]; // using 16 byte buffer
            self.socket.read(&mut data)?;
            data
        };

        let pubkey = self.crypto.init_keys();
        self.socket.write_all(&pubkey.to_vec())?;

        self.crypto.handshake(&pub_key_bytes);
        println!("Handshake complete!");
        Ok(())
    }
}

/* Spawn two threads for input from either stdin or the server */

fn accept_input(chat: ChatServer) -> io::Result<()> {
    let stream_clone1 = chat.try_clone()?;
    let stream_clone2 = chat.try_clone()?;
    thread::spawn(move || handle_stream_server(stream_clone1));
    thread::spawn(move || handle_stream_stdin(stream_clone2));

    Ok(())
}

fn handle_stream_server(mut chat: ChatServer) {
    loop {
        match chat.receive() {
            Ok(Some(txt)) => {
                println!("received: {}", txt);
            }
            Ok(None) => {
                println!("disconnected\n");
                break;
            }
            _ => {}
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
    chat.dh_handshake();

    thread::spawn(move || accept_input(chat));
    loop {
        recv.recv();
    }
}
