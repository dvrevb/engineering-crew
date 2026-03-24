class Account:
    """Represents a user trading account."""

    def __init__(self, id, username, balance, initial_deposit):
        self.id = id
        self.username = username
        self.balance = balance
        self.initial_deposit = initial_deposit

    def to_dict(self):
        return {
            "account_id": self.id,
            "username": self.username,
            "balance": self.balance,
            "initial_deposit": self.initial_deposit,
        }

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return Account(
            id=row["id"],
            username=row["username"],
            balance=row["balance"],
            initial_deposit=row["initial_deposit"],
        )
