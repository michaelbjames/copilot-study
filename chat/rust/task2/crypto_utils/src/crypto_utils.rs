use num::BigUint;
use openssl::symm::{Cipher, Crypter, Mode};
use rand::Rng;

type KeyBytes = [u8; 16];

pub trait Crypto {
    fn init_keys(&mut self) -> KeyBytes;
    fn handshake(&mut self, other_pub_key: &KeyBytes);
    fn encrypt(&self, plaintext: &[u8]) -> Vec<u8>;
    fn decrypt(&self, ciphertext: &[u8]) -> Vec<u8>;
    fn serialize(&self, pub_key: &BigUint) -> KeyBytes;
    fn deserialize(&self, pub_key: &KeyBytes) -> BigUint;
}

impl Crypto for PrimeDiffieHellman {
    /** Facilitate a cryptographic handshake between two parties.
        This will generate the private key and the public key.
        The private key is initialized inside the class and
        you are given the public key, in a format you can
        readily send to the other party.
    */
    fn init_keys(&mut self) -> KeyBytes {
        self.priv_key = self.gen_priv_key();
        let pub_key = self.gen_pub_key(&self.priv_key);
        self.serialize(&pub_key)
    }

    // You must call handshake() with the public key the other party gives you.
    fn handshake(&mut self, other_pub_key: &KeyBytes) {
        let deserialized_key = self.deserialize(other_pub_key);
        let shared_secret = self.compute_shared_secret(&self.priv_key, &deserialized_key);
        let shared_key = self.pad_be(&shared_secret);
        self.key = shared_key;
    }

    // Encrypts plaintext using the shared secret
    fn encrypt(&self, plaintext: &[u8]) -> Vec<u8> {
        let mut encryptvec: Vec<u8> = plaintext.to_vec();
        encryptvec.push(encryptvec.len() as u8); // add data length
        let mut ciphertext = vec![0; plaintext.len() + self.cipher.block_size()];
        let mut crypter = Crypter::new(self.cipher, Mode::Encrypt, &self.key, None).unwrap();
        crypter.pad(true);
        let datalen = encryptvec.pop();
        let count = crypter.update(&encryptvec, &mut ciphertext).unwrap();
        let rest = crypter.finalize(&mut ciphertext[count..]).unwrap();

        ciphertext.truncate(count + rest);
        ciphertext.push(datalen.unwrap());
        ciphertext
    }

    // Decrypt a message using the shared secret
    fn decrypt(&self, data: &[u8]) -> Vec<u8> {
        let mut decrypted = Crypter::new(self.cipher, Mode::Decrypt, &self.key, None).unwrap();
        let mut output = vec![0_u8; data.len() + self.cipher.block_size()];
        let datalen = data.to_vec().pop();
        decrypted.update(data, &mut output).unwrap();
        output.truncate(datalen.unwrap() as usize);
        output
    }

    // Input: a public key to be sent to the other party
    // Output: a string representing the public key, in bytes
    fn serialize(&self, pub_key: &BigUint) -> KeyBytes {
        self.pad_be(pub_key)
    }

    // Input: bytes representing a public key as a string.
    // Output: a public key int
    fn deserialize(&self, pub_key: &KeyBytes) -> BigUint {
        BigUint::from_bytes_be(pub_key)
    }
}

#[derive(Clone)]
pub struct PrimeDiffieHellman {
    p: usize,
    g: usize,
    cipher: Cipher,
    key: KeyBytes,
    priv_key: BigUint,
}

impl PrimeDiffieHellman {
    pub fn new() -> PrimeDiffieHellman {
        PrimeDiffieHellman {
            cipher: Cipher::aes_128_ecb(),
            key: [0_u8; 16],
            p: 997,
            g: 2,
            priv_key: BigUint::from(0u8),
        }
    }

    fn gen_priv_key(&self) -> BigUint {
        let mut rng = rand::thread_rng();
        let priv_key = rng.gen_range(1..(self.p - 1));
        BigUint::from(priv_key)
    }

    fn gen_pub_key(&self, priv_key: &BigUint) -> BigUint {
        BigUint::from(self.g).modpow(priv_key, &self.p.into())
    }

    fn compute_shared_secret(&self, priv_key: &BigUint, other_pub_key: &BigUint) -> BigUint {
        other_pub_key.modpow(priv_key, &BigUint::from(self.p))
    }

    fn pad_be(&self, key: &BigUint) -> KeyBytes {
        let mut buffer = [0u8; 16];
        let key_bytes = key.to_bytes_be();
        buffer[16 - key_bytes.len()..].copy_from_slice(&key_bytes);
        buffer
    }
}

impl Default for PrimeDiffieHellman {
    fn default() -> Self {
        Self::new()
    }
}
