from backend.models import get_connection
from backend.models.account import Account
from backend.models.transaction import Transaction


class AccountService:
    """Handles core logic for account operations."""

    def create_account(self, username, initial_deposit):
        if username is None:
            raise ValueError("Username must not be None.")
        if initial_deposit is None:
            raise ValueError("Initial deposit must not be None.")
        username = username.strip()
        if not username:
            raise ValueError("Username must not be empty.")
        if initial_deposit < 0:
            raise ValueError("Initial deposit must be non-negative.")

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO accounts (username, balance, initial_deposit) VALUES (?, ?, ?)",
                (username, initial_deposit, initial_deposit),
            )
            conn.commit()
            account_id = cursor.lastrowid
            return {"account_id": account_id, "message": "Account created successfully."}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_account(self, account_id):
        if account_id is None:
            raise ValueError("Account ID must not be None.")
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return Account.from_row(row)
        finally:
            conn.close()

    def deposit(self, account_id, amount):
        if account_id is None:
            raise ValueError("Account ID must not be None.")
        if amount is None:
            raise ValueError("Amount must not be None.")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            account = Account.from_row(row)
            if account is None:
                return None

            new_balance = account.balance + amount
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (new_balance, account_id),
            )
            cursor.execute(
                "INSERT INTO transactions (account_id, transaction_type, symbol, quantity, price, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (account_id, "deposit", None, None, None, amount),
            )
            conn.commit()
            return {"new_balance": new_balance, "message": "Deposit successful."}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def withdraw(self, account_id, amount):
        if account_id is None:
            raise ValueError("Account ID must not be None.")
        if amount is None:
            raise ValueError("Amount must not be None.")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            account = Account.from_row(row)
            if account is None:
                return None

            if account.balance < amount:
                raise ValueError("Insufficient funds for withdrawal.")

            new_balance = account.balance - amount
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (new_balance, account_id),
            )
            cursor.execute(
                "INSERT INTO transactions (account_id, transaction_type, symbol, quantity, price, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (account_id, "withdrawal", None, None, None, amount),
            )
            conn.commit()
            return {"new_balance": new_balance, "message": "Withdrawal successful."}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_transactions(self, account_id):
        if account_id is None:
            raise ValueError("Account ID must not be None.")
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM transactions WHERE account_id = ? ORDER BY created_at DESC",
                (account_id,),
            )
            rows = cursor.fetchall()
            return [Transaction.from_row(row).to_dict() for row in rows]
        finally:
            conn.close()
