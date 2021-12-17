# copilot-study
Thanks for taking part in this study!
We want to understand how people interact with Copilot.
- When do you use Copilot?
- Do you trust its output?
  - If not, what would make you more confident?
- Do you plan your input or let it just work in the background?
- How confident are you about what you get back?

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

# Chat Server
MyRC is a secure chat client and server. Messages are encrypted and sent to all
connected clients. Clients pick a username by which they are identified. There
is only one big room for all clients. All clients should have unique usernames.

## Protocol
The server's protocol is simple:
1. Client and server perform a handshake to establish a shared secret key.
2. Server asks for a username
3. Client gives a username
4. Server sends a welcome message and all connected clients.

Messaging now commences at this point.

A user can quit either with the `/quit` command or by quitting the client (e.g.,
ctrl-c or ctrl-d).

## Handshake
The handshake establishes a shared secret key between the client and server.
This shared key is used as input to an AES-256 cipher in what's called `ECB`
mode. To find the shared secret, the handshake protocol is as follows:
Server -> Client:
{"type":"PrimeDiffieHellman", "key":<public-key-as-int>}
Client -> Server:
{"type":"PrimeDiffieHellman", "key":<public-key-as-int>}

The client and server each can take the other's public key, along with their own
private key, and generate a shared secret key.
Note: this is with the PrimeDiffieHellman algorithm, you'll implement both this
and the ECDiffieHellman algorithm.

## AES Cipher
This shared key is used as the key for an AES-256-ECB cipher.
The cipher takes in a byte string of plaintext and outputs a byte string of
ciphertext. This input to AES in ECB mode needs to be padded so it is always a
multiple of AES.block_size (16 bytes). Remember, this padding will need to be
removed after decryption, too.

All messages after the diffie hellman handshake are encrypted with this AES
cipher. Each client will have a different secret key with the server.

## Commands
A user can type any of the following commands for the desired effect:
/quit : disconnects. Same as ctrl-c or ctrl-d
/list : lists the connected other client usernames
/help : show this list


# Tasks
While implementing these tasks, you're welcome to (but not required to):
- Import extra libraries
- Look on the internet for API information / stackoverflow
- Write tests
- Write extra functions or classes
- Rename the solution files so you can test your work (e.g., renaming
  `crypto.py` and `task_crypto.py` so you can test your crypto work with the
  solution client/server).
- Run the solutions to test against (e.g., testing your client against the
  solution server)

Please DON'T:
- read the solution code

## Task 1 Implement DiffieHellman Key Exchange, 2 ways
The crypto library needs to be implemented.
### PrimeDiffieHellman
Create an implementation of this crypto class
using the traditional diffie-hellman key exchange protocol,
using prime numbers.
It works by implementing the following math:
Alice and Bob have already agreed on a prime, p, and a group generator number g.
    In this case, use g=2; and p can be any prime of your choosing
    [51,997]. We need small-ish numbers to use Python's built-in math
    operations.
Alice:
    1. pick some number priv_a [2,p-1]
    2. generate pub_a as g^priv_a mod p
Bob:
    1. pick some number priv_b [2,p-1]
    2. generate pub_b as g^priv_b mod p

3. Alice: generate shared secret as (pub_b^priv_a) mod p
3. Bob: generate shared secret as (pub_a^priv_b) mod p

### ECDiffieHellman
Create an implementation of this crypto class.
It uses an elliptic curve to do a diffie-hellman key exchange.
A Point on a Curve has two values: x and y.
A Curve forms a field of points, which for our purposes means it's
closed under multiplication.
This process works as follows:
Alice and Bob agree on a particular curve to use, "brainpoolP160r1"
This curve has a generator point, g, and a prime, p.

Alice's private key is a random number between 1 and the order of the field; curve.field.n
Alice computes her public key, which is the generator point on the curve
multiplied by her private key. The tinyec library will do the actual
elliptic curve math. The entire Point (x-y coords) is the public key.
When Alice gets Bob's public key, she can compute the shared secret.
Alice computes the shared secret Point as the product of her private key
and Bob's public key. The secret _value_ is the x-coordinate of that point.

## Task 2: Implement the Client
You have only the main function from the client and need to implement the rest.
You know the client needs to take an IP and a port number, and that it uses TCP.

After establishing a connection to the server, the client needs to facilitate
the diffie-hellman handshake to establish a secure connection. The client then
needs to listen for input from both the secure connection and also from the
console. Content from the server is put on screen and messages from the console
are sent to the server.

Import any packages you need. Remember, the cryptographic module provides the
interfaces and implementations you'll need for that part.

## Task 3 Implement the Server
The business logic of the server is missing. You'll need to implement it.
The server should be able to talk to many clients at once, and share messages
between them all. It should ensure that no two clients can have the same
username.