import requests
import pandas as pd
import time

coins_list = ['BTC', 'ETH', 'DOGE', 'SHIB', 'SOL', 'PEPE', 'FLOKI']
sentiment_api_keys = {
    'lunarcrush': 'YOUR_LUNARCRUSH_API_KEY',
    'cryptopanic': 'YOUR_CRYPTOPANIC_API_KEY',
    # Optional: Twitter, Santiment, etc.
}

def fetch_lunarcrush_sentiment(coin):
    # Example API call:
    url = f"https://api.lunarcrush.com/v2?data=assets&key={sentiment_api_keys['lunarcrush']}&symbol={coin}"
    resp = requests.get(url)
    # Parse response for score/trending_metric
    try:
        return resp.json()['data'][0]['alt_rank']
    except:
        return 0

def fetch_cryptopanic_news_sentiment(coin):
    # Example pseudo-call (needs real API):
    return 0  # Dummy

def fetch_binance_price(coin):
    # Example - fetch latest price with Binance API
    binance_symbol = coin + "USDT"
    url = f"https://api.binance.com/api/v3/klines?symbol={binance_symbol}&interval=1h&limit=1000"
    resp = requests.get(url)
    if resp.status_code == 200:
        df = pd.DataFrame(resp.json(), columns=['open_time','open','high','low','close','volume','close_time','quote_asset_volume','trade_count','taker_buy_base','taker_buy_quote','ignore'])
        df['close'] = df['close'].astype(float)
        return df
    else:
        return pd.DataFrame()

def calculate_sentiment_score(coin):
    lc_score = fetch_lunarcrush_sentiment(coin)
    cp_score = fetch_cryptopanic_news_sentiment(coin)
    # Weighted average example:
    return 0.7*lc_score + 0.3*cp_score

# Leaderboard:
sentiment_results = {}
for coin in coins_list:
    score = calculate_sentiment_score(coin)
    sentiment_results[coin] = score
    print(f"{coin}: Sentiment Score {score}")

# Pump scanner logic: Top N coins by sentiment
top_coins = sorted(sentiment_results, key=sentiment_results.get, reverse=True)[:5]
print("Top Trending Coins Awaiting Pump based on Sentiment:", top_coins)

# Backtest: Entry on sentiment spike, exit on drop/max hold
for coin in top_coins:
    df_price = fetch_binance_price(coin)
    # (Optional) Backtesting code uses price + sentiment triggers
    # Simulate trades here...

# Print leaderboard/results
print(pd.DataFrame(list(sentiment_results.items()), columns=["Coin", "Sentiment Score"]))