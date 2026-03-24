import gradio as gr
import requests

BACKEND_URL = "http://localhost:5000"


def create_account(username, initial_deposit):
    if not username or str(username).strip() == "":
        return {"error": "Username is required."}
    if initial_deposit is None:
        return {"error": "Initial deposit is required."}
    try:
        response = requests.post(
            f"{BACKEND_URL}/accounts/create",
            json={"username": str(username).strip(), "initial_deposit": float(initial_deposit)},
            timeout=10,
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the server running on port 5000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}


def deposit_funds(account_id, amount):
    if account_id is None:
        return {"error": "Account ID is required."}
    if amount is None:
        return {"error": "Deposit amount is required."}
    try:
        response = requests.post(
            f"{BACKEND_URL}/accounts/deposit",
            json={"account_id": int(account_id), "amount": float(amount)},
            timeout=10,
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the server running on port 5000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}


def withdraw_funds(account_id, amount):
    if account_id is None:
        return {"error": "Account ID is required."}
    if amount is None:
        return {"error": "Withdrawal amount is required."}
    try:
        response = requests.post(
            f"{BACKEND_URL}/accounts/withdraw",
            json={"account_id": int(account_id), "amount": float(amount)},
            timeout=10,
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the server running on port 5000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}


def buy_shares(account_id, symbol, quantity):
    if account_id is None:
        return {"error": "Account ID is required."}
    if not symbol or str(symbol).strip() == "":
        return {"error": "Stock symbol is required."}
    if quantity is None:
        return {"error": "Quantity is required."}
    try:
        response = requests.post(
            f"{BACKEND_URL}/transactions/buy",
            json={
                "account_id": int(account_id),
                "symbol": str(symbol).strip().upper(),
                "quantity": int(quantity),
            },
            timeout=10,
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the server running on port 5000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}


def sell_shares(account_id, symbol, quantity):
    if account_id is None:
        return {"error": "Account ID is required."}
    if not symbol or str(symbol).strip() == "":
        return {"error": "Stock symbol is required."}
    if quantity is None:
        return {"error": "Quantity is required."}
    try:
        response = requests.post(
            f"{BACKEND_URL}/transactions/sell",
            json={
                "account_id": int(account_id),
                "symbol": str(symbol).strip().upper(),
                "quantity": int(quantity),
            },
            timeout=10,
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the server running on port 5000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}


def get_portfolio(account_id):
    if account_id is None:
        return {"error": "Account ID is required."}
    try:
        response = requests.get(
            f"{BACKEND_URL}/accounts/{int(account_id)}/portfolio",
            timeout=10,
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the server running on port 5000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}


def get_transactions(account_id):
    if account_id is None:
        return {"error": "Account ID is required."}
    try:
        response = requests.get(
            f"{BACKEND_URL}/accounts/{int(account_id)}/transactions",
            timeout=10,
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the server running on port 5000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}


with gr.Blocks(title="TraderSim - Stock Trading Simulator", theme=gr.themes.Soft()) as app:

    gr.Markdown("# TraderSim - Stock Trading Simulator")
    gr.Markdown(
        "Manage your trading account, buy and sell shares, and track your portfolio performance.\n\n"
        "**Backend must be running at** `http://localhost:5000`"
    )

    with gr.Tab("Account Management"):
        gr.Markdown("## Account Management")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Create New Account")
                create_username = gr.Textbox(label="Username", placeholder="e.g. alice")
                create_deposit = gr.Number(label="Initial Deposit ($)", value=1000.0)
                create_btn = gr.Button("Create Account", variant="primary")
                create_output = gr.JSON(label="Response")
                create_btn.click(
                    fn=create_account,
                    inputs=[create_username, create_deposit],
                    outputs=[create_output],
                )

            with gr.Column():
                gr.Markdown("### Deposit Funds")
                deposit_account_id = gr.Number(label="Account ID", precision=0)
                deposit_amount = gr.Number(label="Deposit Amount ($)", value=100.0)
                deposit_btn = gr.Button("Deposit", variant="primary")
                deposit_output = gr.JSON(label="Response")
                deposit_btn.click(
                    fn=deposit_funds,
                    inputs=[deposit_account_id, deposit_amount],
                    outputs=[deposit_output],
                )

            with gr.Column():
                gr.Markdown("### Withdraw Funds")
                withdraw_account_id = gr.Number(label="Account ID", precision=0)
                withdraw_amount = gr.Number(label="Withdrawal Amount ($)", value=100.0)
                withdraw_btn = gr.Button("Withdraw", variant="primary")
                withdraw_output = gr.JSON(label="Response")
                withdraw_btn.click(
                    fn=withdraw_funds,
                    inputs=[withdraw_account_id, withdraw_amount],
                    outputs=[withdraw_output],
                )

    with gr.Tab("Trade Shares"):
        gr.Markdown("## Buy and Sell Shares")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Buy Shares")
                buy_account_id = gr.Number(label="Account ID", precision=0)
                buy_symbol = gr.Textbox(label="Stock Symbol", placeholder="e.g. AAPL")
                buy_quantity = gr.Number(label="Quantity", value=1, precision=0)
                buy_btn = gr.Button("Buy Shares", variant="primary")
                buy_output = gr.JSON(label="Response")
                buy_btn.click(
                    fn=buy_shares,
                    inputs=[buy_account_id, buy_symbol, buy_quantity],
                    outputs=[buy_output],
                )

            with gr.Column():
                gr.Markdown("### Sell Shares")
                sell_account_id = gr.Number(label="Account ID", precision=0)
                sell_symbol = gr.Textbox(label="Stock Symbol", placeholder="e.g. AAPL")
                sell_quantity = gr.Number(label="Quantity", value=1, precision=0)
                sell_btn = gr.Button("Sell Shares", variant="stop")
                sell_output = gr.JSON(label="Response")
                sell_btn.click(
                    fn=sell_shares,
                    inputs=[sell_account_id, sell_symbol, sell_quantity],
                    outputs=[sell_output],
                )

    with gr.Tab("Portfolio"):
        gr.Markdown("## View Portfolio")
        gr.Markdown(
            "Enter your Account ID to view your current portfolio value, "
            "individual holdings, and total profit/loss."
        )
        portfolio_account_id = gr.Number(label="Account ID", precision=0)
        portfolio_btn = gr.Button("Load Portfolio", variant="primary")
        portfolio_output = gr.JSON(label="Portfolio Details")
        portfolio_btn.click(
            fn=get_portfolio,
            inputs=[portfolio_account_id],
            outputs=[portfolio_output],
        )

    with gr.Tab("Transaction History"):
        gr.Markdown("## Transaction History")
        gr.Markdown(
            "Enter your Account ID to retrieve a full list of all past "
            "buy, sell, deposit, and withdrawal transactions."
        )
        history_account_id = gr.Number(label="Account ID", precision=0)
        history_btn = gr.Button("Load Transactions", variant="primary")
        history_output = gr.JSON(label="Transaction List")
        history_btn.click(
            fn=get_transactions,
            inputs=[history_account_id],
            outputs=[history_output],
        )

    gr.Markdown("---\nTraderSim | Built with Gradio and Flask")


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, show_error=True)
