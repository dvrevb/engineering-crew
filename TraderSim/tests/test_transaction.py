import unittest
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.models import init_db, get_connection
from backend.services.account_service import AccountService
from backend.services.portfolio_service import PortfolioService


def _reset_db():
    """Drop and recreate tables for a clean test state."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS accounts")
    conn.commit()
    conn.close()
    init_db()


class TestPortfolioService(unittest.TestCase):

    def setUp(self):
        _reset_db()
        self.account_service = AccountService()
        self.portfolio_service = PortfolioService()
        result = self.account_service.create_account("trader1", 10000.0)
        self.account_id = result["account_id"]

    # ------------------------------------------------------------------
    # record_buy
    # ------------------------------------------------------------------

    def test_buy_success(self):
        result = self.portfolio_service.record_buy(self.account_id, "AAPL", 2)
        self.assertIn("transaction_id", result)
        self.assertIsInstance(result["transaction_id"], int)
        self.assertIn("message", result)

    def test_buy_reduces_balance(self):
        price = 190.00  # AAPL mock price
        self.portfolio_service.record_buy(self.account_id, "AAPL", 5)
        account = self.account_service.get_account(self.account_id)
        expected_balance = 10000.0 - (price * 5)
        self.assertAlmostEqual(account.balance, expected_balance, places=2)

    def test_buy_insufficient_funds_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_buy(self.account_id, "AAPL", 1000)

    def test_buy_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_buy(self.account_id, "AAPL", 0)

    def test_buy_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_buy(self.account_id, "AAPL", -3)

    def test_buy_none_account_id_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_buy(None, "AAPL", 1)

    def test_buy_none_symbol_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_buy(self.account_id, None, 1)

    def test_buy_none_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_buy(self.account_id, "AAPL", None)

    def test_buy_nonexistent_account_returns_none(self):
        result = self.portfolio_service.record_buy(999999, "AAPL", 1)
        self.assertIsNone(result)

    def test_buy_symbol_case_insensitive(self):
        result = self.portfolio_service.record_buy(self.account_id, "aapl", 1)
        self.assertIn("AAPL", result["message"])

    # ------------------------------------------------------------------
    # record_sell
    # ------------------------------------------------------------------

    def test_sell_success(self):
        self.portfolio_service.record_buy(self.account_id, "AAPL", 5)
        result = self.portfolio_service.record_sell(self.account_id, "AAPL", 3)
        self.assertIn("transaction_id", result)
        self.assertIn("message", result)

    def test_sell_increases_balance(self):
        price = 190.00  # AAPL mock price
        self.portfolio_service.record_buy(self.account_id, "AAPL", 5)
        balance_after_buy = self.account_service.get_account(self.account_id).balance
        self.portfolio_service.record_sell(self.account_id, "AAPL", 2)
        balance_after_sell = self.account_service.get_account(self.account_id).balance
        self.assertAlmostEqual(balance_after_sell, balance_after_buy + (price * 2), places=2)

    def test_sell_more_than_owned_raises(self):
        self.portfolio_service.record_buy(self.account_id, "AAPL", 2)
        with self.assertRaises(ValueError):
            self.portfolio_service.record_sell(self.account_id, "AAPL", 5)

    def test_sell_without_any_holdings_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_sell(self.account_id, "AAPL", 1)

    def test_sell_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_sell(self.account_id, "AAPL", 0)

    def test_sell_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_sell(self.account_id, "AAPL", -1)

    def test_sell_none_account_id_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_sell(None, "AAPL", 1)

    def test_sell_none_symbol_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_sell(self.account_id, None, 1)

    def test_sell_none_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.record_sell(self.account_id, "AAPL", None)

    def test_sell_nonexistent_account_returns_none(self):
        result = self.portfolio_service.record_sell(999999, "AAPL", 1)
        self.assertIsNone(result)

    def test_sell_exact_holdings(self):
        self.portfolio_service.record_buy(self.account_id, "AAPL", 3)
        result = self.portfolio_service.record_sell(self.account_id, "AAPL", 3)
        self.assertIn("transaction_id", result)

    # ------------------------------------------------------------------
    # get_portfolio
    # ------------------------------------------------------------------

    def test_get_portfolio_empty(self):
        result = self.portfolio_service.get_portfolio(self.account_id)
        self.assertIsNotNone(result)
        self.assertIn("total_value", result)
        self.assertIn("holdings", result)
        self.assertIn("profit_loss", result)
        self.assertEqual(result["holdings"], [])

    def test_get_portfolio_with_holdings(self):
        self.portfolio_service.record_buy(self.account_id, "AAPL", 2)
        result = self.portfolio_service.get_portfolio(self.account_id)
        self.assertEqual(len(result["holdings"]), 1)
        self.assertEqual(result["holdings"][0]["symbol"], "AAPL")
        self.assertEqual(result["holdings"][0]["quantity"], 2)

    def test_get_portfolio_after_sell_all(self):
        self.portfolio_service.record_buy(self.account_id, "AAPL", 2)
        self.portfolio_service.record_sell(self.account_id, "AAPL", 2)
        result = self.portfolio_service.get_portfolio(self.account_id)
        self.assertEqual(result["holdings"], [])

    def test_get_portfolio_nonexistent_account_returns_none(self):
        result = self.portfolio_service.get_portfolio(999999)
        self.assertIsNone(result)

    def test_get_portfolio_none_id_raises(self):
        with self.assertRaises(ValueError):
            self.portfolio_service.get_portfolio(None)

    def test_get_portfolio_total_value_includes_cash(self):
        result = self.portfolio_service.get_portfolio(self.account_id)
        account = self.account_service.get_account(self.account_id)
        self.assertAlmostEqual(result["total_value"], account.balance, places=2)

    def test_get_portfolio_multiple_symbols(self):
        self.portfolio_service.record_buy(self.account_id, "AAPL", 1)
        self.portfolio_service.record_buy(self.account_id, "GOOG", 1)
        result = self.portfolio_service.get_portfolio(self.account_id)
        symbols = [h["symbol"] for h in result["holdings"]]
        self.assertIn("AAPL", symbols)
        self.assertIn("GOOG", symbols)


if __name__ == "__main__":
    unittest.main()
