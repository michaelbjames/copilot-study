use std::io::Write;
use std::io::{self, *};
use std::net::TcpStream;
use std::sync::mpsc::{channel, Sender};
use std::thread;
extern crate openssl;
extern crate rand;
extern crate rustc_serialize;
use crypto_utils::{Crypto, PrimeDiffieHellman};
const LOCAL: &str = "127.0.0.1:4040";

pub struct EncryptedStream {
    socket: TcpStream,
    crypto: crypto_utils::PrimeDiffieHellman,
}

impl EncryptedStream {
    pub fn establish(mut socket: TcpStream) -> io::Result<Self> {
        let mut crypto = PrimeDiffieHellman::new();

        let b_bytes = {
            let mut data = [0_u8; 16]; // using 16 byte buffer
            socket.read_exact(&mut data)?;
            data
        };

        let other_pub_key = crypto.deserialize(&b_bytes);
        let (priv_key, pubkey) = crypto.generate_keys();
        socket.write_all(&pubkey.to_vec())?;

        crypto.handshake(&priv_key, &other_pub_key);
        println!("Handshake complete!");

        Ok(EncryptedStream { socket, crypto })
    }

    pub fn send(&mut self, msg: &str) -> io::Result<()> {
        let mut msg_bytes: Vec<u8> = msg.trim().as_bytes().to_vec();
        msg_bytes.push(msg_bytes.len() as u8); // add data length
        let encrypted_msg = self.crypto.encrypt(&msg_bytes);
        self.socket.write_all(&encrypted_msg)?;
        Ok(())
    }

    pub fn try_clone(&self) -> io::Result<Self> {
        let socket = self.socket.try_clone()?;

        Ok(EncryptedStream {
            socket,
            crypto: self.crypto.clone(),
        })
    }

    pub fn receive(&mut self) -> io::Result<Option<String>> {
        let raw = Self::receive_raw(&mut self.socket)?;
        let message = self.crypto.decrypt(&raw);
        let txt = std::str::from_utf8(&message)
            .ok()
            .map(str::trim)
            .map(String::from);
        println!("Received: {:?}", &txt);
        Ok(txt)
    }

    fn receive_raw(socket: &mut TcpStream) -> io::Result<Vec<u8>> {
        let mut data = vec![0_u8; 256]; // using 256 byte buffer
        socket.read(&mut data).map(|_| data)
    }
}

fn connect(channel: Sender<Message>) -> io::Result<()> {
    println!("Connecting to {}", LOCAL);
    let socket = match TcpStream::connect(LOCAL) {
        Ok(socket) => socket,
        Err(e) => panic!("could not connect to server: {}", e),
    };

    let enc_stream = EncryptedStream::establish(socket)?;

    let server_stream = enc_stream.try_clone()?;
    let stdin_server = enc_stream.try_clone()?;
    thread::spawn(move || handle_stream_server(server_stream, channel));
    thread::spawn(move || handle_stream_stdin(stdin_server));

    Ok(())
}

enum Message {
    Disconnected,
    Text(String),
}

fn handle_stream_server(
    mut enc_stream: EncryptedStream,
    channel: Sender<Message>,
) -> io::Result<()> {
    loop {
        let msg = match enc_stream.receive() {
            Ok(Some(txt)) => Message::Text(txt),
            Err(_) => Message::Disconnected,
            _ => {
                // ignored
                continue;
            }
        };

        channel.send(msg).unwrap();
    }
}

fn handle_stream_stdin(mut enc_stream: EncryptedStream) -> io::Result<()> {
    loop {
        let mut line = String::new();
        match std::io::stdin().read_line(&mut line).unwrap() {
            0 => continue,
            _ => {
                if let Err(e) = enc_stream.send(&line) {
                    eprintln!("Error sending message to server: {:?}", e);
                }
                println!("Client Sent! {:?}", &line);
            }
        };
    }
}

fn handle_msg(msg: Message) {
    match msg {
        Message::Disconnected => {
            println!("disconnected\n");
        }
        Message::Text(txt) => {
            println!("received: {}", txt);
        }
    }
}

fn main() {
    let (send, recv) = channel();
    thread::spawn(move || connect(send));

    while let Ok(msg) = recv.recv() {
        handle_msg(msg)
    }
}
