import unittest
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.models import init_db, get_connection
from backend.services.account_service import AccountService


def _reset_db():
    """Drop and recreate tables for a clean test state."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS accounts")
    conn.commit()
    conn.close()
    init_db()


class TestAccountService(unittest.TestCase):

    def setUp(self):
        _reset_db()
        self.service = AccountService()

    # ------------------------------------------------------------------
    # create_account
    # ------------------------------------------------------------------

    def test_create_account_success(self):
        result = self.service.create_account("alice", 500.0)
        self.assertIn("account_id", result)
        self.assertIsInstance(result["account_id"], int)
        self.assertIn("message", result)

    def test_create_account_zero_deposit(self):
        result = self.service.create_account("bob", 0.0)
        self.assertIn("account_id", result)

    def test_create_account_negative_deposit_raises(self):
        with self.assertRaises(ValueError):
            self.service.create_account("charlie", -100.0)

    def test_create_account_empty_username_raises(self):
        with self.assertRaises(ValueError):
            self.service.create_account("   ", 100.0)

    def test_create_account_none_username_raises(self):
        with self.assertRaises(ValueError):
            self.service.create_account(None, 100.0)

    def test_create_account_none_deposit_raises(self):
        with self.assertRaises(ValueError):
            self.service.create_account("dave", None)

    # ------------------------------------------------------------------
    # get_account
    # ------------------------------------------------------------------

    def test_get_account_exists(self):
        result = self.service.create_account("eve", 250.0)
        account = self.service.get_account(result["account_id"])
        self.assertIsNotNone(account)
        self.assertEqual(account.username, "eve")
        self.assertEqual(account.balance, 250.0)
        self.assertEqual(account.initial_deposit, 250.0)

    def test_get_account_not_found_returns_none(self):
        account = self.service.get_account(999999)
        self.assertIsNone(account)

    def test_get_account_none_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_account(None)

    # ------------------------------------------------------------------
    # deposit
    # ------------------------------------------------------------------

    def test_deposit_success(self):
        acc = self.service.create_account("frank", 100.0)
        result = self.service.deposit(acc["account_id"], 50.0)
        self.assertEqual(result["new_balance"], 150.0)

    def test_deposit_zero_raises(self):
        acc = self.service.create_account("grace", 100.0)
        with self.assertRaises(ValueError):
            self.service.deposit(acc["account_id"], 0.0)

    def test_deposit_negative_raises(self):
        acc = self.service.create_account("henry", 100.0)
        with self.assertRaises(ValueError):
            self.service.deposit(acc["account_id"], -10.0)

    def test_deposit_nonexistent_account_returns_none(self):
        result = self.service.deposit(999999, 50.0)
        self.assertIsNone(result)

    def test_deposit_none_amount_raises(self):
        acc = self.service.create_account("iris", 100.0)
        with self.assertRaises(ValueError):
            self.service.deposit(acc["account_id"], None)

    def test_deposit_none_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.deposit(None, 50.0)

    # ------------------------------------------------------------------
    # withdraw
    # ------------------------------------------------------------------

    def test_withdraw_success(self):
        acc = self.service.create_account("jack", 200.0)
        result = self.service.withdraw(acc["account_id"], 75.0)
        self.assertEqual(result["new_balance"], 125.0)

    def test_withdraw_exact_balance(self):
        acc = self.service.create_account("kate", 100.0)
        result = self.service.withdraw(acc["account_id"], 100.0)
        self.assertEqual(result["new_balance"], 0.0)

    def test_withdraw_insufficient_funds_raises(self):
        acc = self.service.create_account("leo", 50.0)
        with self.assertRaises(ValueError):
            self.service.withdraw(acc["account_id"], 100.0)

    def test_withdraw_zero_raises(self):
        acc = self.service.create_account("mia", 100.0)
        with self.assertRaises(ValueError):
            self.service.withdraw(acc["account_id"], 0.0)

    def test_withdraw_negative_raises(self):
        acc = self.service.create_account("ned", 100.0)
        with self.assertRaises(ValueError):
            self.service.withdraw(acc["account_id"], -20.0)

    def test_withdraw_nonexistent_account_returns_none(self):
        result = self.service.withdraw(999999, 10.0)
        self.assertIsNone(result)

    def test_withdraw_none_amount_raises(self):
        acc = self.service.create_account("olive", 100.0)
        with self.assertRaises(ValueError):
            self.service.withdraw(acc["account_id"], None)

    def test_withdraw_none_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.withdraw(None, 50.0)

    # ------------------------------------------------------------------
    # get_transactions
    # ------------------------------------------------------------------

    def test_get_transactions_empty(self):
        acc = self.service.create_account("paul", 100.0)
        txns = self.service.get_transactions(acc["account_id"])
        self.assertEqual(txns, [])

    def test_get_transactions_after_deposit(self):
        acc = self.service.create_account("quinn", 100.0)
        self.service.deposit(acc["account_id"], 50.0)
        txns = self.service.get_transactions(acc["account_id"])
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0]["transaction_type"], "deposit")

    def test_get_transactions_none_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_transactions(None)


if __name__ == "__main__":
    unittest.main()
