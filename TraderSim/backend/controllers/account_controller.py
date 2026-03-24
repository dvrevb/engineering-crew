from flask import Blueprint, request, jsonify
from backend.services.account_service import AccountService
from backend.services.portfolio_service import PortfolioService

account_bp = Blueprint("account_bp", __name__)
account_service = AccountService()
portfolio_service = PortfolioService()


# ---------------------------------------------------------------------------
# Account endpoints
# ---------------------------------------------------------------------------

@account_bp.route("/accounts/create", methods=["POST"])
def create_account():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON."}), 400

        username = data.get("username")
        initial_deposit = data.get("initial_deposit")

        if username is None:
            return jsonify({"error": "username is required."}), 400
        if initial_deposit is None:
            return jsonify({"error": "initial_deposit is required."}), 400

        result = account_service.create_account(username, initial_deposit)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500


@account_bp.route("/accounts/deposit", methods=["POST"])
def deposit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON."}), 400

        account_id = data.get("account_id")
        amount = data.get("amount")

        if account_id is None:
            return jsonify({"error": "account_id is required."}), 400
        if amount is None:
            return jsonify({"error": "amount is required."}), 400

        result = account_service.deposit(account_id, amount)
        if result is None:
            return jsonify({"error": f"Account {account_id} not found."}), 404
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500


@account_bp.route("/accounts/withdraw", methods=["POST"])
def withdraw():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON."}), 400

        account_id = data.get("account_id")
        amount = data.get("amount")

        if account_id is None:
            return jsonify({"error": "account_id is required."}), 400
        if amount is None:
            return jsonify({"error": "amount is required."}), 400

        result = account_service.withdraw(account_id, amount)
        if result is None:
            return jsonify({"error": f"Account {account_id} not found."}), 404
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500


# ---------------------------------------------------------------------------
# Transaction endpoints
# ---------------------------------------------------------------------------

@account_bp.route("/transactions/buy", methods=["POST"])
def buy():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON."}), 400

        account_id = data.get("account_id")
        symbol = data.get("symbol")
        quantity = data.get("quantity")

        if account_id is None:
            return jsonify({"error": "account_id is required."}), 400
        if symbol is None:
            return jsonify({"error": "symbol is required."}), 400
        if quantity is None:
            return jsonify({"error": "quantity is required."}), 400

        result = portfolio_service.record_buy(account_id, symbol, quantity)
        if result is None:
            return jsonify({"error": f"Account {account_id} not found."}), 404
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500


@account_bp.route("/transactions/sell", methods=["POST"])
def sell():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON."}), 400

        account_id = data.get("account_id")
        symbol = data.get("symbol")
        quantity = data.get("quantity")

        if account_id is None:
            return jsonify({"error": "account_id is required."}), 400
        if symbol is None:
            return jsonify({"error": "symbol is required."}), 400
        if quantity is None:
            return jsonify({"error": "quantity is required."}), 400

        result = portfolio_service.record_sell(account_id, symbol, quantity)
        if result is None:
            return jsonify({"error": f"Account {account_id} not found."}), 404
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500


# ---------------------------------------------------------------------------
# Portfolio & transaction history endpoints
# ---------------------------------------------------------------------------

@account_bp.route("/accounts/<int:account_id>/portfolio", methods=["GET"])
def get_portfolio(account_id):
    try:
        if account_id is None:
            return jsonify({"error": "account_id is required."}), 400

        result = portfolio_service.get_portfolio(account_id)
        if result is None:
            return jsonify({"error": f"Account {account_id} not found."}), 404
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500


@account_bp.route("/accounts/<int:account_id>/transactions", methods=["GET"])
def get_transactions(account_id):
    try:
        if account_id is None:
            return jsonify({"error": "account_id is required."}), 400

        # Verify account exists first
        account = account_service.get_account(account_id)
        if account is None:
            return jsonify({"error": f"Account {account_id} not found."}), 404

        transactions = account_service.get_transactions(account_id)
        return jsonify({"transactions": transactions}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500
