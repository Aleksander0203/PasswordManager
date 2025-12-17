import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import argon2
from argon2.exceptions import VerifyMismatchError

def encrypt(plaintext: str, key: bytes) -> bytes: 
    nonce = secrets.token_bytes(12)
    ciphertext = nonce + AESGCM(key).encrypt(nonce, plaintext.encode(), b"")
    return ciphertext

def decrypt(ciphertext: bytes, key: bytes) -> str:
    return AESGCM(key).decrypt(ciphertext[:12], ciphertext[12:], b"").decode()

def deriveKey(masterPassword: str, salt: bytes):
    hsh = argon2.low_level.hash_secret_raw(
        secret = masterPassword.encode(),
        salt = salt,
        time_cost = 3,
        memory_cost = 64 * 1024, 
        parallelism=2,
        hash_len=32,
        type=argon2.low_level.Type.ID
    )
    return hsh 

def hashPassword(masterPassword: str):
    ph = argon2.PasswordHasher()
    hsh = ph.hash(masterPassword)
    return hsh

def verifyHash(storedHash: str, masterPassword: str):
    ph = argon2.PasswordHasher()
    try:
        res = ph.verify(storedHash,masterPassword)
        return True
    except VerifyMismatchError: 
        return False
