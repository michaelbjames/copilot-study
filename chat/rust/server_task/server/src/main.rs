use encstream::EncryptedStream;
use std::collections::HashMap;
use std::io::{self, *};
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::sync::mpsc::{channel, Sender};
use std::thread;

const LOCAL: &str = "127.0.0.1:4040";

#[derive(Default)]
struct ChatServer {
    clients: HashMap<SocketAddr, ClientConnection>,
}

impl ChatServer {
    pub fn new() -> Self {
        Default::default()
    }

    fn handle_msg(&mut self, addr: SocketAddr, msg: Message) {
        //TODO
    }
}

struct ClientConnection {
    stream: EncryptedStream,
    username: Option<String>,
}

impl ClientConnection {
    fn send(&mut self, txt: &str) {
        if let Err(e) = self.stream.send(txt) {
            eprintln!("Error sending message to client: {:?}", e);
        }
    }
}
enum Message {
    Connected(EncryptedStream),
    Disconnected,
    Text(String),
}

fn accept(channel: Sender<(SocketAddr, Message)>) {
    loop {
        // create a new socket to accept connections
        let socket = match TcpListener::bind(LOCAL) {
            Ok(socket) => socket,
            Err(e) => panic!("could not read start TCP listener: {}", e),
        };

        // accept connections and process them using separate threads
        for stream in socket.incoming() {
            match stream {
                Ok(stream) => {
                    let local_channel = channel.clone();
                    thread::spawn(move || handle_stream(stream, local_channel));
                }
                Err(e) => {
                    eprintln!("Accepting socket shutdown {}", e);
                }
            }
        }
    }
}

fn handle_stream(socket: TcpStream, channel: Sender<(SocketAddr, Message)>) -> io::Result<()> {
    let addr = socket.peer_addr()?;
    let mut enc_stream = EncryptedStream::dh_handshake(socket)?;
    let foreign_stream = enc_stream.try_clone()?;

    // notify the server that we've established a connection
    channel
        .send((addr, Message::Connected(foreign_stream)))
        .unwrap();

    loop {
        let msg = match enc_stream.recv() {
            Ok(Some(txt)) => Message::Text(txt),
            Ok(None) => {
                drop(Message::Disconnected);
                break;
            }
            _ => {
                continue;
            }
        };

        channel.send((addr, msg)).unwrap();
    }

    Ok(())
}

fn main() {
    // create a channel to send messages to the server
    let (send, recv) = channel();
    thread::spawn(move || accept(send));

    let mut server = ChatServer::new();
    while let Ok((addr, msg)) = recv.recv() {
        server.handle_msg(addr, msg)
    }
}
