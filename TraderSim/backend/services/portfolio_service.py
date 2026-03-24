import urllib.request
import json
from backend.models import get_connection
from backend.models.account import Account
from backend.models.transaction import Transaction


# ---------------------------------------------------------------------------
# Minimal stock-price stub – in production this would call a real market API.
# Returns a float price for the given symbol. Falls back to 0.0 if unknown.
# ---------------------------------------------------------------------------
MOCK_PRICES = {
    "AAPL": 190.00,
    "GOOG": 140.00,
    "MSFT": 380.00,
    "AMZN": 185.00,
    "TSLA": 175.00,
}


def get_current_price(symbol):
    """Return the current price for a symbol (mock implementation)."""
    if symbol is None:
        return 0.0
    return MOCK_PRICES.get(symbol.upper(), 100.0)  # default $100 for unknown symbols


class PortfolioService:
    """Manages portfolio calculations: value, profit/loss, and holdings."""

    def get_portfolio(self, account_id):
        if account_id is None:
            raise ValueError("Account ID must not be None.")

        conn = get_connection()
        try:
            cursor = conn.cursor()

            # Verify account exists
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            account = Account.from_row(row)
            if account is None:
                return None

            # Retrieve all buy/sell transactions for this account
            cursor.execute(
                "SELECT * FROM transactions WHERE account_id = ? AND transaction_type IN ('buy', 'sell') ORDER BY created_at ASC",
                (account_id,),
            )
            rows = cursor.fetchall()
            transactions = [Transaction.from_row(r) for r in rows]

        finally:
            conn.close()

        # Build holdings map: symbol -> net quantity and total cost basis
        holdings_map = {}
        for txn in transactions:
            symbol = txn.symbol
            if symbol is None:
                continue
            symbol = symbol.upper()
            if symbol not in holdings_map:
                holdings_map[symbol] = {"quantity": 0, "total_cost": 0.0}

            if txn.transaction_type == "buy":
                holdings_map[symbol]["quantity"] += txn.quantity
                holdings_map[symbol]["total_cost"] += txn.amount if txn.amount else 0.0
            elif txn.transaction_type == "sell":
                qty_sold = txn.quantity
                if holdings_map[symbol]["quantity"] > 0:
                    avg_cost = holdings_map[symbol]["total_cost"] / holdings_map[symbol]["quantity"]
                    holdings_map[symbol]["total_cost"] -= avg_cost * qty_sold
                holdings_map[symbol]["quantity"] -= qty_sold

        # Build holdings list and compute total portfolio value
        holdings = []
        total_market_value = 0.0
        total_cost_basis = 0.0

        for symbol, data in holdings_map.items():
            qty = data["quantity"]
            if qty <= 0:
                continue
            current_price = get_current_price(symbol)
            market_value = current_price * qty
            cost_basis = data["total_cost"]
            unrealized_pnl = market_value - cost_basis

            total_market_value += market_value
            total_cost_basis += cost_basis

            holdings.append({
                "symbol": symbol,
                "quantity": qty,
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "cost_basis": round(cost_basis, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
            })

        # Total value includes cash balance + market value of holdings
        total_value = account.balance + total_market_value
        profit_loss = round(total_market_value - total_cost_basis, 2)

        return {
            "total_value": round(total_value, 2),
            "holdings": holdings,
            "profit_loss": profit_loss,
        }

    def record_buy(self, account_id, symbol, quantity):
        """Record a share purchase, deducting cost from account balance."""
        if account_id is None:
            raise ValueError("Account ID must not be None.")
        if symbol is None:
            raise ValueError("Symbol must not be None.")
        if quantity is None:
            raise ValueError("Quantity must not be None.")
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        symbol = symbol.upper()
        price = get_current_price(symbol)
        total_cost = price * quantity

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            account = Account.from_row(row)
            if account is None:
                return None

            if account.balance < total_cost:
                raise ValueError(
                    f"Insufficient funds. Required: ${total_cost:.2f}, Available: ${account.balance:.2f}"
                )

            new_balance = account.balance - total_cost
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (new_balance, account_id),
            )
            cursor.execute(
                "INSERT INTO transactions (account_id, transaction_type, symbol, quantity, price, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (account_id, "buy", symbol, quantity, price, total_cost),
            )
            conn.commit()
            transaction_id = cursor.lastrowid
            return {
                "transaction_id": transaction_id,
                "message": f"Bought {quantity} share(s) of {symbol} at ${price:.2f} each. Total cost: ${total_cost:.2f}.",
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def record_sell(self, account_id, symbol, quantity):
        """Record a share sale, crediting proceeds to account balance."""
        if account_id is None:
            raise ValueError("Account ID must not be None.")
        if symbol is None:
            raise ValueError("Symbol must not be None.")
        if quantity is None:
            raise ValueError("Quantity must not be None.")
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        symbol = symbol.upper()
        price = get_current_price(symbol)
        total_proceeds = price * quantity

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            account = Account.from_row(row)
            if account is None:
                return None

            # Verify the account holds enough shares to sell
            cursor.execute(
                "SELECT transaction_type, quantity FROM transactions WHERE account_id = ? AND symbol = ? AND transaction_type IN ('buy', 'sell')",
                (account_id, symbol),
            )
            txn_rows = cursor.fetchall()
            net_quantity = 0
            for t in txn_rows:
                if t["transaction_type"] == "buy":
                    net_quantity += t["quantity"]
                elif t["transaction_type"] == "sell":
                    net_quantity -= t["quantity"]

            if net_quantity < quantity:
                raise ValueError(
                    f"Insufficient shares. You hold {net_quantity} share(s) of {symbol}, attempted to sell {quantity}."
                )

            new_balance = account.balance + total_proceeds
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (new_balance, account_id),
            )
            cursor.execute(
                "INSERT INTO transactions (account_id, transaction_type, symbol, quantity, price, amount) VALUES (?, ?, ?, ?, ?, ?)",
                (account_id, "sell", symbol, quantity, price, total_proceeds),
            )
            conn.commit()
            transaction_id = cursor.lastrowid
            return {
                "transaction_id": transaction_id,
                "message": f"Sold {quantity} share(s) of {symbol} at ${price:.2f} each. Total proceeds: ${total_proceeds:.2f}.",
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
