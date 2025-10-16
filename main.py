import time, uuid, requests, random, os, sys, csv
from solders.keypair import Keypair
from common.constants import REST_URL
from common.utils import sign_message
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

# ================= CONFIG =================
MAIN_WALLET_PUBLIC_KEY = "****"
AGENT_WALLET_PRIVATE_KEY = "****"
SYMBOL = "HYPE"
LOT_SIZE = 1.0   # minimum lot
MIN_USD = 400         # minimum trade USD
SLIPPAGE_MIN, SLIPPAGE_MAX = 0.2, 0.5
LEVERAGE_MIN, LEVERAGE_MAX = 1, 2
TRADE_AMOUNT_USD_MIN, TRADE_AMOUNT_USD_MAX = 300, 400
PROFIT_TARGET_MIN, PROFIT_TARGET_MAX = 0.01, 0.05
MAX_HOLD_TIME_MIN, MAX_HOLD_TIME_MAX = 1, 10  # seconds
LOG_FILE = "trade_log.csv"
TARGET_VOLUME_USD = 5000
# ==========================================

MARKET_ORDER_API_URL = f"{REST_URL}/orders/create_market"

# ----------------- Utility -----------------
def log(msg, color=Fore.WHITE):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {color}{msg}{Style.RESET_ALL}")

def append_log(row):
    header = ["time","trade_no","side","amount_btc","amount_usd","leverage","profit","fees","net","status","order_id"]
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def usd_to_btc(usd, price=120000):  
    btc = round(usd / price, 8)
    
    return round(max(btc, LOT_SIZE), 8)

# ----------------- Create Market Order -----------------
def create_market_order(main_pub, agent_wallet, agent_pub, side, amount_btc, reduce_only=False, slippage=None, leverage=None):
    timestamp = int(time.time() * 1_000)
    header = {"timestamp": timestamp, "expiry_window": 5000, "type": "create_market_order"}
    payload = {
        "symbol": SYMBOL,
        "reduce_only": reduce_only,
        "amount": f"{amount_btc:.8f}",
        "side": side,
        "slippage_percent": str(slippage or 0.5),
        "client_order_id": str(uuid.uuid4())
    }
    try:
        _, signature = sign_message(header, payload, agent_wallet)
        request = {
            "account": main_pub,
            "agent_wallet": agent_pub,
            "signature": signature,
            "timestamp": timestamp,
            "expiry_window": 5000,
            **payload
        }
        r = requests.post(MARKET_ORDER_API_URL, json=request, headers={"Content-Type": "application/json"})
        if r.status_code == 200 and r.json().get("success"):
            return True, r.json()
        else:
            return False, r.text
    except Exception as e:
        return False, str(e)

# ----------------- Loop -----------------
def human_like_trader():
    agent_wallet = Keypair.from_base58_string(AGENT_WALLET_PRIVATE_KEY)
    agent_pub = str(agent_wallet.pubkey())
    trade_no = 0

    total_volume_traded_usd = 0.0
    log(f"🤖 Human-like trader started. Target volume: ${TARGET_VOLUME_USD:.2f}", Fore.CYAN)

    while total_volume_traded_usd < TARGET_VOLUME_USD:
        trade_no += 1

        # Random parameters
        side = random.choice(["bid", "ask"])
        usd_amount = random.uniform(TRADE_AMOUNT_USD_MIN, TRADE_AMOUNT_USD_MAX)
        btc_amount = usd_to_btc(usd_amount)
        leverage = random.randint(LEVERAGE_MIN, LEVERAGE_MAX)
        slippage = round(random.uniform(SLIPPAGE_MIN, SLIPPAGE_MAX), 2)
        profit_target = round(random.uniform(PROFIT_TARGET_MIN, PROFIT_TARGET_MAX), 2)
        hold_time = random.uniform(MAX_HOLD_TIME_MIN, MAX_HOLD_TIME_MAX)

        log(f"🚀 Starting trade #{trade_no} | {side.upper()} | ${usd_amount:.2f} (Margin) | {leverage}x | Position Size: ${usd_amount * leverage:.2f}", Fore.CYAN)

        # Place OPEN order
        success, resp = create_market_order(MAIN_WALLET_PUBLIC_KEY, agent_wallet, agent_pub, side, btc_amount, reduce_only=False, slippage=slippage, leverage=leverage)
        if not success:
            log(f"❌ OPEN order failed: {resp}", Fore.RED)
            time.sleep(random.uniform(1,3))
            continue

        order_id = resp.get("data", {}).get("order_id", "N/A")
        log(f"📦 OPEN order sent: {order_id}", Fore.GREEN)

        # ---  (margin * leverage) ---
        total_volume_traded_usd += (usd_amount * leverage)
        log(f"📈 Cumulative Volume (Open): ${total_volume_traded_usd:.2f} / ${TARGET_VOLUME_USD:.2f}", Fore.BLUE)

        # Simulate profit monitoring
        start = time.time()
        profit = 0.0
        while time.time() - start < hold_time:
            profit += 0.01
            
            if profit >= profit_target:
                log("🎯 Profit target reached!", Fore.YELLOW)
                break
            time.sleep(0.5)

        # Place CLOSE order
        close_side = "ask" if side=="bid" else "bid"
        success_close, resp_close = create_market_order(MAIN_WALLET_PUBLIC_KEY, agent_wallet, agent_pub, close_side, btc_amount, reduce_only=True, slippage=slippage, leverage=leverage)
        
        if success_close:
            # ---  position (margin * leverage) ---
            total_volume_traded_usd += (usd_amount * leverage)
            close_order_id = resp_close.get("data", {}).get("order_id", "N/A")
            log(f"🔒 Trade closed: {close_order_id}", Fore.GREEN)
            log(f"📈 Cumulative Volume (Close): ${total_volume_traded_usd:.2f} / ${TARGET_VOLUME_USD:.2f}", Fore.BLUE)

        else:
            close_order_id = "N/A"
            log(f"❌ CLOSE order failed: {resp_close}", Fore.RED)

        fees = round(profit*0.001,4)
        net = round(profit - fees,4)

        append_log([datetime.now().isoformat(), trade_no, side, btc_amount, usd_amount, leverage, profit, fees, net, "closed" if success_close else "failed", order_id])

        
        if total_volume_traded_usd < TARGET_VOLUME_USD:
            sleep_time = random.uniform(5, 30)
            log(f"⏱ Waiting {sleep_time:.1f}s before next trade...\n", Fore.MAGENTA)
            time.sleep(sleep_time)
    
    log(f"🎯 Target volume of ${TARGET_VOLUME_USD:.2f} reached or exceeded. Trader stopping.", Fore.YELLOW)

if __name__ == "__main__":
    try:
        human_like_trader()
    except KeyboardInterrupt:
        log("🛑 Trader stopped manually", Fore.RED)
        sys.exit(0)