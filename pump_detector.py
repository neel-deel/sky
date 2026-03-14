import requests
import pandas as pd
import time
from datetime import datetime, timedelta

class PumpDetector:
    def __init__(self, symbol='BTCUSDT', interval='5m', lookback='3 years'):
        self.symbol = symbol
        self.interval = interval
        self.lookback = lookback
        self.data = self.fetch_data()

    def fetch_data(self):
        url = f'https://api.binance.com/api/v3/klines?symbol={self.symbol}&interval={self.interval}&limit=1000'
        end_time = int(time.time() * 1000)
        since = self.get_since_date()
        all_data = []

        while end_time >= since:
            response = requests.get(url + f'&endTime={end_time}')
            candles = response.json()
            if not candles:
                break
            all_data += candles
            end_time = candles[0][0] - 1

        df = pd.DataFrame(all_data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'])
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        return df[['Open Time', 'Close']]

    def get_since_date(self):
        if self.lookback == '3 years':
            return int((datetime.now() - timedelta(days=3*365)).timestamp() * 1000)

    def detect_pumps(self):
        self.data['Close'] = self.data['Close'].astype(float)
        pumps = []
        for i in range(1, len(self.data)):
            if self.data['Close'][i] < self.data['Close'][i-1]:  # Price drop
                low = self.data['Close'][i]
                while i < len(self.data) and self.data['Close'][i] <= low:
                    i += 1
                if i < len(self.data):  # Price recovery
                    for level in range(1, 10):  # 1% to 9%
                        entry_level = low * (1 + level / 100)
                        if self.data['Close'][i] >= entry_level:
                            pumps.append((self.data['Open Time'][i], entry_level))
        return pumps

    def backtest(self):
        trades = []
        pumps = self.detect_pumps()
        for entry_time, entry_price in pumps:
            exit_time = entry_time + timedelta(hours=12)
            # Simulate exit
            exit_price = self.find_exit_price(entry_time, exit_time, entry_price)
            if exit_price:
                trades.append({
                    'Entry Time': entry_time,
                    'Entry Price': entry_price,
                    'Exit Price': exit_price,
                    'Profit': exit_price - entry_price
                })
        self.generate_report(trades)

    def find_exit_price(self, entry_time, exit_time, entry_price):
        exit_data = self.data[(self.data['Open Time'] >= entry_time) & (self.data['Open Time'] <= exit_time)]
        for index, row in exit_data.iterrows():
            if row['Close'] < entry_price:
                return float(row['Close'])
        return exit_data['Close'].iloc[-1] if not exit_data.empty else None

    def generate_report(self, trades):
        total_trades = len(trades)
        wins = sum(1 for trade in trades if trade['Profit'] > 0)
        win_rate = wins / total_trades * 100 if total_trades > 0 else 0
        avg_profit = sum(trade['Profit'] for trade in trades) / total_trades if total_trades > 0 else 0

        print(f'Total Trades: {total_trades}')
        print(f'Win Rate: {win_rate:.2f}%')
        print(f'Average Profit: {avg_profit:.2f}')

if __name__ == '__main__':
    pd = PumpDetector()
    pd.backtest()