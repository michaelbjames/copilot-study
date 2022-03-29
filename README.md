# copilot-study
Thanks for taking part in this study!
We want to understand how people interact with Copilot.
- What kind of tasks do you use Copilot for?
- Do you actively provide input to Copilot or let it just work in the background?
- How confident are you about what you get back? How do you increase your confidence?
- What are the main pain points you would like to see improved in the future?

To get at these kinds of questions *and more* we've created a small application,
YOU'RE going to build (with Copilot's help).

## Organization
This project will be a set of tasks to accomplish with copilot.
```
/.
  chat/
    py/   <- python implementation
    rust/ <- rust implementation
  task<N>/
    py/   <- python implementation
    rust/ <- rust implementation
```

# Before you begin
You'll need:
- VSCode/Neovim/Jetbrains IDE
- the Copilot plugin for your editor
- If doing python:
  - pip3
  - run `$ pip3 install -r requirements.txt`

# Tasks
While implementing these tasks, you're welcome to (but not required to):
- Import extra libraries
- Look on the internet for API information / stackoverflow
- Write tests
- Write extra functions or classes
- Run the solutions to test against (e.g., testing your client against the
  solution server)

Please DON'T:
- read the code of other tasks.
- read the solution code (under the `solution` directory in python)

## Training Task
This task is meant to familiarize you with Copilot, and how you might interact
with it. You task is to write the main function of the client chat application.
The main function should read in the two arguments from the command line: the
hostname and the port number. It does not need to actually do any networking,
just print out the hostname and the port. If both are not supplied, the main
function should show the usage message.

This is located under `training/`

```
$ python client localhost 4040
Connecting to localhost:4040

$ python client
Usage: client.py host port
```
It doesn't do anything other than print out the two arguments it was given. :-)

This is a time to check that your usual plugins are operating as you'd expect.



# Chat Server (Tasks 1, 2)

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

## Running the application

### Server
The server needs to be running first and can be invoked with:
- Python: `chat/py/task<n>$ python3 server.py`
- Rust: `chat/rust/server$ cargo run`

### Client
The client can be called with:
- Python: `chat/py/task<n>$ python3 client.py localhost 4040`
- Rust: `chat/rust/client$ cargo run localhost 4040`

You'll need to run multiple clients to see the chat room in action.
## Task 1 Implement the Server
You need to implement the server. It will be listening for connections on port
4040 over TCP. Any connection it makes, it will perform a handshake. It should ask for a
unique username; then it should send a welcome message to all connected clients. Any
message sent to the server from the client at this point should be sent to all
the other clients, unless it is a command.

As an example exchange:
```
Server: listening...
Client 1: <connects>
-⬆️  handled for you  ⬆️-
-⬇️ (if in python) to be implemented ⬇️-
Server: <send its public key>
Client 1: <send its public key>
-⬇️ (if in rust) to be implemented ⬇️-
Server(encrypted to Client 1): Please pick a username:
Client 1: MySuperCoolUsername
Server(to all): Welcome MySuperCoolUsername!
Client 2: <connects; handshakes; picks username>
Client 1: Hello!
Server(to all but Client 1): MySuperCoolUsername: Hello!
Client 1: /quit
```
### Commands

The following are the supported commands and their effect:
```
/quit : disconnects. Same as ctrl-c or ctrl-d
/list : lists the connected other client usernames
/help : show this list
```

All other commands are invalid, and their behavior is unspecified.


**You need to implement the function `run_client` (python) or `handle_msg` (rust) with the TODO under
`task1/server`**. The networking logic has already been implemented for you.
This function takes a message and which client sent it, it then deals with the
message according to the server specification above.

## Task 2: Implement the Client
You have only the main function from the client and need to implement the rest.
You know the client needs to take an IP and a port number, and that it uses TCP.

After establishing a connection to the server, the client needs to do its part
of the cryptographic handshake to establish a secure connection. The client then
needs to listen for input from both the secure network connection and also from the
console. Content from the server is put on screen and messages from the console
are sent to the server.

### Protocol

1. Client connects to server (`localhost:4040`).
2. Server sends its public key to the client.
3. Client sends its public key to the server.

At this point, a *shared secret* is generated, and all communication henceforth is encrypted with that secret.

4. Server asks for a username.
5. Client gives a username.
6. Server sends a welcome message to all connected clients.

Messaging commences at this point.

7. Client waits for a message from the server *or* user input from console.
8. If it gets a message from the server, the message is shown to the client.
9. Messages are sent to the server.
10. Server sends the message to all other connected users.

Some messages are commands, but they are all handled by the server.

As an example exchange:
```
Server: listening...
Client 1: <connects>
Server: <send its public key>
Client 1: <send its public key>
Server(encrypted to Client 1): Please pick a username:
Client 1: MySuperCoolUsername
Server(to all): Welcome MySuperCoolUsername!
Client 2: <connects; handshakes; picks username>
Client 1: Hello!
Server(to all but Client 1): MySuperCoolUsername: Hello!
Client 1: /quit
```

### Using the crypto library
The Crypto class encapsulates all the encryption functionality you'll need. It provides 4 methods:

`init_keys`: The first of a two-part procedure to generate the shared secret. This method generates a pair of a public and private key. It returns the public key and stores the private key internally.

`handshake`: The second part of the procedure to generate the shared secret.
This method takes a public key from the other party and combines it with the
previously generated private key. The resulting shared secret is stored
internally. After calling this method, you can call encrypt and decrypt to
communicate securely with the other party.

`encrypt`: This method takes a message as bytes and encrypts it. It returns a ciphertext as bytes.

`decrypt`: This method takes a ciphertext as bytes and returns a message as bytes.



# Task 3
You are playing the role of a data scientist. You need to create a couple plots.
Your subtasks are:
1. Create a fibonacci function. It should be fast enough to produce fib(50) in
  <1 second (use some memoization technique).
2. Plot the log of the fibonacci function up to 50.

3. Create a dataset from the _first digit_ of each fibonacci number up to 50.
4. Plot the dataset as a histogram. (This distribution demonstrates Benford's Law).

### Python
You'll use matplotlib to create the plots.

### Rust
You'll use the plotters library to create the plots.

# Task 4
Benford's Law is an observation that the first digit of a number is likely to be
low. While this observation appears true in many datasets,
it is not true for all. The fibonacci sequence observes Benford's Law, but
the reciprocal of consecutive numbers do not. You'll be plotting these two
sequences to see the difference.

First (in Rust), generate the fibonacci sequence up to 180:
fib(180) = 18547707689471986212190138521399707760
- It should be fast enough to run in <1 second
- Write to a file (fib.txt)

Second (in Python), plot this data as a histogram of the first digits.
- Get the first digit of each number
- Plot it as a histogram in matplotlib

Third (in Rust), generate the reciprocal of numbers 2,3,...,181,182:
- You'll get 0.5, 0.333333333, .... 0.00549450549
- Write these to a file (inverse.txt)

Fourth (in Python), plot this data as a histogram of the first digits, on top of
the previous plot.
- Ignore leading zeros
- Get the first digit of each number
- Plot it as a histogram in matplotlib
  - Both plots should be visible at the same time!

# Task 5

### Part 1
A submarine can take a series of commands like forward 1, down 2, or up 3:

forward X increases the horizontal position by X units.
down X increases the depth by X units.
up X decreases the depth by X units.
Note that since you're on a submarine, down and up affect your depth, and so they have the opposite result of what you might expect.

The submarine seems to already have a planned course (your puzzle input). You should probably figure out where it's going. For example:
```
forward 5
down 5
forward 8
up 3
down 8
forward 2
```
Your horizontal position and depth both start at 0. The steps above would then modify them as follows:

forward 5 adds 5 to your horizontal position, a total of 5.
down 5 adds 5 to your depth, resulting in a value of 5.
forward 8 adds 8 to your horizontal position, a total of 13.
up 3 decreases your depth by 3, resulting in a value of 2.
down 8 adds 8 to your depth, resulting in a value of 10.
forward 2 adds 2 to your horizontal position, a total of 15.
After following these instructions, you would have a horizontal position of 15 and a depth of 10. (Multiplying these together produces 150.)

Calculate the horizontal position and depth you would have after following the planned course. What do you get if you multiply your final horizontal position by your final depth?

### Part 2
Based on your calculations, the planned course doesn't seem to make any sense. You find the submarine manual and discover that the process is actually slightly more complicated.

In addition to horizontal position and depth, you'll also need to track a third value, aim, which also starts at 0. The commands also mean something entirely different than you first thought:

down X increases your aim by X units.
up X decreases your aim by X units.
forward X does two things:
It increases your horizontal position by X units.
It increases your depth by your aim multiplied by X.
Again note that since you're on a submarine, down and up do the opposite of what you might expect: "down" means aiming in the positive direction.

```
forward 5
down 5
forward 8
up 3
down 8
forward 2
```

Now, the above example does something different:

forward 5 adds 5 to your horizontal position, a total of 5. Because your aim is 0, your depth does not change.
down 5 adds 5 to your aim, resulting in a value of 5.
forward 8 adds 8 to your horizontal position, a total of 13. Because your aim is 5, your depth increases by 8*5=40.
up 3 decreases your aim by 3, resulting in a value of 2.
down 8 adds 8 to your aim, resulting in a value of 10.
forward 2 adds 2 to your horizontal position, a total of 15. Because your aim is 10, your depth increases by 2*10=20 to a total of 60.
After following these new instructions, you would have a horizontal position of 15 and a depth of 60. (Multiplying these produces 900.)

Using this new interpretation of the commands, calculate the horizontal position and depth you would have after following the planned course. What do you get if you multiply your final horizontal position by your final depth?