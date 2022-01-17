use num::BigUint;
use openssl::symm::{Cipher, Crypter, Mode};
use rand::Rng;

type KeyBytes = [u8; 16];
pub trait Crypto {
    fn encrypt(&self, plaintext: &[u8]) -> Vec<u8>;
    fn decrypt(&self, ciphertext: &[u8]) -> Vec<u8>;
    fn handshake(&mut self, priv_key: &BigUint, other_pub_key: &BigUint);
    fn serialize(&self, pub_key: &BigUint) -> KeyBytes;
    fn deserialize(&self, pub_key: &KeyBytes) -> BigUint;
    fn init_key(&mut self, key: &KeyBytes);
    fn generate_keys(&self) -> (BigUint, KeyBytes);
    fn pad_be(&self, key: &BigUint) -> KeyBytes;
}

#[derive(Clone)]
pub struct PrimeDiffieHellman {
    p: usize,
    g: usize,
    cipher: Cipher,
    key: KeyBytes,
}

impl PrimeDiffieHellman {
    pub fn new() -> PrimeDiffieHellman {
        PrimeDiffieHellman {
            cipher: Cipher::aes_128_ecb(),
            key: [0u8; 16],
            p: 997,
            g: 2,
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
}

impl Default for PrimeDiffieHellman {
    fn default() -> Self {
        Self::new()
    }
}

impl Crypto for PrimeDiffieHellman {
    fn pad_be(&self, key: &BigUint) -> KeyBytes {
        let mut buffer = [0u8; 16];
        let key_bytes = key.to_bytes_be();
        buffer[16 - key_bytes.len()..].copy_from_slice(&key_bytes);
        buffer
    }

    fn encrypt(&self, plaintext: &[u8]) -> Vec<u8> {
        let mut encryptvec: Vec<u8> = plaintext.to_vec();
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

    fn decrypt(&self, data: &[u8]) -> Vec<u8> {
        let mut decrypted = Crypter::new(self.cipher, Mode::Decrypt, &self.key, None).unwrap();
        let mut output = vec![0_u8; data.len() + self.cipher.block_size()];
        let mut decryptvec: Vec<u8> = data.to_vec().into_iter().rev().skip_while(|&x| x == 0).collect();
        decryptvec.reverse();
        let datalen = decryptvec.pop();
        let decrypted_result = decrypted.update(&decryptvec, &mut output);

        match decrypted_result {
            Ok(_) => {
                output.truncate(datalen.unwrap() as usize);
                output
            }
            Err(e) => panic!("Error decrypting text: {}", e),
        }
    }

    fn handshake(&mut self, priv_key: &BigUint, other_pub_key: &BigUint) {
        let shared_secret = self.compute_shared_secret(priv_key, other_pub_key);
        println!("Shared secret: {}", shared_secret);
        let shared_key = self.pad_be(&shared_secret);
        self.init_key(&shared_key);
    }

    fn serialize(&self, pub_key: &BigUint) -> KeyBytes {
        self.pad_be(&pub_key)
    }

    fn deserialize(&self, pub_key: &KeyBytes) -> BigUint {
        BigUint::from_bytes_be(pub_key)
    }

    fn init_key(&mut self, key: &KeyBytes) {
        self.key = *key;
    }

    fn generate_keys(&self) -> (BigUint, KeyBytes) {
        let priv_key = self.gen_priv_key();
        let pub_key = self.gen_pub_key(&priv_key);
        let pubkey_bytes = self.serialize(&pub_key);
        (priv_key, pubkey_bytes)
    }
}
