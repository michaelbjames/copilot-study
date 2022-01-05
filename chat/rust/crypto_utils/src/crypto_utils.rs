pub use bp256::r1::BrainpoolP256r1;
use byteorder::{ReadBytesExt, WriteBytesExt, BigEndian, LittleEndian};
use num_bigint::ToBigInt;
use num_bigint::ToBigUint;
use std::io::{Write, Read};
use openssl::symm::Mode;
extern crate openssl;
extern crate rustc_serialize;
extern crate rand;
use rand::Rng;
use rand::thread_rng;
use openssl::symm::{Cipher, Crypter};
use num_bigint::BigUint;

 
pub struct Crypto {
    cipher: Cipher,
    //key: Vec<u8>
}

impl Crypto {
    
    pub fn new() -> Crypto {
        let cipher = Cipher::aes_128_ecb();
        Crypto {
            cipher,
        }
    }

    pub fn encrypt(plaintext: &[u8]) -> Vec<u8> {
        let cipher = Crypto::new().cipher;
        //let mut key = vec![];
        let key = [134, 234, 34, 234, 34, 234, 34, 234, 34, 234, 34, 234, 34, 234, 34, 234];

        //let key = Crypto::handshake();

        let mut ciphertext = vec![0; plaintext.len() + cipher.block_size()];
        let mut crypter = Crypter::new(cipher, Mode::Encrypt, &key, None).unwrap();
        crypter.pad(true);
    
        let count = crypter.update(plaintext, &mut ciphertext).unwrap();
        let rest = crypter.finalize(&mut ciphertext[count..]).unwrap();
    
        ciphertext.truncate(count + rest);
        ciphertext
    }

    pub fn decrypt(data: &[u8]) -> Vec<u8> {
        let cipher = Crypto::new().cipher;
        let key = [134, 234, 34, 234, 34, 234, 34, 234, 34, 234, 34, 234, 34, 234, 34, 234];

        let mut decrypted = Crypter::new(cipher, Mode::Decrypt, &key, None).unwrap();
        let mut output = vec![0 as u8; data.len() + cipher.block_size()];
    
        let decrypted_result = decrypted.update(&data, &mut output);
    
        match decrypted_result {
            Ok(_) => output,
            Err(e) => panic!("Error decrypting text: {}", e),
        }
    }

    pub fn handshake() -> Vec<u8> {
        let pdh = PrimeDiffieHellman::new();
        let priv_key = pdh.gen_priv_key();
        let pub_key = pdh.gen_pub_key(priv_key);
        //println!("Public Key: {}", pub_key);
        //let shared_secret = pdh.compute_shared_secret(priv_key, pub_key);
        let mut wtr = Vec::new();
        wtr.write_u16::<BigEndian>(997).unwrap();
        while wtr.len() != 16 {
            wtr.push(0);
        }

        //println!("{:?} {}", wtr, wtr.len());
        return wtr[..].to_vec();
    }  
}

pub struct PrimeDiffieHellman {
    p: usize,
    g: usize
}

impl PrimeDiffieHellman {
    pub fn new() -> PrimeDiffieHellman {  
        PrimeDiffieHellman {
            p: 997,
            g: 2,
        }  
    }

    pub fn serialize_key(&self, key: usize) {
        
    }

    pub fn deserialize_key(&self, key: usize) {
        
    }

    pub fn gen_priv_key(&self) -> usize {
        let mut rng = rand::thread_rng();
        let priv_key = rng.gen_range(1..(self.p - 1));
        return priv_key;
    }

    pub fn gen_pub_key(&self, priv_key: usize) -> usize {
        let pub_key = usize::pow(self.g, priv_key as u32) % self.p;
        return pub_key;
    }

    pub fn compute_shared_secret(&self, priv_key: usize, other_pub_key: usize) -> usize {
        let secret = other_pub_key.pow(priv_key as u32) % self.p;
        return secret;
    } 
}
pub struct ECDiffieHellman {
    curve: BrainpoolP256r1,
    priv_key: usize,
    pub_key: usize
}

pub fn main() {
    
}