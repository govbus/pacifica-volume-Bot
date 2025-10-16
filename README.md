# Crypto Trading Bot

This repository contains a Python script for an automated trading bot that executes market orders on a cryptocurrency exchange. The bot is designed to simulate human-like trading behavior by randomizing trade parameters such as side (buy/sell), trade amount, leverage, and holding time, with the goal of reaching a specific trading volume.

---

## Features

- **Automated Market Orders:** Executes market orders to open and close positions automatically.  
- **Human-like Behavior:** Simulates random trading patterns by varying trade size, leverage, slippage, and timing between trades.  
- **Volume Targeting:** Continuously trades until a predefined trading volume in USD is achieved.  
- **Simple Risk Simulation:** Simulates trade decisions based on profit targets and maximum holding times.  
- **Comprehensive Logging:** Records all trade activities, including side, amount, leverage, profit, and status, into a CSV file for later analysis.  
- **Real-time Feedback:** Provides color-coded console output for easy monitoring of the bot's status.  

---

## Getting Started

Follow these instructions to get the bot up and running on your local machine.

### Prerequisites

- Python 3.7+  
- Required Python libraries:  

```bash
pip install requests solders colorama
```

### Installation

1. Clone the repository:

```bash
git clone https://github.com/govbus/pacifica-volume-Bot.git
```

2. Navigate to the project directory:

```bash
cd pacifica-volume-Bot
```

---

## Configuration

Before running the script, configure the trading parameters in the `main.py` file. Open the file and edit the variables within the **CONFIG** section:

- `MAIN_WALLET_PUBLIC_KEY`: Your main wallet's address.  
- `AGENT_WALLET_PRIVATE_KEY`: The private key of the agent wallet used for signing transactions.  
- `SYMBOL`: The trading symbol for the market (e.g., "HYPE").  
- `LOT_SIZE`: The minimum trade size allowed by the exchange.  
- `MIN_USD`: The minimum trade amount in USD.  
- `SLIPPAGE_MIN`, `SLIPPAGE_MAX`: Min/max slippage tolerance for orders.  
- `LEVERAGE_MIN`, `LEVERAGE_MAX`: Min/max leverage to be used for trades.  
- `TRADE_AMOUNT_USD_MIN`, `TRADE_AMOUNT_USD_MAX`: Randomized range for the USD value of each trade's margin.  
- `PROFIT_TARGET_MIN`, `PROFIT_TARGET_MAX`: Simulated profit target range that triggers a position close.  
- `MAX_HOLD_TIME_MIN`, `MAX_HOLD_TIME_MAX`: Randomized range (in seconds) for how long to hold a position.  
- `LOG_FILE`: The name of the CSV file for logging trades.  
- `TARGET_VOLUME_USD`: Total trading volume in USD the bot should aim to achieve before stopping.  

---

## Usage

Run the trading bot with:

```bash
python main.py
```

The bot will start executing trades based on your configuration. It will print its status to the console and log all trades to the specified CSV file.  

To stop the bot manually at any time, press **Ctrl+C**.

---

## How It Works

The script operates in a continuous loop, where each iteration represents a full trade cycle (open and close):

1. **Initialization:** The script starts and aims to trade until the `TARGET_VOLUME_USD` is met.  
2. **Randomization:** Generates random parameters for trade side (bid/ask), margin, leverage, slippage, profit target, and hold time.  
3. **Open Position:** Places a market order to open a new position. The volume of this trade (`margin * leverage`) is added to the cumulative total.  
4. **Simulate Holding:** Pauses for a random duration (`hold_time`) to simulate holding the position and monitoring for a profit target.  
5. **Close Position:** Places a closing market order (opposite side of the open order). Volume of this closing trade is added to cumulative total.  
6. **Logging:** All trade details are appended to the log file.  
7. **Wait:** The bot waits for a random interval before initiating the next trade.  
8. **Completion:** Repeats until total volume traded reaches or exceeds `TARGET_VOLUME_USD`, then the script terminates.  

---

## Disclaimer

This script is provided for **educational and informational purposes only**. Trading cryptocurrencies involves substantial risk and is not suitable for every investor. The authors and contributors of this project are **not responsible** for any financial losses you may incur. Use this script entirely at your own risk.
