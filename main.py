from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
import os
from dotenv import load_dotenv
import logging
import re

# Load environment variables
load_dotenv()

# Binance API credentials
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Initialize Binance client
client = Client(API_KEY, API_SECRET, tld='us')

# Flask app
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    """
    Root endpoint to verify the webhook server is running.
    """
    return "Webhook server is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Receive alerts from TradingView and execute trades on Binance.
    """
    try:
        # Get the raw alert message from the request
        message = request.data.decode('utf-8')
        logging.info(f"Received message: {message}")

        # Parse the message to extract action, symbol, quantity
        action, symbol, quantity = parse_alert_message(message)

        if not action or not symbol or not quantity:
            raise ValueError("Invalid data extracted from the alert message.")

        # Execute the trade on Binance
        if action == "BUY":
            place_order(symbol, quantity, SIDE_BUY)
        elif action == "SELL":
            place_order(symbol, quantity, SIDE_SELL)
        else:
            logging.error(f"Unknown action: {action}")
            return jsonify({"error": "Unknown action"}), 400

        return jsonify({"success": True, "action": action, "symbol": symbol}), 200

    except Exception as e:
        logging.exception("Error processing webhook")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test_binance():
    """
    Test endpoint to verify connection with Binance API.
    """
    try:
        # Fetch account information to confirm API connection
        account = client.get_account()
        return jsonify({
            "status": "success",
            "account_type": account['accountType'],
            "balances": account['balances']
        }), 200
    except Exception as e:
        logging.error(f"Error testing Binance API: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def parse_alert_message(message):
    """
    Parse the TradingView alert message to extract action, symbol, and quantity.
    """
    try:
        # Regular expression patterns to extract data
        action_pattern = r'order (\w+)'  # Extracts 'BUY' or 'SELL'
        quantity_pattern = r'@ ([\d\.]+)'  # Extracts quantity after '@'
        symbol_pattern = r'filled on (\w+)'  # Extracts symbol after 'filled on'

        # Extract action
        action_match = re.search(action_pattern, message)
        action = action_match.group(1).upper() if action_match else None

        # Extract quantity
        quantity_match = re.search(quantity_pattern, message)
        quantity = float(quantity_match.group(1)) if quantity_match else None

        # Extract symbol
        symbol_match = re.search(symbol_pattern, message)
        symbol = symbol_match.group(1).upper() if symbol_match else None

        # Adjust symbol for Binance (e.g., 'XRP' to 'XRPUSDT')
        if symbol:
            symbol = symbol + 'USDT'  # Modify this if trading against a different base currency

        return action, symbol, quantity
    except Exception as e:
        logging.error(f"Error parsing alert message: {e}")
        return None, None, None

def get_step_size(symbol):
    """
    Retrieve the step size for a given symbol from Binance.
    """
    try:
        info = client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize'])
        return None
    except Exception as e:
        logging.error(f"Error retrieving step size for symbol {symbol}: {e}")
        return None

def place_order(symbol, quantity, side):
    """
    Place a market order on Binance.
    """
    try:
        # Get step size for symbol
        step_size = get_step_size(symbol)
        if step_size:
            # Adjust quantity to step size
            from binance.helpers import round_step_size
            quantity = round_step_size(quantity, step_size)
        else:
            logging.error(f"Could not retrieve step size for symbol {symbol}")
            raise Exception("Step size not found")

        # Place the market order
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        logging.info(f"Order placed: {order}")
        return order
    except Exception as e:
        logging.error(f"Error placing order on Binance: {e}")
        raise

if __name__ == '__main__':
    app.run(port=5000)
