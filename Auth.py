import Storage as storage
import Crypto as crypto

class Auth:

    def __init__(self):
        self.__key: bytes | None = None

    def getKey(self) -> bytes:
        if self.__key is None:
            raise RuntimeError("Vault is locked")
        return self.__key

    def isInitialised(self) -> bool:
        return storage.getHashedPassword() is not None

    def isUnlocked(self) -> bool:
        return self.__key is not None

    def createMasterPassword(self, masterPassword: str):
        if self.isInitialised():
            raise RuntimeError("Vault already initialised")
        storage.storeHashedMasterPassword(masterPassword)
        storage.generateAndStoreSalt()
        self.__key = crypto.deriveKey(masterPassword,salt = storage.getSalt())

    def unlock(self, masterPassword: str) -> bool:
        stored = storage.getHashedPassword()
        if stored is None: 
            raise RuntimeError("Vault not initialised")
        if not crypto.verifyHash(storedHash=stored, masterPassword=masterPassword):
            return False
        self.__key = crypto.deriveKey(masterPassword, salt=storage.getSalt())
        return True

    def lock(self):
        self.__key = None
