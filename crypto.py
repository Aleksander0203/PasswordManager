import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import argon2

def encrypt(plaintext: str, key: str):
    nonce = secrets.token_bytes(12)
    ciphertext = nonce + AESGCM(key).encrypt(nonce, plaintext.encode(), b"")
    return ciphertext

def decrypt(ciphertext: str, key: str):
    return AESGCM(key).decrypt(ciphertext[:12], ciphertext[12:], b"").decode()

def deriveKey(masterPassword: str, salt: bytes):
    ph = argon2.PasswordHasher()
    hash = argon2.low_level.hash_secret_raw(
        secret = masterPassword.encode(),
        salt = salt,
        time_cost = 3,
        memory_cost = 64 * 1024, 
        parallelism=2,
        hash_len=32,
        type=argon2.low_level.Type.ID
    )
    return hash 

def hashPassword(masterPassword: str):
    ph = argon2.PasswordHasher()
    hash = ph.hash(masterPassword)
    return hash

def verifyHash(storedHash: bytes, masterPassword: str):
    ph = argon2.PasswordHasher()
    try:
        res = ph.verify(storedHash,masterPassword)
        return True
    except: 
        return False
