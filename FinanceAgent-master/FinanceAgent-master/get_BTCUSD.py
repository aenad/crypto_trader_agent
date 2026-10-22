import requests
import datetime
import pandas as pd

# CryptoCompare API for hourly candles
url = "https://min-api.cryptocompare.com/data/v2/histohour"
params = {
    "fsym": "BTC",
    "tsym": "USD",
    "limit": 168 - 1,  # 7 days * 24 hours = 168 points - 1 because it includes now
    "aggregate": 1
}

response = requests.get(url, params=params)
data = response.json()

if data["Response"] == "Success":
    df = pd.DataFrame(data["Data"]["Data"])
    df["datetime"] = pd.to_datetime(df["time"], unit="s")
    df = df[["datetime", "open", "high", "low", "close", "volumefrom", "volumeto"]]
    df.columns = ["datetime", "open", "high", "low", "close", "volume_btc", "volume_usd"]

    print(df.head())  # Preview first rows
    df.to_csv("btc_ohlcv_last_7_days.csv", index=False)
    print("✅ Saved to btc_ohlcv_last_7_days.csv")
else:
    print("❌ API Error:", data.get("Message", "Unknown error"))
