#!/usr/bin/env python3

from sys import byteorder
from Crypto.Cipher import AES
from tinyec import registry
from tinyec import ec
import random
import json
import math

BYTE_ORDER = "big"
DH_MESSAGE_SIZE_BYTES = 32

class Crypto(object):
    def __init__(self):
        self.key = None
        self.cipher = None

    @classmethod
    def _type_name(cls):
        return cls.__name__

    @classmethod
    def _serialize_key_obj(cls, key):
        NotImplementedError()

    @classmethod
    def _deserialize_key_obj(cls, key_bytes):
        NotImplementedError()

    @classmethod
    def serialize_key(cls, key):
        """
        Serialize a key into a wire-safe format.
        Create a JSON object with the following format:
        {
            "type": <str>
            "key": <key object>
        }
        """
        key_type = cls._type_name()
        key = {
            "type": key_type,
            "key": cls._serialize_key_obj(key)
        }
        # Return key as a bytes object
        return json.dumps(key).encode()

    @classmethod
    def deserialize_key(cls, key_repr):
        """
        Deserialize a key from a wire-safe format.
        """
        key_obj = json.loads(key_repr)
        key_type = key_obj["type"]
        key_bytes = key_obj["key"]
        if key_type != cls._type_name():
            raise ValueError("Invalid key type")
        return cls._deserialize_key_obj(key_bytes)

    def handshake(self):
        priv_key = self._gen_priv_key() # some random int
        pub_key = self._mk_pub_key(priv_key)
        def complete_handshake(other_pub_key):
            shared_secret = self._combine_secret(priv_key, other_pub_key)
            self.key = shared_secret.to_bytes(DH_MESSAGE_SIZE_BYTES, byteorder=BYTE_ORDER)
            self._init_cipher(self.key)
            return
        pubkey_bytes = type(self).serialize_key(pub_key)
        return (pubkey_bytes, complete_handshake)

    def _gen_priv_key(self):
        NotImplementedError()

    def _mk_pub_key(self, priv_key):
        NotImplementedError()

    def _combine_secret(self, priv_key, other_pub_key):
        NotImplementedError()

    def _init_cipher(self, key):
        self.cipher = AES.new(key, AES.MODE_ECB)

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

    def _combine_secret(self, priv_key, other_pub_key):
        return (other_pub_key ** priv_key) % self.p

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

    def _combine_secret(self, priv_key, other_pub_key):
        # Combine the two keys, and truncate to the AES key size
        point_sum = other_pub_key * priv_key
        secret = point_sum.x
        return secret

