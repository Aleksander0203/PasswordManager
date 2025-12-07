import sqlite3

def addEmailPasswordCombo(email: str, password: str, nonce: str):
    conn = sqlite.connect("/TestFiles/testVault.db")
    cursor = conn.cursor
