# Automated Trading Bot for Binance

A **Flask-based** bot for automated trading on Binance, triggered by **TradingView** webhooks. Designed to run 24/7 on a **Raspberry Pi**, with external accessibility provided via **ngrok**.

---

## Features

- Receives **TradingView alerts** via webhooks.
- Parses **BUY/SELL** signals and executes **market orders** on Binance.
- Manages API credentials securely using `.env`.
- Includes logging for error handling and debugging.
- Easy to deploy and run on Raspberry Pi with **ngrok**.

---

## Usage

1. **Start the Flask server**  
   - The bot listens for webhooks at the `/webhook` endpoint.  
   - You can test the server by accessing the `/` route or `/test`.

2. **Use ngrok to expose the Flask server**  
   - Forward the local Flask server with ngrok to create a public URL.  
   - Copy the ngrok URL and use it as the webhook URL in TradingView.

3. **Configure TradingView alerts**  
   - Set the webhook URL to the ngrok public URL (e.g., `https://<random>.ngrok.io/webhook`).  
   - Customize the alert message in TradingView to provide necessary data:
     ```text
     order BUY @ 50 filled on XRP
     ```
     This will:
     - Trigger a **BUY** order
     - For **50 units**
     - On **XRPUSDT** (the bot appends `USDT` by default)

---

## Example Alert Format

TradingView webhook alert message:
```text
order BUY @ 50 filled on BTC
```
The bot will:

- Execute a **BUY** order
- With 50 **units**
- On **BTC/USDT**

## Running on Raspberry Pi with ngrok

- Deploy the bot to your Raspberry Pi.
- Start the Flask server and yse ngrok to forward it.
- Configure TradingView to send alerts to ngrok URL.
- Leave the Raspberry Pi running to handle webhooks 24/7

## Disclaimer

- This bot is provided **as-is** without any guarantees of profit or success.
- Use **at your own risk**, especially when trading real funds.
- Test thoroughly through paper trading, small amounts, or demo accounts before live trading.
- Please ensure you have a strategy prepared on TradingView for the script to function.

## Happy Trading!

