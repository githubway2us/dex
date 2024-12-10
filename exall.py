import tkinter as tk
import asyncio
import requests
import threading
import pandas as pd
from tkinter import ttk

# ฟังก์ชันดึงข้อมูลราคา Bitcoin จากแต่ละกระดาน
def get_price_from_exchange(exchange):
    try:
        if exchange == "Binance":
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["price"])}
        
        elif exchange == "Coinbase":
            url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["data"]["amount"])}
        
        elif exchange == "KuCoin":
            url = "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["data"]["price"])}
        
        elif exchange == "Kraken":
            url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["result"]["XXBTZUSD"]["c"][0])}
        
        elif exchange == "Bitfinex":
            url = "https://api.bitfinex.com/v1/pubticker/btcusd"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["last_price"])}
        
        elif exchange == "Bittrex":
            url = "https://api.bittrex.com/v3/markets/BTC-USDT/ticker"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["lastTradeRate"])}
        
        elif exchange == "Gemini":
            url = "https://api.gemini.com/v2/pubticker/btcusd"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["last"])}
        
        elif exchange == "HitBTC":
            url = "https://api.hitbtc.com/api/2/public/ticker/BTCUSD"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["last"])}
        
        elif exchange == "Huobi":
            url = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["tick"]["close"])}
        
        elif exchange == "Gate.io":
            url = "https://api.gateio.ws/api2/1/ticker/btc_usdt"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["last"])}
        
        elif exchange == "OKEX":
            url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["data"][0]["last"])}
        
        elif exchange == "Poloniex":
            url = "https://api.poloniex.com/public?command=returnTicker"
            response = requests.get(url)
            data = response.json()
            return {"Exchange": exchange, "Price": float(data["USDT_BTC"]["last"])}
        
    except Exception as e:
        return {"Exchange": exchange, "Price": None}

# ฟังก์ชันดึงข้อมูลราคาเรียลไทม์จากทุกกระดาน
async def fetch_all_prices():
    exchanges = [
        "Binance", "Coinbase", "KuCoin", "Kraken", "Bitfinex", 
        "Bittrex", "Gemini", "HitBTC", "Huobi", "Gate.io", 
        "OKEX", "Poloniex"
    ]
    prices = []
    
    # ดึงข้อมูลราคาในแต่ละกระดาน
    for exchange in exchanges:
        result = await asyncio.to_thread(get_price_from_exchange, exchange)
        prices.append(result)
    return prices

# ฟังก์ชันเพื่ออัพเดต UI
def update_prices():
    prices = asyncio.run(fetch_all_prices())
    
    # ล้างข้อมูลใน Treeview ก่อน
    for row in tree.get_children():
        tree.delete(row)
    
    # เพิ่มข้อมูลใหม่เข้าใน Treeview
    for price in prices:
        if price["Price"] is not None:
            tree.insert("", "end", values=(price["Exchange"], f"{price['Price']:.2f}"))
    
    # เรียกใช้งานการอัพเดตในทุกๆ 10 วินาที
    root.after(10000, update_prices)

# สร้าง UI ด้วย tkinter
root = tk.Tk()
root.title("Bitcoin Prices from Exchanges")
root.geometry("300x300")  # Adjust window size to accommodate more data

# สร้าง Treeview เพื่อแสดงข้อมูลราคา
columns = ("Exchange", "Price")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("Exchange", text="Exchange")
tree.heading("Price", text="Price (USD)")
tree.pack(fill=tk.BOTH, expand=True)

# เริ่มต้นอัพเดตข้อมูลราคา
update_prices()

# เริ่มต้น UI
root.mainloop()
