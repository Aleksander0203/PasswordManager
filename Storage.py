import sqlite3
import os
import secrets

class PasswordEntry: 
    def __init__(self,ID, serviceName, userName, password):
        self.ID = ID
        self.serviceName = serviceName
        self.username = userName
        self.password = password
    
    def getID(self):
        return self.ID
    
    def getServiceName(self):
        return self.serviceName
    
    def getUsername(self):
        return self.username
    
    def getPassword(self):
        return self.password

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

def createDB():
    cur, conn = openDB()
    try:
        res = cur.execute("""
        SELECT * FROM PASSWORDS;
        """)
        res = cur.execute("""
        SELECT * FROM METADATA;
        """)
        print("Database already created.")
    except:
        res = cur.execute("""
        CREATE TABLE PASSWORDS(
            ID INTEGER PRIMARY KEY,
            SERVICENAME TEXT NOT NULL,
            USERNAME TEXT NOT NULL,
            PASSWORD BLOB NOT NULL
        );
        """)
        res = cur.execute("""
        CREATE TABLE IF NOT EXISTS METADATA(
            KEY TEXT PRIMARY KEY,
            BLOBVAL BLOB,
            STRVAL TEXT
        );
        """)
        conn.commit()
        print("Database created successfully.")

def generateAndStoreSalt():
    cur, conn = openDB()
    salt = secrets.token_bytes(12)
    cur.execute("INSERT INTO METADATA(KEY, BLOBVAL) VALUES (?, ?);", ("salt", salt))
    conn.commit()

def storeHashedMasterPassword(hashMasterPassword: str):
    cur, conn = openDB()
    res = cur.execute("SELECT COUNT(*) FROM METADATA WHERE STRVAL NOT NULL;")
    cur.execute("INSERT INTO METADATA(KEY, STRVAL) VALUES (?, ?);", ("hashedPassword", hashMasterPassword))
    conn.commit()

def getSalt():
    cur, conn = openDB()
    res = cur.execute("SELECT BLOBVAL FROM METADATA WHERE KEY = (?)", ("salt",))
    try:
        return res.fetchone()[0]
    except:
        return None

def getHashedPassword():
    cur, conn = openDB()
    res = cur.execute("SELECT STRVAL FROM METADATA WHERE KEY = (?);", ("hashedPassword", ))
    try:
        return res.fetchone()[0]
    except:
        return None

def deleteDB():
    path = "TestFiles/testVault.db"
    if os.path.exists(path):
        os.remove(path)
        print("Database removed.")
    else:
        print("Database file not found.")

def addUserPasswordCombo(serviceName:str, userName: str, password: bytes):
    cur, conn = openDB()
    try:
        cur.execute(f"""
        INSERT INTO PASSWORDS(SERVICENAME, USERNAME, PASSWORD)
        VALUES (?, ?,?);
        """, (serviceName, userName, password))
        conn.commit()
        print("Successfully added password")
    except Exception as e:
        print("Error inserting a password")
        print(e)

def deleteEntryByID(ID: int):
    cur, conn = openDB()
    try:
        cur.execute(f"DELETE FROM PASSWORDS WHERE ID = ?;", (ID, ))
        conn.commit()
        print("Entry removed successfully")
    except Exception as e:
        print(f"Error deleting the password entry.")
        print(e)

def deleteEntryByUsername(userName: str):
    cur, conn = openDB()
    try:
        cur.execute(f"DELETE FROM PASSWORDS WHERE USERNAME = ?;", (userName, ))
        conn.commit()
        print("Entry removed by username successfully")
    except Exception as e:
        print(f"Error deleting the password entry.")
        print(e)

def deleteEntryByService(serviceName: str):
    cur, conn = openDB()
    try:
        cur.execute(f"DELETE FROM PASSWORDS WHERE SERVICENAME = ?;", (serviceName, ))
        conn.commit()
        print("Entry removed by service successfully")
    except Exception as e:
        print(f"Error deleting the password entry.")
        print(e)

def deleteAllPasswords():
    cur, conn = openDB()
    try:
        cur.execute(f"DELETE FROM PASSWORDS;")
        conn.commit()
        print("All entries removed successfully.")
    except Exception as e:
        print(f"Error deleting password entry")
        print(e)

def printAllPasswords():
    cur, conn = openDB()
    try:
        query = cur.execute(f"SELECT * FROM PASSWORDS;")
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print("Error printing all entries.")
        print(e)

def getAllPasswords():
    cur, conn = openDB()
    res = []
    try:
        query = cur.execute(f"SELECT * FROM PASSWORDS;")
        rows = cur.fetchall()
        for row in rows:
            ID, serviceName, username, password = row
            passwordEntry = PasswordEntry(ID, serviceName, username, password)
            res.append(passwordEntry)
        return res
    except Exception as e:
        print("Error getting all entries")
        print(e)
        return []
            

