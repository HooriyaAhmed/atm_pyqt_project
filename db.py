import sqlite3
from datetime import datetime

def connect():
    conn = sqlite3.connect("atm.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acc_no TEXT UNIQUE,
        pin TEXT,
        balance INTEGER DEFAULT 0,
        locked INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acc_no TEXT,
        type TEXT,
        amount INTEGER,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_user(pin, acc_no):
    conn = sqlite3.connect("atm.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (acc_no, pin, balance, locked) VALUES (?, ?, 0, 0)",
        (acc_no, pin)
    )

    conn.commit()
    conn.close()


def get_user(acc_no):
    conn = sqlite3.connect("atm.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE acc_no=?", (acc_no,))
    user = cur.fetchone()

    conn.close()
    return user


def update_balance(acc_no, balance):
    conn = sqlite3.connect("atm.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET balance=? WHERE acc_no=?",
        (balance, acc_no)
    )

    conn.commit()
    conn.close()


def lock_user(acc_no):
    conn = sqlite3.connect("atm.db")
    cur = conn.cursor()

    cur.execute("UPDATE users SET locked=1 WHERE acc_no=?", (acc_no,))

    conn.commit()
    conn.close()


def add_transaction(acc_no, t_type, amount):
    conn = sqlite3.connect("atm.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions (acc_no, type, amount, time)
        VALUES (?, ?, ?, ?)
    """, (
        acc_no,
        t_type,
        amount,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_last_transactions(acc_no, limit=5):
    conn = sqlite3.connect("atm.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT type, amount, time
        FROM transactions
        WHERE acc_no=?
        ORDER BY id DESC
        LIMIT ?
    """, (acc_no, limit))

    data = cur.fetchall()
    conn.close()
    return data