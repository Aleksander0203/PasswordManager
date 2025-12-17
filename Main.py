import cryptography
import Storage as storage
import Crypto as crypto
from argon2 import PasswordHasher

class Client:

    def __init__(self):
        self.__masterKey = b""
        self.__masterPassword = ""
        self.handleLogin()
        self.setKey()

    def handleLogin(self):
        isSet = self._checkIfPasswordIsSet()
        if (isSet):
            self._login()
        else:
            self._createNewPassword()
    
    def _checkIfPasswordIsSet(self):
        hashedPassword = storage.getHashedPassword()
        if x is None:
            return False 
        return True
    
    def _login(self):
        hashedPassword = storage.getHashedPassword()
        passwordInput = input("Enter your password:\n")
        verified = crypto.verifyHash(storedHash = hashedPassword, masterPassword = passwordInput)
        while (!verified): 
            passwordInput = input("Enter your password:\n")
            verified = crypto.verifyHash(storedHash = hashedPassword, masterPassword = passwordInput)
        self.__masterPassword = passwordInput

    def _createNewPassword(self):
        firstInput = input("In order to use this password manager you must make a master password.\nPlease enter a password:\n")
        secondInput = input("Enter it again:\n")
        while firstInput != secondInput:
            firstInput = input("Passwords did not match. Please try again.\nPlease enter a password:\n")
            secondInput = input("Enter it again:\n")
        storage.storeHashedMasterPassword(firstInput)
        self.__masterPassword = firstInput

    def getMasterPassword(self):
        return self.__masterPassword

    def setKey(self):
        salt = storage.getSalt()
        if salt is None:
            storage.generateAndStoreSalt()
        salt = storage.getSalt()
        self.__masterKey = crypto.deriveKey(masterPassword = self.getPassword(), salt = salt)

    def getKey(self):
        return self.__masterKey



def main():
    inst = Client()
    return inst

if __name__ == "__main__":
    main()
