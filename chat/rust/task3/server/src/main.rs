use crypto_utils::{Crypto, PrimeDiffieHellman};
use std::collections::HashMap;
use std::io::{self, *};
use std::net::{Shutdown, SocketAddr, TcpListener, TcpStream};
use std::sync::mpsc::{channel, Sender};
use std::thread;

const LOCAL: &str = "127.0.0.1:4040";

pub struct EncryptedStream {
    socket: TcpStream,
    crypto: PrimeDiffieHellman,
}

impl EncryptedStream {
    pub fn establish(mut socket: TcpStream) -> io::Result<Self> {
        let mut crypto = PrimeDiffieHellman::new();

        let (priv_key, pubkey) = crypto.generate_keys();
        socket.write_all(&pubkey.to_vec())?;

        let b_bytes = {
            let mut data = [0_u8; 16]; // using 16 byte buffer
            socket.read_exact(&mut data)?;
            data
        };

        let other_pub_key = crypto.deserialize(&b_bytes);
        crypto.handshake(&priv_key, &other_pub_key);
        println!("Handshake complete!");

        Ok(EncryptedStream { socket, crypto })
    }

    pub fn close(&mut self) {
        if let Err(e) = self.socket.shutdown(Shutdown::Both) {
            eprintln!("Error shutting down socket: {:?}", e);
        }
    }

    pub fn send(&mut self, msg: &str) -> io::Result<()> {
        let mut msg_bytes: Vec<u8> = msg.trim().as_bytes().to_vec();
        msg_bytes.push(msg_bytes.len() as u8); // add data length
        let encrypted_msg = self.crypto.encrypt(&msg_bytes);
        self.socket.write_all(&encrypted_msg)?;
        println!("Sent: {}", &msg);
        Ok(())
    }

    pub fn try_clone(&self) -> io::Result<Self> {
        let socket = self.socket.try_clone()?;

        Ok(EncryptedStream {
            socket,
            crypto: self.crypto.clone(),
        })
    }

    pub fn recv(&mut self) -> io::Result<Option<String>> {
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

enum Message {
    Connected(EncryptedStream),
    Disconnected,
    Text(String),
}

fn accept(channel: Sender<(SocketAddr, Message)>) {
    loop {
        let socket = match TcpListener::bind(LOCAL) {
            Ok(socket) => socket,
            Err(e) => panic!("could not read start TCP listener: {}", e),
        };

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
    let mut enc_stream = EncryptedStream::establish(socket)?;
    let foreign_stream = enc_stream.try_clone()?;

    // Notify the server that we've established a connection
    channel
        .send((addr, Message::Connected(foreign_stream)))
        .unwrap();

    loop {
        let msg = match enc_stream.recv() {
            Ok(Some(txt)) => Message::Text(txt),
            Err(_) => Message::Disconnected,
            _ => {
                // ignored
                continue;
            }
        };

        channel.send((addr, msg)).unwrap();
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

#[derive(Default)]
struct ChatServer {
    clients: HashMap<SocketAddr, ClientConnection>,
}

impl ChatServer {
    pub fn new() -> Self {
        Default::default()
    }

    fn handle_msg(&mut self, addr: SocketAddr, msg: Message) {
        match msg {
            Message::Connected(stream) => {
                let mut client = ClientConnection {
                    stream,
                    username: None,
                };

                // We ignore the possible failure here because it'll come back to us via a disconnect later
                client.send("Enter username: ");

                self.clients.insert(addr, client);
            }
            Message::Disconnected => {
                self.clients.remove(&addr);
            }
            Message::Text(txt) => {
                let username = {
                    self.clients
                        .get_mut(&addr)
                        .expect("Text messages should only come from clients that are known")
                        .username
                        .clone()
                };
                let proposed_username = txt.clone();
                // Negotiating username
                if username == None {
                    // user name is taken
                    let is_unique = self
                        .clients
                        .values()
                        .find(move |c| c.username.as_ref() == Some(&txt))
                        .is_none();
                    let client = self
                        .clients
                        .get_mut(&addr)
                        .expect("Text messages should only come from clients that are known");
                    if !is_unique {
                        client.send("Username taken!\nEnter username: ");
                    } else {
                        client.username = Some(proposed_username);
                        client.send("Username granted!");
                    }
                } else {
                    self.handle_chat_msg(addr, &txt);
                }
            }
        }
    }

    pub fn handle_chat_msg(&mut self, addr: SocketAddr, msg: &str) {
        if msg.is_empty() {
            return;
        }
        if msg.starts_with('/') {
            let client = self.clients.get_mut(&addr).unwrap();

            if msg == "/quit" {
                client.stream.close();
                self.clients.remove(&addr);
            } else if msg == "/list" {
                for (_client_addr, client) in self.clients.iter_mut() {
                    client.send(&format!("Client username: {:?}", client.username));
                }
            } else if msg == "/help" {
                client.send(
                    "
                    /quit - quit the chat
                    /list - list usernames
                    /help - show this help message",
                );
            } else {
                client.send("Invalid command! Type /help for help.\n");
            }
        } else {
            // Invariant, we only call handle_chat_msg for clients with usernames
            let chat = {
                let uname = self.clients[&addr].username.as_ref().unwrap();
                format!("{}: {}", uname, msg)
            };

            for (client_addr, client) in self.clients.iter_mut() {
                if client_addr != &addr {
                    client.send(&chat);
                }
            }
        }
    }
}

fn main() {
    let (send, recv) = channel();
    thread::spawn(move || accept(send));

    let mut server = ChatServer::new();
    while let Ok((addr, msg)) = recv.recv() {
        server.handle_msg(addr, msg)
    }
}
