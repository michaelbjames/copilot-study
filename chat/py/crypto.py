
#!/usr/bin/env python3

from sys import byteorder
from Crypto.Cipher import AES
from Crypto.Util import Padding
from tinyec import registry
from tinyec import ec
import random
import json
import math
import struct
import gmpy2
# gmpy2.get_context().precision=128
from gmpy2 import mpfr
from gmpy2 import mpz

BYTE_ORDER = "big"
DH_MESSAGE_SIZE_BYTES = 32

class Crypto(object):
    def __init__(self):
        self.key = None
        self.cipher = None

    def encrypt(self, message):
        """
        Encrypt a message using the shared secret.
        Input: message:bytes
        Output: ciphertext:bytes
        """
        assert self.cipher is not None
        padded = Padding.pad(message, AES.block_size)
        return self.cipher.encrypt(padded)

    def decrypt(self, cipherbytes):
        """
        Decrypt a message using the shared secret.
        Input: cipherbytes:bytes
        Output: message:bytes or None if the message is empty
        """
        assert self.cipher is not None
        padded = self.cipher.decrypt(cipherbytes)
        if len(padded) == 0:
            return None
        return Padding.unpad(padded, AES.block_size)

    @classmethod
    def serialize_key(cls, key):
        """
        Input: a public key to be sent to the other party
        Output: a byte string representing the public key and metadata.
        How:
        Create a JSON object with the following format:
        {
            "type": <str>
            "key": <key object>
        }
        then return it as a byte string.
        """
        key_type = cls.__name__
        key = {
            "type": key_type,
            "key": cls._serialize_key_obj(key)
        }
        return json.dumps(key).encode()

    @classmethod
    def deserialize_key(cls, key_repr):
        """
        Input: a byte string representing a public key and metadata.
        Output: a public key object.
        """
        key_obj = json.loads(key_repr)
        key_type = key_obj["type"]
        key_bytes = key_obj["key"]
        if key_type != cls.__name__:
            raise ValueError("Invalid key type")
        return cls._deserialize_key_obj(key_bytes)

    def handshake(self):
        """
        Facilitate a cryptographic handshake between two parties.
        This will generate a private key and a public key, and
        provide a way to compute the shared secret.
        Output: (public_key:bytes, continuation:callable(bytes)->())
            The continuation accepts the other party's public key
            It will then compute the shared secret and initialize the cipher.

        The actual math is deferred to a subclass.
        """
        priv_key = self._gen_priv_key()
        pub_key = self._mk_pub_key(priv_key)
        print("Public key:", pub_key)
        def complete_handshake(other_pub_key_bytes):
            other_pub_key = type(self).deserialize_key(other_pub_key_bytes)
            self.key = self._compute_shared_secret(priv_key, other_pub_key)
            # self.key = shared_secret.to_bytes(DH_MESSAGE_SIZE_BYTES, byteorder=BYTE_ORDER)
            self._init_cipher(self.key)
            print("Handshake complete: {}".format(self.key.hex()))
            return
        pubkey_bytes = type(self).serialize_key(pub_key)
        return (pubkey_bytes, complete_handshake)

    def _init_cipher(self, key):
        self.cipher = AES.new(key, AES.MODE_ECB)

    @classmethod
    def _serialize_key_obj(cls, key):
        """
        Input: a public key object
        Output: a bytes object representing the public key
        """
        NotImplementedError()

    @classmethod
    def _deserialize_key_obj(cls, key_bytes):
        """
        Input: a bytes object representing a public key
        Output: a public key object
        """
        NotImplementedError()

    def _gen_priv_key(self):
        """
        Output: a private key object
        """
        NotImplementedError()

    def _mk_pub_key(self, priv_key):
        """
        Input: a private key object
        Output: a public key object
        """
        NotImplementedError()

    def _compute_shared_secret(self, priv_key, other_pub_key):
        """
        Input: a private key object, and a public key object
        Output: bytes of a shared secret. Output must be exactly 32 bytes long.
        """
        NotImplementedError()

class PrimeDiffieHellman(Crypto):
    def __init__(self):
        super().__init__()
        self.p = 997
        self.g = 2

    @classmethod
    def _serialize_key_obj(cls, key):
        return key

    @classmethod
    def _deserialize_key_obj(cls, key):
        return int(key)

    def _gen_priv_key(self):
        return random.randint(1, self.p - 1)

    def _mk_pub_key(self, priv_key):
        return (self.g ** priv_key) % self.p

    def _compute_shared_secret(self, priv_key, other_pub_key):
        secret_num = (other_pub_key ** priv_key) % self.p
        return secret_num.to_bytes(AES.block_size, byteorder=BYTE_ORDER)

class ModOneDiffieHellman(Crypto):
    def __init__(self):
        super().__init__()
        # gmpy2.get_context().precision=128
        # N cannot be larger than 10 otherwise we get some strange rounding error.
        self.n = 8
        # x is a transcendental number, we'll use pi from gmpy2
        self.x = gmpy2.const_pi()

    @classmethod
    def _serialize_key_obj(cls, key):
        return str(gmpy2.digits(key)[0])

    @classmethod
    def _deserialize_key_obj(cls, key_repr):
        return mpfr("0." + key_repr)

    def _gen_priv_key(self):
        # generate a random int from 2^(n-1) to (2^n)-1
        a = random.randint(2 ** (self.n - 1), (2 ** self.n)-1)
        priv_key = mpfr(a)
        return mpfr(str(priv_key))

    def _mk_pub_key(self, priv_key):
        a_prime = gmpy2.mod(gmpy2.mul(priv_key,self.x), 1)
        return a_prime

    def _compute_shared_secret(self, priv_key, other_pub_key):
        print("priv_key: {}".format(priv_key))
        print("other_pub_key: {}".format(other_pub_key))
        if priv_key == other_pub_key:
            print("priv_key == other_pub_key")
            raise ValueError("Private and public keys are the same")
        k = gmpy2.mul(priv_key, other_pub_key)
        k_prime = gmpy2.mod(k,1)
        k_prime_hex = gmpy2.digits(k_prime)[0]

        print("k_prime: {}".format(k_prime))
        # k_prime_str = str(k_prime)[2:]  # remove the 0. prefix
        # k_prime_hex = hex(int(k_prime_str))[2:]
        print("k_prime_hex: {}".format(k_prime_hex))

        key_size_bytes = AES.key_size[0]
        # ensure the length of k_prime_hex is exactly 2*key_size_bytes
        if len(k_prime_hex) < 2*key_size_bytes:
            k_prime_hex = k_prime_hex.zfill(2*key_size_bytes)
        elif len(k_prime_hex) > 2*key_size_bytes:
            k_prime_hex = k_prime_hex[:2*key_size_bytes]
        return bytes.fromhex(k_prime_hex)

class ECDiffieHellman(Crypto):
    curve = registry.get_curve("brainpoolP160r1")
    key_size = math.ceil(math.log2(curve.g.p))
    def __init__(self):
        super().__init__()
        self.generator = None
        self.secret = None

    @classmethod
    def _serialize_key_obj(cls, key):
        return {
            "x": key.x,
            "y": key.y,
        }

    @classmethod
    def _deserialize_key_obj(cls, key):
        return ec.Point(cls.curve, key["x"], key["y"])

    def _gen_priv_key(self):
        return random.randint(1, self.curve.field.n - 1)

    def _mk_pub_key(self, priv_key):
        return self.curve.g * priv_key

    def _compute_shared_secret(self, priv_key, other_pub_key):
        # Combine the two keys, and truncate to the AES key size
        point_sum = other_pub_key * priv_key
        secret = point_sum.x
        return secret

# make a main function to test the DH class
if __name__ == "__main__":
    import socket
    import threading
    import sys

    # pick random port
    port = random.randint(1024, 65535)

    def fake_client():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", port))
            dh = ModOneDiffieHellman()
            c_pubkey, c_complete_handshake = dh.handshake()
            print("client made c_pubkey: {}".format(c_pubkey))
            s_pubkey = sock.recv(2048)
            print("client got s_pubkey: {}".format(s_pubkey))
            sock.send(c_pubkey)
            c_complete_handshake(s_pubkey)
            print(f"client shared secret: {dh.key.hex()}")
        except Exception as e:
            print(e)
        finally:
            sys.exit(0)


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", port))
        s.listen()

        tc = threading.Thread(target=fake_client)
        tc.start()

        (conn, src) = s.accept()
        server_crypto = ModOneDiffieHellman()
        s_pubkey, s_complete_handshake = server_crypto.handshake()
        print("server made s_pubkey: {}".format(s_pubkey))
        conn.send(s_pubkey)
        c_pubkey = conn.recv(2048)
        print("server got c_pubkey: {}".format(c_pubkey))
        s_complete_handshake(c_pubkey)
        print(f"server shared secret: {server_crypto.key.hex()}")


