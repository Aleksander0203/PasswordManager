import sqlite3
import os
import secrets
import time

class PasswordEntry: 
    def __init__(self,ID, serviceName, userName, password, updatedAt):
        self.ID = ID
        self.serviceName = serviceName
        self.username = userName
        self.password = password
        self.updatedAt = updatedAt
    
    def getID(self):
        return self.ID
    
    def getServiceName(self):
        return self.serviceName
    
    def getUsername(self):
        return self.username
    
    def getPassword(self):
        return self.password

    def getUpdatedAt(self):
        return self.updatedAt

    def __str__(self):
        finalStr = f"""
        ID: {self.getID()}\n
        Service Name: {self.getServiceName()}\n
        Username: {self.getUsername()}\n
        Password: {self.getPassword()}\n
        """
        return finalStr


def openDB():
    try:
        conn = sqlite3.connect("TestFiles/testVault.db")
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error in openDB method: {e}")
    return (cursor,conn)

def closeDB(conn):
    conn.close()

def createDB():
    cur, conn = openDB()
    res = cur.execute("""
    CREATE TABLE IF NOT EXISTS PASSWORDS(
        ID INTEGER PRIMARY KEY,
        SERVICENAME TEXT NOT NULL,
        USERNAME TEXT NOT NULL,
        PASSWORD BLOB NOT NULL,
        UPDATED_AT INTEGER NOT NULL
    );
    """)
    res = cur.execute("""
    CREATE TABLE IF NOT EXISTS METADATA(
        KEYNAME TEXT PRIMARY KEY,
        BLOBVAL BLOB,
        STRVAL TEXT
    );
    """)
    conn.commit()
    closeDB(conn)

def generateAndStoreSalt():
    cur, conn = openDB()
    salt = secrets.token_bytes(12)
    cur.execute("INSERT OR REPLACE INTO METADATA(KEYNAME, BLOBVAL) VALUES (?, ?);", ("salt", salt))
    conn.commit()
    closeDB(conn)

def storeHashedMasterPassword(hashMasterPassword: str):
    cur, conn = openDB()
    res = cur.execute("SELECT COUNT(*) FROM METADATA WHERE STRVAL NOT NULL;")
    cur.execute("INSERT OR REPLACE INTO METADATA(KEYNAME, STRVAL) VALUES (?, ?);", ("hashedPassword", hashMasterPassword))
    conn.commit()
    closeDB(conn)

def getSalt():
    cur, conn = openDB()
    res = cur.execute("SELECT BLOBVAL FROM METADATA WHERE KEYNAME = (?)", ("salt",))
    row = res.fetchone()
    closeDB(conn)
    return row[0] if row else None

def getHashedPassword():
    cur, conn = openDB()
    res = cur.execute("SELECT STRVAL FROM METADATA WHERE KEYNAME = (?);", ("hashedPassword", ))
    row = res.fetchone()
    closeDB(conn)
    return row[0] if row else None 

def deleteDB():
    path = "TestFiles/testVault.db"
    if os.path.exists(path):
        os.remove(path)

def addUserPasswordCombo(serviceName:str, userName: str, password: bytes):
    cur, conn = openDB()
    cur.execute(f"INSERT INTO PASSWORDS(SERVICENAME, USERNAME, PASSWORD, UPDATED_AT) VALUES (?,?,?,?);", (serviceName, userName, password, int(time.time()), ))
    conn.commit()
    closeDB(conn)

def deleteEntryByID(ID: int):
    cur, conn = openDB()
    cur.execute(f"DELETE FROM PASSWORDS WHERE ID = ?;", (ID, ))
    conn.commit()
    closeDB(conn)

def deleteEntryByUsername(userName: str):
    cur, conn = openDB()
    cur.execute(f"DELETE FROM PASSWORDS WHERE USERNAME = ?;", (userName, ))
    conn.commit()
    closeDB(conn)

def deleteEntryByService(serviceName: str):
    cur, conn = openDB()
    cur.execute(f"DELETE FROM PASSWORDS WHERE SERVICENAME = ?;", (serviceName, ))
    conn.commit()
    closeDB(conn)

def deleteAllPasswords():
    cur, conn = openDB()
    cur.execute(f"DELETE FROM PASSWORDS;")
    conn.commit()
    closeDB(conn)

def editPasswordByID(serviceName: str, username: str, password: bytes, id: int):
    cur, conn = openDB()
    cur.execute("UPDATE PASSWORDS SET SERVICENAME = ?, USERNAME = ?, PASSWORD = ?, UPDATED_AT = ? WHERE ID = ?;", (serviceName, username, password, int(time.time()),id,  ))
    conn.commit()
    closeDB(conn)

def getAllPasswords():
    cur, conn = openDB()
    res = []
    query = cur.execute(f"SELECT * FROM PASSWORDS ORDER BY UPDATED_AT DESC;")
    rows = cur.fetchall()
    for row in rows:
        ID, serviceName, username, password, updatedAt = row
        passwordEntry = PasswordEntry(ID, serviceName, username, password, updatedAt)
        res.append(passwordEntry)
    closeDB(conn)
    return res

def getEntryByID(ID: int):
    cur, conn = openDB()
    query = cur.execute(f"SELECT * FROM PASSWORDS WHERE ID = ?;", (ID, )) 
    row = cur.fetchone()
    ID, serviceName, username, password, updatedAt = row
    passwordEntry = PasswordEntry(ID, serviceName, username, password, updatedAt)
    closeDB(conn)
    return passwordEntry
