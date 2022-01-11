pub use bp256::r1::BrainpoolP256r1;
use json::JsonValue;
use num::BigInt;
extern crate rand;
use rand::Rng;
use openssl::symm::{Cipher, Crypter, Mode};
use byteorder::WriteBytesExt;
use byteorder::BigEndian;
use num::ToPrimitive;

pub trait Crypto {
    fn new() -> Self;
    fn encrypt(&self, plaintext: &[u8]) -> Vec<u8>;
    fn decrypt(&self, ciphertext: &[u8]) -> Vec<u8>;
    fn gen_priv_key(&self) -> BigInt;
    fn gen_pub_key(&self, priv_key: &mut BigInt) -> BigInt;
    fn compute_shared_secret(&self, priv_key: &mut BigInt, other_pub_key: BigInt) -> BigInt;
    fn handshake(&mut self, priv_key: &mut BigInt, other_pub_key: BigInt) -> ();
    fn serialize(&self, pub_key: &BigInt) -> Vec<u8>;
    fn deserialize(&self, pub_key: &[u8]) -> BigInt;
    fn init_key(&mut self, key: Vec<u8>) -> ();
    fn generate_keys(&self) -> (BigInt, Vec<u8>);
}

pub struct PrimeDiffieHellman {
    p: usize,
    g: usize,
    cipher: Cipher,
    key: Vec<u8>
}

impl Crypto for PrimeDiffieHellman {
    fn new() -> PrimeDiffieHellman {
        PrimeDiffieHellman {
            cipher: Cipher::aes_128_ecb(),
            key: vec![0; 16],
            p: 997,
            g: 2,
        }
    }

    fn gen_priv_key(&self) -> BigInt {
        let mut rng = rand::thread_rng();
        let priv_key = rng.gen_range(1..(self.p - 1));
        return BigInt::from(priv_key);
    }

    fn gen_pub_key(&self, priv_key: &mut BigInt) -> BigInt {
        let pub_key = BigInt::modpow(&BigInt::from(self.g), &priv_key, &BigInt::from(self.p));
        return pub_key;
    }

    fn compute_shared_secret(&self, priv_key: &mut BigInt, other_pub_key: BigInt) -> BigInt {
        let secret = BigInt::modpow(&other_pub_key, &priv_key, &BigInt::from(self.p));
        return secret;
    }

    fn encrypt(&self, plaintext: &[u8]) -> Vec<u8> {
        let mut ciphertext = vec![0; plaintext.len() + self.cipher.block_size()];
        let mut crypter = Crypter::new(self.cipher, Mode::Encrypt, &self.key, None).unwrap();
        crypter.pad(true);
    
        let count = crypter.update(plaintext, &mut ciphertext).unwrap();
        let rest = crypter.finalize(&mut ciphertext[count..]).unwrap();
    
        ciphertext.truncate(count + rest);
        ciphertext
    }

    fn decrypt(&self, data: &[u8]) -> Vec<u8> {
        let mut decrypted = Crypter::new(self.cipher, Mode::Decrypt, &self.key, None).unwrap();
        let mut output = vec![0 as u8; data.len() + self.cipher.block_size()];
    
        let decrypted_result = decrypted.update(&data, &mut output);
    
        match decrypted_result {
            Ok(_) => output,
            Err(e) => panic!("Error decrypting text: {}", e),
        }
    }

    fn generate_keys(&self) -> (BigInt, Vec<u8>) {
        let mut priv_key = self.gen_priv_key();
        let pub_key = self.gen_pub_key(&mut priv_key);
        let pubkey_bytes = self.serialize(&pub_key);
        return (priv_key, pubkey_bytes);
    }

    fn handshake(&mut self, priv_key: &mut BigInt, other_pub_key: BigInt) {
        let shared_secret = self.compute_shared_secret(priv_key, other_pub_key);
        let mut wtr = Vec::new();
            wtr.write_u16::<BigEndian>(ToPrimitive::to_u16(&shared_secret).unwrap()).unwrap();
            while wtr.len() != 16 {
                wtr.push(0);
            }
        self.init_key(wtr[..].to_vec());
        return;
    }

    fn init_key(&mut self, key: Vec<u8>) {
        self.key = key;
    }

    fn serialize(&self, pub_key: &BigInt) -> Vec<u8> {
        let mut key_data = json::JsonValue::new_object();
        key_data["key_val"] = ToPrimitive::to_u16(pub_key).unwrap().into();
        let key_json_str = key_data.dump();
        return key_json_str.as_bytes().to_vec();
    }

    fn deserialize(&self, pub_key: &[u8]) -> BigInt {
        let key_json_str = String::from_utf8(pub_key.to_vec()).unwrap();
        let key_data: JsonValue = json::parse(&key_json_str).unwrap();
        let key_value = key_data["key_val"].as_u16().unwrap();
        return BigInt::from(key_value);
    }
}

pub fn main() {}