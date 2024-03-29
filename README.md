This repo contains the qualitative study materials for the paper [Grounded Copilot: How Programmers Interact with Code-Generating Models (OOPSLA 2023)](https://dl.acm.org/doi/pdf/10.1145/3586030).

# Copilot-Study
Thanks for taking part in this study!
We want to understand how people interact with Copilot.
- What kind of tasks do you use Copilot for?
- Do you actively provide input to Copilot or let it just work in the background?
- How confident are you about what you get back? How do you increase your confidence?
- What are the main pain points you would like to see improved in the future?

To get at these kinds of questions *and more* we've created a small application,
YOU'RE going to build (with Copilot's help).

Please read up to and including the ##Training Task section.
Your interviewer will tell you which problem you'll be working on after that.

## Organization
This project will be a set of tasks to accomplish with copilot.
```
/.
  chat/
    py/   <- python implementation
    rust/ <- rust implementation
  <task-name>/
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


# Task 3: Benford's Law
Benford's Law is an observation that the first digit of a number is likely to be
low. While this observation appears true in many datasets,
it is not true for all. The Fibonacci sequence observes Benford's Law, but
the reciprocal of consecutive numbers do not. You'll be plotting these two
sequences to see the difference.

First (in Rust), generate the Fibonacci sequence up to 180:
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

# Task 4: Advent of Code
## Advent of Code 2021, Day 14
### Part 1
The incredible pressures at this depth are starting to put a strain on your submarine. The submarine has polymerization equipment that would produce suitable materials to reinforce the submarine, and the nearby volcanically-active caves should even have the necessary input elements in sufficient quantities.

The submarine manual contains instructions for finding the optimal polymer formula; specifically, it offers a polymer template and a list of pair insertion rules (your puzzle input). You just need to work out what polymer would result after repeating the pair insertion process a few times.

For example:
```
NNCB

CH -> B
HH -> N
CB -> H
NH -> C
HB -> C
HC -> B
HN -> C
NN -> C
BH -> H
NC -> B
NB -> B
BN -> B
BB -> N
BC -> B
CC -> N
CN -> C
```
The first line is the polymer template - this is the starting point of the process.

The following section defines the pair insertion rules. A rule like AB -> C means that when elements A and B are immediately adjacent, element C should be inserted between them. These insertions all happen simultaneously.

So, starting with the polymer template NNCB, the first step simultaneously considers all three pairs:

The first pair (NN) matches the rule NN -> C, so element C is inserted between the first N and the second N.
The second pair (NC) matches the rule NC -> B, so element B is inserted between the N and the C.
The third pair (CB) matches the rule CB -> H, so element H is inserted between the C and the B.
Note that these pairs overlap: the second element of one pair is the first element of the next pair. Also, because all pairs are considered simultaneously, inserted elements are not considered to be part of a pair until the next step.

After the first step of this process, the polymer becomes NCNBCHB.

Here are the results of a few steps using the above rules:

Template:     NNCB
- After step 1: NCNBCHB
- After step 2: NBCCNBBBCBHCB
- After step 3: NBBBCNCCNBBNBNBBCHBHHBCHB
- After step 4: NBBNBNBBCCNBCNCCNBBNBBNBBBNBBNBBCBHCBHHNHCBBCBHCB
This polymer grows quickly.
- After step 5, it has length 97; After step 10, it has length 3073. After step 10, B occurs 1749 times, C occurs 298 times, H occurs 161 times, and N occurs 865 times; taking the quantity of the most common element (B, 1749) and subtracting the quantity of the least common element (H, 161) produces 1749 - 161 = 1588.

Apply 10 steps of pair insertion to the polymer template and find the most and least common elements in the result. What do you get if you take the quantity of the most common element and subtract the quantity of the least common element?

### Part 2
The resulting polymer isn't nearly strong enough to reinforce the submarine. You'll need to run more steps of the pair insertion process; a total of 40 steps should do it.

In the above example, the most common element is B (occurring 2192039569602 times) and the least common element is H (occurring 3849876073 times); subtracting these produces 2188189693529.

Apply 40 steps of pair insertion to the polymer template and find the most and least common elements in the result. What do you get if you take the quantity of the most common element and subtract the quantity of the least common element?
