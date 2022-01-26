use crypto_utils::{Crypto, PrimeDiffieHellman};
use std::env;
use std::io::Write;
use std::io::{self, *};
use std::net::TcpStream;
use std::sync::mpsc::{channel, Sender};
use std::thread;

pub struct EncryptedStream {
    socket: TcpStream,
    crypto: crypto_utils::PrimeDiffieHellman,
}

impl EncryptedStream {
    /** Complete the Diffie-Hellman handshake
        Return the key as bytes.
        Output must be 16 bytes long. (for a 128-bit AES key)
    */
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

    /* Encrypt and send a message to the server */

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

    /* Receive a message from the server and decrypt */

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

fn main() {
    let (send, recv) = channel();

    let args: Vec<String> = env::args().collect();
    let ip = &args[1];
    let port = &args[2];
    let address = format!("{}:{}", ip, port);

    thread::spawn(move || connect(send, &address));

    while let Ok(msg) = recv.recv() {
        handle_msg(msg)
    }
}
