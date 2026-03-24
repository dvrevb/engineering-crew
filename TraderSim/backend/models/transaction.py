class Transaction:
    """
    Represents a financial transaction.

    transaction_type: 'buy' | 'sell' | 'deposit' | 'withdrawal'
    """

    VALID_TYPES = {"buy", "sell", "deposit", "withdrawal"}

    def __init__(self, id, account_id, transaction_type, symbol, quantity, price, amount, created_at=None):
        self.id = id
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.amount = amount
        self.created_at = created_at

    def to_dict(self):
        return {
            "transaction_id": self.id,
            "account_id": self.account_id,
            "transaction_type": self.transaction_type,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "amount": self.amount,
            "created_at": str(self.created_at) if self.created_at else None,
        }

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return Transaction(
            id=row["id"],
            account_id=row["account_id"],
            transaction_type=row["transaction_type"],
            symbol=row["symbol"],
            quantity=row["quantity"],
            price=row["price"],
            amount=row["amount"],
            created_at=row["created_at"],
        )
