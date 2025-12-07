import crypto
import secrets
import random
import string

def testEncrptAndDecrypt():
    tests = []
    keys = []
    for _ in range(10):
        tests.append("".join(random.choices(string.ascii_lowercase + string.digits, k = 10)))
    for _ in range(10):
        keys.append(secrets.token_bytes(32))
    for i in tests:
        print(i)
    ciphertexts = []
    for i in range(10):
        x = crypto.encrypt(key=keys[i], plaintext=tests[i])
        print(x)
        ciphertexts.append(x)
    for i in range(10):
        x = crypto.decrypt(key=keys[i], ciphertext=ciphertexts[i])
        print(x)
        
    

testEncrptAndDecrypt()
