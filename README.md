# copilot-study
Thanks for taking part in this study!
We want to understand how people interact with Copilot.
- What kind of tasks do you use Copilot for?
- Do you actively provide input to Copilot or let it just work in the background?
- How confident are you about what you get back? How do you increase your confidence?
- What are the main pain points you would like to see improved in the future?

To get at these kinds of questions *and more* we've created a small application,
YOU'RE going to build (with Copilot's help).

You'll be writing a secure instant message application.

## Organization
This project will be a set of tasks to accomplish with copilot.
```
/.
  chat/
    py/   <- python implementation
    rust/ <- rust implementation
```

# Before you begin
You'll need:
- VSCode
- the Copilot plugin for VSCode
- If doing python:
  - pip3
  - run `chat/py$ pip3 install -r requirements.txt`

# Chat Server

MyRC is a secure chat application.
Multiple clients connect to a single server.
When a client sends a chat message,
it is broadcast to all other connected clients
(that is, there is a single chat room for everyone).
Each client picks a username, which must be unique.
All messages are encrypted.

## Architecture
There are three main components to this application:
- The server: listens for connections and manages the chat room.
- The client: connects to the server; listens to user input and relays messages to/from the server.
- The crypto library: both client and server rely on this library to encrypt and decrypt messages.

## Protocol

1. Client connects to server (`localhost:4040`).
2. Server sends its public key to the client.
3. Client sends its public key to the server.

At this point, a *shared secret* is generated, and all comunication henceforth is encrypted with that secret.

3. Server asks for a username.
4. Client gives a username.
5. Server sends a welcome message to all connected clients.

Messaging commences at this point.

6. Client waits for a message from the server *or* user input from console.
7. If it gets a message from the server, the message is shown to the client.
8. If it gets input from the user, and the input starts with a `/`, it is interpreted as a *command* (see below).
9. Otherwise, the input is interpreted as a *message* and sent to the server.
10. Server sends the message to all other connected users.

### Commands

The following are the supported commands and their effect:
```
/quit : disconnects. Same as ctrl-c or ctrl-d
/list : lists the connected other client usernames
/help : show this list
```

All other commands are invalid, and their behavior is unspecified.

## Crypto Library
The `Crypto` class encapsulates all the encryption functionality. It provides 4 methods:

- `init_keys`: The first of a two-part procedure to generate the shared secret.
  This method generates a pair of a public and private key.
  It returns the public key and stores the private key internally.
- `handshake`: The second part of the procedure to generate the shared secret.
  This method takes a public key **from the other party**
  and combines it with the previously generated private key.
  The resulting shared secret is stored internally.
  After calling this method, you can call `encrypt` and `decrypt`
  to communicate securely with the party whose public key was used in this step.
- `encrypt`: This method takes a message as bytes and encrypts it.
  It returns a ciphertext as bytes.
- `decrypt`: This method takes a ciphertext as bytes
  and returns a message as bytes.

## Running the application

### Server
The server needs to be running first and can be invoked with:
- Python: `chat/py$ python3 server.py`
- Rust: `chat/rust/server$ cargo run`

### Client
The client can be called with:
- Python: `chat/py$ python3 client.py localhost 4040`
- Rust: `chat/rust/client$ cargo run localhost 4040`

# Tasks
While implementing these tasks, you're welcome to (but not required to):
- Import extra libraries
- Look on the internet for API information / stackoverflow
- Write tests
- Write extra functions or classes
- Run the solutions to test against (e.g., testing your client against the
  solution server)

Please DON'T:
- read the solution code. It's in the same directory as your tasks so you can
  test against them, and use the solutions in your imports.

## Training Task
This task is meant to familiarize you with Copilot, and how you might interact
with it. You task is to write the main function of the client chat application.
The main function should read in the two arguments from the command line: the
hostname and the port number. It does not need to actually do any networking,
just print out the hostname and the port. If both are not supplied, the main
function should show the usage message.

```
$ python client localhost 4040
Connecting to localhost:4040

$ python client
Usage: client.py host port
```

## Task 1 Implement the Server
You need to implement the server. It should be listening for connections on port
4040 over TCP. Any connection it makes, it should perform a handshake; ask for a
unique username; and then send a welcome message to all connected clients. Any
message sent to the server should be sent to all the other clients.

The server should support the following commands:
```
- /quit: disconnects the client (same as ctrl-d or EOF)
- /list: list all connected clients (this message is only sent to the asking client)
- /help: show this list
```
As an example exchange:
```
Server: listening...
Client 1: <connects>
Server: <handshake: sends its public-key>
Client 1: <handshake: sends its public-key>
Server(encrypted to Client 1): Please pick a username:
Client 1: MySuperCoolUsername
Server(to all): Welcome MySuperCoolUsername!
Client 2: <connects; handshakes; picks username>
Client 1: Hello!
Server(to all but Client 1): MySuperCoolUsername: Hello!
```

## Task 2 Implement DiffieHellman Key Exchange
The crypto library needs to be implemented.
The `Crypto` class has stubs for unimplemented methods that are called by the
interface functions. The unimplemented methods will implement the
diffie-hellman key exchange math.

It works by implementing the following math:

Alice and Bob have already agreed on a prime, `p`,
and a group generator number `g`.
In this case, use `g=2`; and p can be any prime of your choosing in the range [51,997]. We need
small-ish numbers to use Python's built-in math operations.

Alice:
1. pick some number `priv_a` in the range [2,p-1]
2. generate `pub_a` as `g` ^ `priv_a` mod `p`

Bob:
1. pick some number `priv_b` in the range [2,p-1]
2. generate `pub_b` as `g`^`priv_b` mod `p`


To generate their shared secret:
- Alice: generate shared secret as (`pub_b`^`priv_a`) mod `p`
- Bob: generate shared secret as (`pub_a`^`priv_b`) mod `p`

## Task 3: Implement the Client
You have only the main function from the client and need to implement the rest.
You know the client needs to take an IP and a port number, and that it uses TCP.

After establishing a connection to the server, the client needs to facilitate
the diffie-hellman handshake to establish a secure connection. The client then
needs to listen for input from both the secure connection and also from the
console. Content from the server is put on screen and messages from the console
are sent to the server.

