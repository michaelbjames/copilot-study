
#!/usr/bin/env python3

from sys import byteorder
from Crypto.Cipher import AES
from Crypto.Util import Padding
import random
import json
import math
from typing import Optional

BYTE_ORDER = "big"
DH_MESSAGE_SIZE_BYTES = 32

class Crypto(object):
    def __init__(self):
        self.aes_secret = None
        self.cipher = None
        self.p = 997
        self.g = 2

    def _gen_priv_key(self) -> int:
        # TODO
        NotImplementedError()

    def _mk_pub_key(self, priv_key:int) -> int:
        # TODO
        NotImplementedError()

    def _compute_shared_secret(self, priv_key:int, other_pub_key:int) -> int:
        # TODO
        NotImplementedError()

    @staticmethod
    def _serialize_key(pub_key:int) -> bytes:
        """
        Input: a public key to be sent to the other party
        Output: a string representing the public key, in bytes
        """
        # TODO
        NotImplementedError()

    @staticmethod
    def _deserialize_key(pub_key_str:bytes) -> int:
        # TODO
        """
        Input: bytes representing a public key as a string.
        Output: a public key int
        """
        NotImplementedError()


    def encrypt(self, message:bytes) -> bytes:
        """
        Encrypt a message using the shared secret.
        Input: message:bytes
        Output: ciphertext:bytes
        """
        assert self.cipher is not None
        padded = Padding.pad(message, AES.block_size)
        return self.cipher.encrypt(padded)

    def decrypt(self, cipherbytes:bytes) -> Optional[bytes]:
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

    def handshake_part1(self) -> bytes:
        """
        Facilitate a cryptographic handshake between two parties.
        This will generate the private key and the public key.
        The private key is initialized inside the class and
        you are given the public key, in a format you can
        readily send to the other party.

        You must call handshake_part2() with information the
        other party gives you.
        """
        self.priv_key = self._gen_priv_key()
        pub_key = self._mk_pub_key(self.priv_key)
        pubkey_repr = Crypto._serialize_key(pub_key)
        return pubkey_repr

    def handshake_part2(self, other_pub_key_repr:bytes) -> None:
        other_pub_key = Crypto._deserialize_key(other_pub_key_repr)
        shared_secret = self._compute_shared_secret(self.priv_key, other_pub_key)
        self.aes_secret = shared_secret.to_bytes(DH_MESSAGE_SIZE_BYTES, byteorder=BYTE_ORDER)
        self._init_cipher(self.aes_secret)
        return

    def _init_cipher(self, key) -> None:
        self.cipher = AES.new(key, AES.MODE_ECB)


# Want to test your work?
# Run this file with python3.
if __name__ == '__main__':
    # write some tests here
    dh1 = Crypto()
    dh2 = Crypto()
    pass