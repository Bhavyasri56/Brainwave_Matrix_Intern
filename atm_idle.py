"""
ATM Interface - atm_idle.py
This version works in IDLE (PIN entered via input instead of hidden getpass).
"""
import json
import os
import time
from datetime import datetime

ACCOUNTS_FILE = "accounts.json"

# --- Data persistence utilities ---
def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return {}
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)

# --- Account helpers ---
def create_account(accounts, acct_no, name, pin, initial_balance=0.0):
    if acct_no in accounts:
        return False, "Account already exists."
    accounts[acct_no] = {
        "name": name,
        "pin": str(pin),
        "balance": float(initial_balance),
        "transactions": []
    }
    add_transaction(accounts, acct_no, "Account Created", 0.0, "Initial account setup")
    save_accounts(accounts)
    return True, "Account created."

def add_transaction(accounts, acct_no, tx_type, amount, remark=""):
    acct = accounts[acct_no]
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": tx_type,
        "amount": float(amount),
        "remark": remark,
        "balance": float(acct["balance"])
    }
    acct["transactions"].append(entry)

# --- Authentication ---
def authenticate(accounts):
    acct_no = input("Enter account number: ").strip()
    if acct_no not in accounts:
        print("Account not found.")
        return None
    pin = input("Enter PIN: ").strip()   # using input instead of getpass
    if pin != accounts[acct_no]["pin"]:
        print("Invalid PIN.")
        return None
    print(f"Welcome, {accounts[acct_no]['name']}!")
    return acct_no

# --- ATM operations ---
def check_balance(accounts, acct_no):
    print(f"Your current balance: ₹{accounts[acct_no]['balance']:.2f}")

def deposit(accounts, acct_no):
    try:
        amt = float(input("Enter amount to deposit: ").strip())
    except ValueError:
        print("Invalid amount.")
        return
    if amt <= 0:
        print("Amount must be positive.")
        return
    accounts[acct_no]["balance"] += amt
    add_transaction(accounts, acct_no, "Deposit", amt, "Cash deposit")
    save_accounts(accounts)
    print(f"Deposited ₹{amt:.2f}. New balance: ₹{accounts[acct_no]['balance']:.2f}")

def withdraw(accounts, acct_no):
    try:
        amt = float(input("Enter amount to withdraw: ").strip())
    except ValueError:
        print("Invalid amount.")
        return
    if amt <= 0:
        print("Amount must be positive.")
        return
    if amt > accounts[acct_no]["balance"]:
        print("Insufficient funds.")
        return
    accounts[acct_no]["balance"] -= amt
    add_transaction(accounts, acct_no, "Withdrawal", amt, "Cash withdrawal")
    save_accounts(accounts)
    print(f"Withdrew ₹{amt:.2f}. New balance: ₹{accounts[acct_no]['balance']:.2f}")

def transfer(accounts, acct_no):
    to_acct = input("Enter destination account number: ").strip()
    if to_acct not in accounts:
        print("Destination account does not exist.")
        return
    try:
        amt = float(input("Enter amount to transfer: ").strip())
    except ValueError:
        print("Invalid amount.")
        return
    if amt <= 0:
        print("Amount must be positive.")
        return
    if amt > accounts[acct_no]["balance"]:
        print("Insufficient funds.")
        return
    accounts[acct_no]["balance"] -= amt
    accounts[to_acct]["balance"] += amt
    add_transaction(accounts, acct_no, "Transfer Out", amt, f"To {to_acct}")
    add_transaction(accounts, to_acct, "Transfer In", amt, f"From {acct_no}")
    save_accounts(accounts)
    print(f"Transferred ₹{amt:.2f} to {to_acct}. New balance: ₹{accounts[acct_no]['balance']:.2f}")

def mini_statement(accounts, acct_no, limit=10):
    txs = accounts[acct_no]["transactions"][-limit:]
    if not txs:
        print("No transactions yet.")
        return
    print(f"Last {len(txs)} transactions:")
    for t in txs:
        print(f"{t['time']} | {t['type']:12} | ₹{t['amount']:.2f} | Bal: ₹{t['balance']:.2f} | {t['remark']}")

def change_pin(accounts, acct_no):
    old = input("Enter current PIN: ").strip()
    if old != accounts[acct_no]["pin"]:
        print("Current PIN incorrect.")
        return
    new = input("Enter new PIN: ").strip()
    confirm = input("Confirm new PIN: ").strip()
    if new != confirm:
        print("PIN mismatch.")
        return
    if not new.isdigit() or len(new) < 4:
        print("PIN must be numeric and at least 4 digits.")
        return
    accounts[acct_no]["pin"] = new
    add_transaction(accounts, acct_no, "PIN Change", 0.0, "PIN updated")
    save_accounts(accounts)
    print("PIN changed successfully.")

# --- UI / Loop ---
def atm_menu(accounts, acct_no):
    while True:
        print("\n--- ATM Menu ---")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. Mini Statement")
        print("6. Change PIN")
        print("7. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            check_balance(accounts, acct_no)
        elif choice == "2":
            deposit(accounts, acct_no)
        elif choice == "3":
            withdraw(accounts, acct_no)
        elif choice == "4":
            transfer(accounts, acct_no)
        elif choice == "5":
            mini_statement(accounts, acct_no)
        elif choice == "6":
            change_pin(accounts, acct_no)
        elif choice == "7":
            print("Logging out...")
            time.sleep(0.7)
            break
        else:
            print("Invalid choice. Try again.")

def main():
    accounts = load_accounts()
    if not accounts:
        print("No accounts found. Creating demo accounts...")
        create_account(accounts, "1001", "Alice", "1234", 5000.0)
        create_account(accounts, "1002", "Bob", "2345", 3000.0)
        print("Demo accounts created:")
        print(" - 1001 / PIN 1234 (Alice, ₹5000)")
        print(" - 1002 / PIN 2345 (Bob, ₹3000)")

    while True:
        print("\n====== Welcome to Python ATM ======")
        print("1. Login")
        print("2. Create new account")
        print("3. Exit")
        action = input("Select: ").strip()
        if action == "1":
            acct_no = authenticate(accounts)
            if acct_no:
                atm_menu(accounts, acct_no)
            accounts = load_accounts()
        elif action == "2":
            acct_no = input("Choose a new account number: ").strip()
            name = input("Enter account holder name: ").strip()
            pin = input("Set PIN (min 4 digits): ").strip()
            try:
                initial = float(input("Initial deposit (0 if none): ").strip() or "0")
            except ValueError:
                initial = 0.0
            ok, msg = create_account(accounts, acct_no, name, pin, initial)
            print(msg)
        elif action == "3":
            print("Exiting. Goodbye.")
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":

    main()
