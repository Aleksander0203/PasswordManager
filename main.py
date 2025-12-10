import cryptography
from argon2 import PasswordHasher

class Client:

    def __init__(self, masterPassword):
        self.__masterPassword = masterPassword
        self.SALT_LEN = 16
        self.KEY_LEN = 32
    
    def getSalt(self):
        salt = ""
        with open("vault/salt.bin") as file:
            salt = file.read
            file.close()
        if salt == "":
            with open("vault/salt.bin")
        
    
    def getMasterPassword(self):
        return self.__masterPassword

    def deriveKey(self):
        ph = PasswordHasher()
        hash = ph.hash(self.__masterPassword, salt)



def login():
def main():
    print("hello world")

if __name__ == "__main__":
    main()
