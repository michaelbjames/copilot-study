
#!/usr/bin/env python3

from sys import byteorder
from Crypto.Cipher import AES
from Crypto.Util import Padding
import random
import json
import math

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
        def complete_handshake(other_pub_key):
            shared_secret = self._compute_shared_secret(priv_key, other_pub_key)
            self.key = shared_secret.to_bytes(DH_MESSAGE_SIZE_BYTES, byteorder=BYTE_ORDER)
            self._init_cipher(self.key)
            return
        pubkey_bytes = type(self).serialize_key(pub_key)
        return (pubkey_bytes, complete_handshake)

    def _init_cipher(self, key):
        self.cipher = AES.new(key, AES.MODE_ECB)

    @classmethod
    def _serialize_key_obj(cls, key):
        NotImplementedError()

    @classmethod
    def _deserialize_key_obj(cls, key_bytes):
        NotImplementedError()

    def _gen_priv_key(self):
        NotImplementedError()

    def _mk_pub_key(self, priv_key):
        NotImplementedError()

    def _compute_shared_secret(self, priv_key, other_pub_key):
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
        return (other_pub_key ** priv_key) % self.p