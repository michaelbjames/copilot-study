use crypto_utils::{Crypto, PrimeDiffieHellman};
use std::io::{self, *};
use std::net::{Shutdown, TcpStream};

pub struct EncryptedStream {
    socket: TcpStream,
    crypto: PrimeDiffieHellman,
}

impl EncryptedStream {
    // complete the Diffie-Hellman handshake before sending any data.

    pub fn dh_handshake(mut socket: TcpStream) -> io::Result<Self> {
        let mut crypto = PrimeDiffieHellman::new();

        let pubkey = crypto.init_keys();
        socket.write_all(&pubkey.to_vec())?;

        let pub_key_bytes = {
            let mut data = [0_u8; 16]; // using 16 byte buffer
            socket.read_exact(&mut data)?;
            data
        };

        crypto.handshake(&pub_key_bytes);
        println!("Handshake complete!");

        Ok(EncryptedStream { socket, crypto })
    }

    // close connection with client

    pub fn close(&mut self) {
        if let Err(e) = self.socket.shutdown(Shutdown::Both) {
            eprintln!("Error shutting down socket: {:?}", e);
        }
    }

    // send an encrypted message to the connected client.

    pub fn send(&mut self, msg: &str) -> io::Result<()> {
        let msg_bytes: Vec<u8> = msg.trim().as_bytes().to_vec();
        let encrypted_msg = self.crypto.encrypt(&msg_bytes);
        self.socket.write_all(&encrypted_msg)?;
        println!("Sent: {}", &msg);
        Ok(())
    }

    // clone the tcp stream, this function can be used to generate separate streams for each connected client

    pub fn try_clone(&self) -> io::Result<Self> {
        let socket = self.socket.try_clone()?;

        Ok(EncryptedStream {
            socket,
            crypto: self.crypto.clone(),
        })
    }

    // receive an encrypted message from the connected client and decrypt it

    pub fn recv(&mut self) -> io::Result<Option<String>> {
        let raw = self.receive_raw()?;
        if raw.is_empty() {
            return Ok(None);
        }
        let message = self.crypto.decrypt(&raw);
        let txt = std::str::from_utf8(&message).ok().map(String::from);
        println!("Received: {:?}", &txt);
        Ok(txt)
    }

    fn receive_raw(&mut self) -> io::Result<Vec<u8>> {
        let mut data = vec![0_u8; 1024];
        let bytes_read = self.socket.read(&mut data)?;
        Ok(data[..bytes_read].to_vec())
    }
}
