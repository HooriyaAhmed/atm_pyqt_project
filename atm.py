import db
import random

attempts = {}


def register(pin):
    acc_no = str(random.randint(100000, 999999))
    db.create_user(pin, acc_no)
    return acc_no


def login(acc_no, pin):
    user = db.get_user(acc_no)

    if not user:
        return "INVALID"

    if user[4] == 1:
        return "LOCKED"

    if user[2] == pin:
        attempts[acc_no] = 0
        return user

    attempts[acc_no] = attempts.get(acc_no, 0) + 1

    if attempts[acc_no] >= 3:
        db.lock_user(acc_no)
        return "LOCKED"

    return "INVALID"


def get_balance(acc_no):
    user = db.get_user(acc_no)
    return user[3] if user else 0


def deposit(acc_no, amount):
    if amount <= 0:
        return "INVALID AMOUNT"

    user = db.get_user(acc_no)
    if not user:
        return "INVALID"

    new_bal = user[3] + amount
    db.update_balance(acc_no, new_bal)
    db.add_transaction(acc_no, "DEPOSIT", amount)

    return new_bal


def withdraw(acc_no, amount):
    user = db.get_user(acc_no)

    if not user:
        return "INVALID"

    if amount <= 0:
        return "INVALID AMOUNT"

    if amount > user[3]:
        return "INSUFFICIENT"

    new_bal = user[3] - amount
    db.update_balance(acc_no, new_bal)
    db.add_transaction(acc_no, "WITHDRAW", amount)

    return new_bal


def transfer(from_acc, to_acc, amount):
    sender = db.get_user(from_acc)
    receiver = db.get_user(to_acc)

    if not sender or not receiver:
        return "INVALID ACCOUNT"

    if amount <= 0:
        return "INVALID AMOUNT"

    if sender[3] < amount:
        return "INSUFFICIENT"

    db.update_balance(from_acc, sender[3] - amount)
    db.update_balance(to_acc, receiver[3] + amount)

    db.add_transaction(from_acc, f"SEND TO {to_acc}", amount)
    db.add_transaction(to_acc, f"RECEIVE FROM {from_acc}", amount)

    return "TRANSFER SUCCESS"


def mini_statement(acc_no):
    return db.get_last_transactions(acc_no)