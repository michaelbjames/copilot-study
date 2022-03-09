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
    // TODO
}

fn accept_input(chat: ChatServer) {
    //TODO
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
