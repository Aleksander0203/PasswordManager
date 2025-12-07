import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(plaintext: str, key: str):
    nonce = secrets.token_bytes(12)
    ciphertext = nonce + AESGCM(key).encrypt(nonce, plaintext.encode(), b"")
    return ciphertext

def decrypt(ciphertext: str, key: str):
    return AESGCM(key).decrypt(ciphertext[:12], ciphertext[12:], b"").decode()
