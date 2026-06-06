import db

db.connect()

acc_no = input("Enter Account No: ")
pin = input("Enter PIN: ")
balance = int(input("Enter Starting Balance: "))

conn = db.sqlite3.connect("atm.db")
cur = conn.cursor()

cur.execute(
    "INSERT INTO users (acc_no, pin, balance, locked) VALUES (?, ?, ?, 0)",
    (acc_no, pin, balance)
)

conn.commit()
conn.close()

print("User Created Successfully")