import tkinter as tk
from tkinter import messagebox
import requests
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Function to read purchase data from the log file
def read_purchase_log():
    purchases = []
    try:
        with open("purchase_log.txt", "r") as file:
            for line in file:
                # Split the line by spaces, assuming the format is consistent
                buy_info = line.split()

                # Ensure the line contains enough data
                if len(buy_info) >= 4:
                    try:
                        # Try to extract the buy price
                        buy_price = float(buy_info[3][1:])  # Remove the '$' symbol
                        amount = float(buy_info[1])  # Extract the amount (assumed to be the 2nd element)
                        profit_loss = float(buy_info[5][1:])  # Extract the profit/loss (assumed to be the 6th element)
                        purchases.append((buy_price, amount, profit_loss))
                    except ValueError:
                        # Handle case where conversion to float fails
                        print(f"Skipping invalid entry: {line}")
                else:
                    print(f"Skipping malformed line: {line}")
    except FileNotFoundError:
        print("Purchase log file not found.")
    return purchases



# Function to plot the purchase data
def plot_purchase_data():
    purchases = read_purchase_log()
    
    if not purchases:
        messagebox.showwarning("No Data", "No purchase data available to plot.")
        return
    
    # Extract the necessary data for plotting
    timestamps = [purchase[0] for purchase in purchases]
    buy_prices = [purchase[1] for purchase in purchases]
    profits = [purchase[3] for purchase in purchases]
    
    # Convert timestamps to date format for better readability
    dates = [time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)) for ts in timestamps]
    
    # Plotting the data using matplotlib
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    ax1.set_xlabel("Timestamp")
    ax1.set_ylabel("Buy Price ($)", color='tab:blue')
    ax1.plot(dates, buy_prices, color='tab:blue', label="Buy Price", marker='o', linestyle='-')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    
    ax2 = ax1.twinx()  # Create a second y-axis for profit/loss
    ax2.set_ylabel("Profit/Loss ($)", color='tab:red')
    ax2.plot(dates, profits, color='tab:red', label="Profit/Loss", marker='x', linestyle='--')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    
    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Title and display the plot
    plt.title("Purchase Data: Buy Prices and Profit/Loss over Time")
    fig.tight_layout()
    plt.show()

# Initialize global variables
previous_price = None
countdown_time = 60  # Countdown timer set to 60 seconds
purchases = []

# Assuming these variables are defined earlier in your code:
btn_color = "lightblue"  # Example button color
fg_color = "black"       # Example text color
font_style = ("Arial", 12)  # Example font style

def fetch_token_data(token_address):
    try:
        response = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token_address}")
        data = response.json()
        if not data or 'pairs' not in data or not data['pairs']:
            raise ValueError("No data available for the specified token.")
        token_data = data['pairs'][0]
        # Extract base token and other details
        base_token = token_data.get('baseToken', {})
        pricechange24h = token_data.get('priceChange', {})
        market_cap = token_data.get('marketCap', {})

        symbol = base_token.get('symbol', 'No Name')

        
        # Extract marketcap and price change
        #market_cap = marketcap.get('marketcap', 'Not Available')
        price_change_24h = pricechange24h.get('h24', 'Not Available')
        
        return token_data, symbol, market_cap, price_change_24h
    except Exception as e:
        return f"Error: {e}", None, None, None

def update_token_info():
    token_address = token_entry.get()
    if not token_address:
        messagebox.showwarning("Warning", "Please enter a token address!")
        return

    token_data, symbol, market_cap, price_change_24h = fetch_token_data(token_address)
    if isinstance(token_data, str):
        token_info_label.config(text=f"Error fetching data: {token_data}")
        return

    # Extract token details
    price = token_data['priceUsd']
    volume_24h = token_data['volume']['h24']
    liquidity_usd = token_data['liquidity']['usd']
    
    # Update labels with fetched data
    price_label.config(text=f"Price: ${price}")
    volume_label.config(text=f"24h Volume: {volume_24h} SOL")
    liquidity_label.config(text=f"Liquidity (USD): ${liquidity_usd}")
    symbol_label.config(text=f"Coin: {symbol}")
    
    # Display market cap and price change
    market_cap_label.config(text=f"Market Cap: ${market_cap}")
    price_change_label.config(text=f"24h Price Change: {price_change_24h} %")

    # Compare price and log changes
    log_price_change(price)
    update_profit_loss(price)

def log_price_change(current_price):
    global previous_price
    if previous_price is None or current_price != previous_price:
        with open("price_changes.txt", "a") as file:
            file.write(f"Price changed: {current_price} at {time.ctime()}\n")
        previous_price = current_price

def update_profit_loss(current_price):
    total_profit_loss = 0
    for purchase in purchases:
        buy_price, amount = purchase
        profit_loss = (current_price - buy_price) * amount
        total_profit_loss += profit_loss
    
    profit_loss_label.config(text=f"Total Profit/Loss: ${total_profit_loss:.2f}")

def track_price_changes():
    global countdown_time
    token_address = token_entry.get()
    if not token_address:
        return
    
    while True:
        update_token_info()  # Fetch and update token data
        countdown_time = 60  # Reset countdown timer to 60 seconds
        update_timer_label()  # Update the countdown display
        time.sleep(60)  # Check every 60 seconds

def update_timer_label():
    timer_label.config(text=f"Next check in: {countdown_time} seconds")
    if countdown_time > 0:
        countdown_time -= 1
    root.after(1000, update_timer_label)  # Update every second

def show_log():
    with open("price_changes.txt", "r") as file:
        logs = file.readlines()
    log_text.config(state=tk.NORMAL)
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "".join(logs))
    log_text.config(state=tk.DISABLED)

def add_purchase():
    try:
        buy_price = float(buy_price_entry.get())
        amount = float(amount_entry.get())
        
        # คำนวณราคาต่อเหรียญ
        price_per_coin = buy_price / amount if amount != 0 else 0
        
        # คำนวณผลกำไร/ขาดทุน
        current_price = float(price_label.cget("text").replace('Price: $', '').strip())
        profit_loss = (current_price - buy_price) * amount
        
        # บันทึกการซื้อและกำไร/ขาดทุน
        purchases.append((buy_price, amount, profit_loss))
        
        # แสดงผลใน Purchase Log
        purchase_log.config(state=tk.NORMAL)
        purchase_log.insert(tk.END, f"Bought {amount} tokens at ${buy_price} - Profit/Loss: ${profit_loss:.2f} - Price per coin: ${price_per_coin:.2f}\n")
        purchase_log.config(state=tk.DISABLED)

        # แสดงผลในคอลัมน์ 2
        price_per_coin_label.config(text=f"Price per coin: ${price_per_coin:.2f}")

        # บันทึกการซื้อในไฟล์
        with open("purchase_log.txt", "a") as file:
            file.write(f"Bought {amount} tokens at ${buy_price}, Profit/Loss: ${profit_loss:.2f}, Price per coin: ${price_per_coin:.2f} at {time.ctime()}\n")
        
        buy_price_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter valid numbers for price and amount.")

# Create main window
root = tk.Tk()
root.title("Token Price and Info Checker")
root.geometry("800x600")

# Modern colors and font settings
bg_color = "#2C3E50"  # Dark background color
fg_color = "#ECF0F1"  # Light foreground color
btn_color = "#3498DB"  # Button color
hover_color = "#2980B9"  # Button hover color
font_style = ("Roboto", 12)

# Create a frame for organizing content into 4 columns with borders
frame = tk.Frame(root, bd=2, relief="solid", bg=bg_color)
frame.pack(padx=10, pady=10)

# Column 1: Token Address Input and Info
column1 = tk.Frame(frame, bd=1, relief="solid", bg=bg_color)
column1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

tk.Label(column1, text="Enter Token Address:", fg=fg_color, bg=bg_color, font=font_style).pack(pady=5)
token_entry = tk.Entry(column1, width=40, font=font_style)
token_entry.pack(pady=5)

fetch_button = tk.Button(column1, text="Fetch Token Data", command=update_token_info, bg=btn_color, fg=fg_color, font=font_style,
                         activebackground=hover_color, relief="solid", borderwidth=2, highlightthickness=0)
fetch_button.pack(pady=10)

# Info Display
price_label = tk.Label(column1, text="Price: --", font=("Helvetica", 14), fg=fg_color, bg=bg_color)
price_label.pack(pady=5)
volume_label = tk.Label(column1, text="24h Volume: --", font=("Helvetica", 14), fg=fg_color, bg=bg_color)
volume_label.pack(pady=5)
liquidity_label = tk.Label(column1, text="Liquidity (USD): --", font=("Helvetica", 14), fg=fg_color, bg=bg_color)
liquidity_label.pack(pady=5)

# Token symbol label
symbol_label = tk.Label(column1, text="Symbol: --", font=("Helvetica", 14), fg=fg_color, bg=bg_color)
symbol_label.pack(pady=5)
    # New labels for market cap and price change
market_cap_label = tk.Label(column1, text="Market Cap: --")
market_cap_label.pack(pady=5)
price_change_label = tk.Label(column1, text="24h Price Change: --")
price_change_label.pack(pady=5)

# Column 2: Profit/Loss and Timer
column2 = tk.Frame(frame, bd=1, relief="solid", bg=bg_color)
column2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

tk.Label(column2, text="รายละเอียด:", font=("Helvetica", 14), fg=fg_color, bg=bg_color).pack(pady=5)
profit_loss_label = tk.Label(column2, text="คัมภีร์สายกระบี่คริปโต", font=("Helvetica", 14), fg=fg_color, bg=bg_color)
profit_loss_label.pack(pady=5)

timer_label = tk.Label(column2, text="Token Price and Info Checker", font=("Helvetica", 14), fg=fg_color, bg=bg_color)
timer_label.pack(pady=10)

# ในคอลัมน์ 2 เพิ่ม Label สำหรับแสดงราคาต่อเหรียญ
price_per_coin_label = tk.Label(column2, text="Price per coin: --", font=("Helvetica", 14), fg=fg_color, bg=bg_color)
price_per_coin_label.pack(pady=5)

# Column 3: Purchase Entry
column3 = tk.Frame(frame, bd=1, relief="solid", bg=bg_color)
column3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

tk.Label(column3, text="Enter Buy Price:", font=("Helvetica", 14), fg=fg_color, bg=bg_color).pack(pady=5)
buy_price_entry = tk.Entry(column3, width=40, font=font_style)
buy_price_entry.pack(pady=5)

tk.Label(column3, text="Enter Amount:", font=("Helvetica", 14), fg=fg_color, bg=bg_color).pack(pady=5)
amount_entry = tk.Entry(column3, width=40, font=font_style)
amount_entry.pack(pady=5)

purchase_button = tk.Button(column3, text="Add Purchase", command=add_purchase, bg=btn_color, fg=fg_color, font=font_style,
                            activebackground=hover_color, relief="solid", borderwidth=2, highlightthickness=0)
purchase_button.pack(pady=10)

# Purchase Log display
purchase_log = tk.Text(column3, width=50, height=10, font=("Helvetica", 12), fg=fg_color, bg=bg_color, wrap=tk.WORD, state=tk.DISABLED)
purchase_log.pack(pady=10)

# Column 4: Log
column4 = tk.Frame(frame, bd=1, relief="solid", bg=bg_color)
column4.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

log_button = tk.Button(column4, text="View Logs", command=show_log, bg=btn_color, fg=fg_color, font=font_style,
                       activebackground=hover_color, relief="solid", borderwidth=2, highlightthickness=0)
log_button.pack(pady=10)

log_text = tk.Text(column4, width=50, height=40, font=("Helvetica", 12), fg=fg_color, bg=bg_color, wrap=tk.WORD, state=tk.DISABLED)
log_text.pack(pady=10)

# Create a button to plot the purchase data
plot_button = tk.Button(root, text="Plot Purchase Data", command=plot_purchase_data, width=20, height=2)
plot_button.pack(pady=20)

root.mainloop()
