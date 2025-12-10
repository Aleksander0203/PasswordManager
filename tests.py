import crypto
import storage
import secrets
import random
import string

def main():
    testEncryptAndDecrypt()
    testOpenDB()

def testEncryptAndDecrypt():
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

def testOpenDB(): 
    storage.openDB()        
    storage.deleteDB()
    storage.createDB()
    storage.createDB()
    storage.addUserPasswordCombo(serviceName="Tesco", userName="user1", password=secrets.token_bytes(12), nonce=secrets.token_bytes(12))
    storage.addUserPasswordCombo(serviceName="Aldi", userName="user2", password=secrets.token_bytes(12), nonce=secrets.token_bytes(12))
    storage.addUserPasswordCombo(serviceName="Asda", userName="user3", password=secrets.token_bytes(12), nonce=secrets.token_bytes(12))
    storage.addUserPasswordCombo(serviceName="GitHub", userName="user4", password=secrets.token_bytes(12), nonce=secrets.token_bytes(12))
    storage.addUserPasswordCombo(serviceName="Dom", userName="user5", password=secrets.token_bytes(12), nonce=secrets.token_bytes(12))
    storage.addUserPasswordCombo(serviceName="De", userName="user6", password=secrets.token_bytes(12), nonce=secrets.token_bytes(12))
    storage.addUserPasswordCombo(serviceName="Hay", userName="user7", password=secrets.token_bytes(12), nonce=secrets.token_bytes(12))
    storage.deleteEntryByID(3)
    storage.deleteEntryByUsername("user2")
    storage.deleteEntryByService("Dom")    
    storage.printAllPasswords()
    print(storage.getAllPasswords())
    

if __name__ == "__main__":
    main()
