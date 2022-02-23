use encstream::EncryptedStream;
use std::collections::HashMap;
use std::io::{self, *};
use std::net::{Shutdown, SocketAddr, TcpListener, TcpStream};
use std::sync::mpsc::{channel, Sender};
use std::thread;

const LOCAL: &str = "127.0.0.1:4040";

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
    let mut enc_stream = EncryptedStream::dh_handshake(socket)?;
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
                    let is_unique = !self
                        .clients
                        .values()
                        .any(move |c| c.username.as_ref() == Some(&txt));
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
            if msg == "/quit" {
                let client = self.clients.get_mut(&addr).unwrap();
                client.stream.close();
                self.clients.remove(&addr);
            } else if msg == "/list" {
                let usernames = self
                    .clients
                    .iter()
                    .map(|c| c.1.username.as_ref().unwrap())
                    .collect::<Vec<&String>>();
                let username_list = format!("Users: {:?}", usernames);
                let client = self.clients.get_mut(&addr).unwrap();
                client.send(&username_list);
            } else if msg == "/help" {
                let client = self.clients.get_mut(&addr).unwrap();

                client.send(
                    "
                    /quit - quit the chat
                    /list - list usernames
                    /help - show this help message",
                );
            } else {
                let client = self.clients.get_mut(&addr).unwrap();

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
    // Create a channel to send messages to the server
    let (send, recv) = channel();
    thread::spawn(move || accept(send));

    let mut server = ChatServer::new();
    while let Ok((addr, msg)) = recv.recv() {
        server.handle_msg(addr, msg)
    }
}
