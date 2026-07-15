import os
import sys

# When launched with pythonw.exe (e.g. via Tradesight.vbs), there is no console
# so sys.stdout / sys.stderr are None. Any print() then raises and crashes the
# route mid-request. Redirect to a log file so the many print() calls are safe
# and still recorded for debugging.
def _ensure_std_streams():
    if sys.stdout is not None and sys.stderr is not None:
        return
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tradesight.log')
    try:
        log_file = open(log_path, 'a', buffering=1, encoding='utf-8')
    except Exception:
        log_file = open(os.devnull, 'w')
    if sys.stdout is None:
        sys.stdout = log_file
    if sys.stderr is None:
        sys.stderr = log_file

_ensure_std_streams()

import yfinance as yf
import requests
import sqlite3
from datetime import date
from flask import Flask, request, jsonify, send_file, send_from_directory
import pandas as pd
import plotly.graph_objects as go
from flask_cors import CORS
import final_prediction_code
from contract_note_importer import (
    scan_and_import_all, get_processed_files,
    set_watcher_username, start_watcher,
)
from gmail_contract_fetcher import fetch_new_contract_notes, start_gmail_watcher

# Load environment variables from .env if present
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

load_env()


# # import pandas as pd
# import functools
# print = functools.partial(print, flush=True)


# Project paths. app.py lives in backend/; the frontend and generated output
# live in sibling folders so the three concerns (code / UI / artifacts) stay
# cleanly separated.
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR  = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))
ANALYTICS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'analytics_charts'))
CHARTS_DIR    = os.path.join(ANALYTICS_DIR, 'charts')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='/static')
os.makedirs(CHARTS_DIR, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/charts/<path:filename>')
def charts(filename):
    """Serve generated Plotly charts (written to ../analytics_charts/charts) to
    the dashboard iframes."""
    return send_from_directory(CHARTS_DIR, filename)

def apply_premium_theme(fig, title, yaxis_title=None, xaxis_title=None, show_legend=True):
    fig.update_layout(
        paper_bgcolor='#0a0c10',
        plot_bgcolor='#0a0c10',
        title={
            'text': title,
            'y': 0.93,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'family': 'Outfit, sans-serif', 'size': 18, 'color': '#f3f4f6'}
        },
        font=dict(
            family="Outfit, sans-serif",
            color="#9ca3af"
        ),
        xaxis=dict(
            title=dict(text=xaxis_title, font=dict(family="Outfit, sans-serif", size=13, color="#9ca3af")) if xaxis_title else None,
            gridcolor='rgba(255, 255, 255, 0.05)',
            zerolinecolor='rgba(255, 255, 255, 0.08)',
            tickfont=dict(family="Inter, sans-serif", size=11, color="#9ca3af"),
            showgrid=True,
            showline=True,
            linecolor='rgba(255, 255, 255, 0.08)'
        ),
        yaxis=dict(
            title=dict(text=yaxis_title, font=dict(family="Outfit, sans-serif", size=13, color="#9ca3af")) if yaxis_title else None,
            gridcolor='rgba(255, 255, 255, 0.05)',
            zerolinecolor='rgba(255, 255, 255, 0.08)',
            tickfont=dict(family="Inter, sans-serif", size=11, color="#9ca3af"),
            showgrid=True,
            showline=True,
            linecolor='rgba(255, 255, 255, 0.08)'
        ),
        showlegend=show_legend,
        legend=dict(
            font=dict(family="Inter, sans-serif", size=11, color="#9ca3af"),
            bgcolor='rgba(10, 12, 16, 0.6)',
            bordercolor='rgba(255, 255, 255, 0.08)',
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ) if show_legend else None,
        margin=dict(t=80, b=40, l=60, r=40),
        hoverlabel=dict(
            bgcolor="#111620",
            bordercolor="#3a86ff",
            font=dict(family="Inter, sans-serif", size=12, color="#f3f4f6")
        ),
        hovermode="x unified"
    )


CORS(app)

def connection():
    print("connection")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Users(
                   Sno INTEGER PRIMARY KEY AUTOINCREMENT,
                   Username TEXT NOT NULL UNIQUE,
                   Password TEXT NOT NULL UNIQUE,
                   Email TEXT NOT NULL UNIQUE
                   )
""")
    
    conn.commit()
    conn.close()

connection()

def connection2():
    print("connection2")
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Stocks (
                   StockID INTEGER PRIMARY KEY AUTOINCREMENT,
                   Username TEXT NOT NULL,
                   StockName TEXT NOT NULL,
                   Quantity INTEGER NOT NULL,
                   Price_per_share REAL NOT NULL,
                   Date DATE DEFAULT CURRENT_DATE,
                   ticker_symbol TEXT NOT NULL
                   )
""")
    
    conn.commit()
    conn.close()

connection2()

@app.route('/add_stock', methods=['POST'])
def add_stock():
    print("add_stock")
    try:
        data = request.get_json()
        username = data['username']
        stock_name = data['stock_name']
        quantity = int(data['quantity'])
        price_per_share = float(data['price_per_share'])
        date_actual = data.get('date', date.today().strftime("%Y-%m-%d"))

        # Validate ticker BEFORE writing to DB so invalid stocks don't pollute the portfolio
        ticker_symbol = search_ticker_strict(stock_name)
        if not ticker_symbol:
            return jsonify({"error": f"'{stock_name}' is not a recognized stock. Please check the name or symbol."}), 400

        live_price = get_live_price(ticker_symbol)
        if live_price is None:
            return jsonify({"error": f"Could not fetch live price for '{stock_name}'. Ticker may be invalid or markets unreachable."}), 400

        # Store in DB only after validation passes
        conn = sqlite3.connect('stock.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Stocks (Username, StockName, Quantity, Price_per_share, Date, ticker_symbol)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, stock_name, quantity, price_per_share, date_actual, ticker_symbol))
            conn.commit()
        finally:
            conn.close()

        # Prepare response
        temp = [stock_name, quantity, price_per_share, date_actual]
        temp.append(live_price)
        temp.append((live_price - price_per_share) * quantity)

        # Get percentage change
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist_data = ticker.history(period="2d", interval="1d")

            if not hist_data.empty and len(hist_data["Close"]) >= 2:
                latest = hist_data["Close"].iloc[-1]
                second_latest = hist_data["Close"].iloc[-2]
                pct_change = ((latest - second_latest) / second_latest) * 100
                temp.append(f"{pct_change:.2f}%")
            else:
                temp.append("0.00%")  # Fallback
        except Exception as err:
            temp.append("0.00%")  # Safe fallback

        return jsonify(temp), 201

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


@ app.route("/register",methods = ['POST'])
def register():
    print("register")
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        email = data['email']

        conn = sqlite3.connect("users.db")
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Users(Username, Password, Email) VALUES (?,?,?)",(username,password,email))
            conn.commit()
        finally:
            conn.close()

        return "registration successful", 201

    except sqlite3.IntegrityError:
        return "User already exists", 400
    except Exception as e: 
        print("Error during registration:", e)
        return "An error occurred", 500
    
@ app.route("/login",methods = ['POST'])
def login():
    print("login")
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        conn = sqlite3.connect("users.db")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (username, password))
            user = cursor.fetchone()
        finally:
            conn.close()

        if user:
            return jsonify({"status": "Login successful"}), 200
        else:
            return jsonify({"status": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"status": "An error occurred"}), 500

def search_ticker_suggestions(query, limit=8):
    """Return a list of {symbol, name, exchange} suggestions from Yahoo Finance for autocomplete."""
    if not query:
        return []
    query = query.strip()
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
    }
    params = {'q': query, 'quotesCount': limit, 'newsCount': 0}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = []
            for q in data.get("quotes", []):
                symbol = q.get("symbol")
                if not symbol:
                    continue
                results.append({
                    "symbol": symbol,
                    "name": q.get("shortname") or q.get("longname") or symbol,
                    "exchange": q.get("exchDisp") or q.get("exchange") or "",
                    "type": q.get("quoteType") or ""
                })
            return results
    except Exception as e:
        print("Suggestion search failed:", e)
    return []


def search_ticker_strict(company_name):
    """Like search_ticker but returns None when no real Yahoo Finance match is found,
    instead of falling back to upper-casing the raw input."""
    if not company_name:
        return None
    suggestions = search_ticker_suggestions(company_name, limit=1)
    if suggestions:
        return suggestions[0]["symbol"]
    return None


def search_ticker(company_name):
    if not company_name:
        return None
    
    company_name = company_name.strip()
    
    # 1. Primary lookup using Yahoo Finance's keyless search API
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
    }
    params = {'q': company_name, 'quotesCount': 5, 'newsCount': 0}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get("quotes", [])
            if quotes:
                symbol = quotes[0].get("symbol")
                if symbol:
                    return symbol
    except Exception as e:
        print("Yahoo Finance search failed:", e)

    # 2. Secondary fallback to FMP (if customized API Key is provided)
    API_KEY = os.environ.get("FMP_API_KEY", "cImJHzsIgHTcT9OrLdHazXt1u9tvPdJa")
    if API_KEY and API_KEY != "cImJHzsIgHTcT9OrLdHazXt1u9tvPdJa":
        fmp_url = "https://financialmodelingprep.com/api/v3/search"
        fmp_params = {
            "query": company_name,
            "limit": 5,
            "apikey": API_KEY
        }
        try:
            fmp_response = requests.get(fmp_url, params=fmp_params, timeout=5)
            if fmp_response.status_code == 200:
                fmp_data = fmp_response.json()
                if fmp_data and isinstance(fmp_data, list) and len(fmp_data) > 0:
                    symbol = fmp_data[0].get("symbol")
                    if symbol:
                        return symbol
        except Exception as e:
            print("FMP search failed:", e)

    # 3. Final fallback: treat company_name directly as the ticker symbol
    return company_name.upper()

def get_live_price(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Try live 1m data first
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return float(data["Close"].iloc[-1])
        
        # Fallback to recent daily closes (handles weekends/market-close)
        data = ticker.history(period="5d", interval="1d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
        
        # Final fallback to info fields
        info = ticker.info
        if info:
            val = info.get("currentPrice") or info.get("regularMarketPreviousClose") or info.get("previousClose")
            if val is not None:
                return float(val)
    except Exception as e:
        print(f"Error getting live price for {ticker_symbol}: {e}")
    return None

def get_column_data(df, col_name, ticker):
    if df.empty:
        return []
    if isinstance(df.columns, pd.MultiIndex):
        if (col_name, ticker) in df.columns:
            return df[(col_name, ticker)].tolist()
        for c in df.columns:
            if c[0] == col_name and c[1].upper() == ticker.upper():
                return df[c].tolist()
        # Fallback to first ticker in multi-index levels
        if len(df.columns.levels) > 1:
            level_tickers = df.columns.levels[1]
            if len(level_tickers) > 0:
                return df[(col_name, level_tickers[0])].tolist()
    else:
        if col_name in df.columns:
            return df[col_name].tolist()
    return []


# plotting our data
@app.route('/plot_live_price', methods=['POST'])
def plot_live_price():
    print("=== plot_live_price route called ===")

    try:
        data = request.get_json()
        print("Received JSON:", data, flush=True)

        stock_name = data.get('stock_name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        print(f"Parsed stock_name: {stock_name}, start_date: {start_date}, end_date: {end_date}", flush=True)

        ticker_symbols = search_ticker(stock_name)
        print("Resolved ticker symbol(s):", ticker_symbols, flush=True)

        data_stock = yf.download(ticker_symbols, start=start_date, end=end_date)
        print(f"Downloaded data shape: {data_stock.shape}", flush=True)

        if data_stock.empty:
            print("ERROR: No stock data returned by yfinance!", flush=True)
            return "No data found", 400

        fig = go.Figure()
        
        close_prices = get_column_data(data_stock, 'Close', ticker_symbols)
        volume_data = get_column_data(data_stock, 'Volume', ticker_symbols)

        # Area chart style for closing price
        fig.add_trace(go.Scatter(
            x=data_stock.index,
            y=close_prices,
            mode='lines',
            name="Closing Price",
            line=dict(width=3, color="#3a86ff", shape='spline', smoothing=1.3),
            fill='tozeroy',
            fillcolor='rgba(58, 134, 255, 0.12)',
            yaxis='y1'
        ))

        # Stylized volume bars
        fig.add_trace(go.Bar(
            x=data_stock.index,
            y=volume_data,
            name="Volume",
            marker=dict(
                color='rgba(6, 214, 160, 0.2)',
                line=dict(color='#06d6a0', width=1)
            ),
            yaxis='y2'
        ))

        print(f"close_prices length: {len(close_prices)}, volume_data length: {len(volume_data)}", flush=True)

        apply_premium_theme(fig, f'{ticker_symbols} - Price and Volume History', yaxis_title="Price", xaxis_title="Date")

        fig.update_layout(
            height=450,
            yaxis=dict(side='left'),
            yaxis2=dict(
                title=dict(text="Volume", font=dict(color="#9ca3af")),
                tickfont=dict(color="#9ca3af"),
                overlaying='y',
                side='right',
                showgrid=False,
                zeroline=False
            )
        )

        fig.write_html(os.path.join(CHARTS_DIR, "live_stock_prices.html"),
                       include_plotlyjs=True, full_html=True,
                       config={"responsive": True})
        return '', 204  # No Content

    except Exception as e:
        import traceback
        print("ERROR in plot_live_price route:", flush=True)
        traceback.print_exc()
        return "Internal Server Error", 500

def plot_profit_loss(username,export_png = False):
    print("plot_profit_loss",flush=True)
    conn = sqlite3.connect("stock.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Stocks WHERE Username=?", (username,))
        stocks = cursor.fetchall()
    finally:
        conn.close()

    # Batch-download all unique tickers in ONE yfinance call
    unique_tickers = list({stock[6] for stock in stocks})
    price_cache = {}
    if unique_tickers:
        try:
            batch = yf.download(unique_tickers, period="2d", interval="1d",
                                auto_adjust=True, progress=False)
            # yfinance returns MultiIndex columns; slice the 'Close' level
            try:
                close_df = batch["Close"]
            except KeyError:
                close_df = batch

            if not close_df.empty:
                # Forward-fill so a still-empty latest row (e.g. today's bar
                # before market data lands) doesn't blank out every ticker and
                # force the slow per-ticker get_live_price fallback below.
                last_row = close_df.ffill().iloc[-1]
                # last_row is a Series; index is ticker symbols
                for t in unique_tickers:
                    try:
                        if isinstance(last_row, pd.Series):
                            val = last_row.get(t)
                        else:
                            val = float(last_row)
                        if val is not None and not pd.isna(val):
                            price_cache[t] = float(val)
                    except Exception:
                        pass
        except Exception as e:
            print(f"Batch price fetch failed, falling back: {e}")
        # Fallback for any ticker still missing
        for t in unique_tickers:
            if t not in price_cache:
                p = get_live_price(t)
                if p:
                    price_cache[t] = p

    stock_dict = {}
    for stock in stocks:
        stock_name = stock[2]
        ticker_symbol = stock[6]
        live_price = price_cache.get(ticker_symbol)
        if live_price is not None:
            if stock_name not in stock_dict:
                stock_dict[stock_name] = 0
            stock_dict[stock_name] += (live_price - stock[4]) * stock[3]

    if not stock_dict:
        fig = go.Figure()
        apply_premium_theme(fig, "Profit / Loss Distribution", show_legend=False)
    else:
        colors = ['#06d6a0' if val >= 0 else '#ff006e' for val in stock_dict.values()]
        border_colors = ['#04a178' if val >= 0 else '#b3004d' for val in stock_dict.values()]
        
        fig = go.Figure(data=[go.Bar(
            x=list(stock_dict.keys()),
            y=list(stock_dict.values()),
            marker=dict(
                color=colors,
                line=dict(color=border_colors, width=1.5)
            )
        )])
        
        apply_premium_theme(fig, "Profit / Loss Distribution", yaxis_title="Gain/Loss (INR)", show_legend=False)
        
    fig.update_layout(
        width=700,
        height=400
    )

    fig.write_html(os.path.join(CHARTS_DIR, "profit_loss.html"),
                   include_plotlyjs=True, full_html=True, config={"responsive": True})

    if (export_png):
        fig.update_layout(paper_bgcolor='#0a0c10', plot_bgcolor='#0a0c10')
        fig.write_image(os.path.join(CHARTS_DIR, "profit_loss.png"))

def portfolio_value(username,start_date=None, end_date=None,export_png = False):
    print("portfolio_value",flush=True)
    conn = sqlite3.connect("stock.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Stocks WHERE username=?", (username,))
        stocks = cursor.fetchall()
    finally:
        conn.close()

    ticker_symbols = {}
    unique_stocks = {}

    for stock in stocks:
        if stock[2] not in unique_stocks:
            unique_stocks[stock[2]] = 0
        unique_stocks[stock[2]] += stock[3]
        if stock[6] not in ticker_symbols:
            ticker_symbols[stock[2]] = stock[6]

    tickers = list(ticker_symbols.values())
    if not tickers:
        fig = go.Figure()
        apply_premium_theme(fig, "Portfolio Net Value Trend", show_legend=False)
        fig.update_layout(width=700, height=400)
        fig.write_html(os.path.join(CHARTS_DIR, "portfolio_value.html"),
                       include_plotlyjs=True, full_html=True, config={"responsive": True})
        return

    data = yf.download(tickers, start=start_date, end=end_date)
    if data.empty:
        fig = go.Figure()
        apply_premium_theme(fig, "Portfolio Net Value Trend", show_legend=False)
        fig.update_layout(width=700, height=400)
        fig.write_html(os.path.join(CHARTS_DIR, "portfolio_value.html"),
                       include_plotlyjs=True, full_html=True, config={"responsive": True})
        return

    close_data = data['Close']
    total_value = {}

    for date, row in close_data.iterrows():
        for stock, qty in unique_stocks.items():
            ticker_symbol = ticker_symbols[stock]
            if ticker_symbol is not None:
                val = None
                if isinstance(close_data, pd.Series):
                    val = row
                elif ticker_symbol in row:
                    val = row[ticker_symbol]
                else:
                    for idx in row.index:
                        if str(idx).upper() == ticker_symbol.upper():
                            val = row[idx]
                            break
                if val is not None and not pd.isna(val):
                    if date not in total_value:
                        total_value[date] = 0
                    total_value[date] += float(val) * qty

    fig = go.Figure()
    if total_value:
        fig.add_trace(go.Scatter(
            x=list(total_value.keys()),
            y=list(total_value.values()),
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(width=3, color='#8338ec', shape='spline', smoothing=1.3),
            marker=dict(size=6, color='#8338ec', line=dict(color='#ffffff', width=1)),
            fill='tozeroy',
            fillcolor='rgba(131, 56, 236, 0.12)'
        ))
    
    apply_premium_theme(fig, "Portfolio Net Value Trend", yaxis_title="Total Value (INR)", xaxis_title="Date", show_legend=False)
    fig.update_layout(
        width=700,
        height=400
    )
    
    fig.write_html(os.path.join(CHARTS_DIR, "portfolio_value.html"))
    if export_png:
        fig.update_layout(paper_bgcolor='#0a0c10', plot_bgcolor='#0a0c10')
        fig.write_image(os.path.join(CHARTS_DIR, "portfolio_value.png"))

@app.route('/portfolio_value_today', methods=['POST'])
def portfolio_value_today():
    print("portfolio_value_today")
    try:
        data = request.get_json()
        username = data['username']

        conn = sqlite3.connect("stock.db")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Stocks WHERE username=?", (username,))
            stocks = cursor.fetchall()
        finally:
            conn.close()

        unique_stocks = {}
        ticker_symbols = {}

        total_value = 0

        for stock in stocks:
            if stock[2] not in unique_stocks:
                unique_stocks[stock[2]] = 0
            unique_stocks[stock[2]] += stock[3]
            ticker_symbols[stock[2]] = stock[6]  # ticker_symbol is now stored in the 6th column

        for stock in unique_stocks:
            ticker_symbol = ticker_symbols[stock]
            if ticker_symbol is not None:
                live_price = get_live_price(ticker_symbol)
                if live_price is not None:
                    total_value += live_price * unique_stocks[stock]
        
        return str(f"{total_value:.2f}"),200
    
    except Exception as e:
        return str(e), 500

@app.route('/profit_loss_value', methods=['POST'])
def profit_loss_value():
    print("profit_loss_value")
    try:
        data = request.get_json()
        username = data['username']

        conn = sqlite3.connect("stock.db")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Stocks WHERE username=?", (username,))
            stocks = cursor.fetchall()
        finally:
            conn.close()

        total = 0
        for stock in stocks:
            # stock_name = stock[2]
            ticker_symbol = stock[6]  # ticker_symbol is now stored in the 6th column
            live_price = get_live_price(ticker_symbol)
            if live_price is not None:
                total += (live_price - stock[4]) * stock[3]
        return str(f"{total:.2f}"), 200
    except Exception as e:
        return str(e), 500
    
@app.route('/investment_value', methods=['POST'])
def investment_value():
    print("investment_value")
    try:
        data = request.get_json()
        username = data['username']
        conn = sqlite3.connect("stock.db")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Stocks WHERE Username=?", (username,))
            stocks = cursor.fetchall()
        finally:
            conn.close()

        total_investment = 0
        for stock in stocks:
            total_investment += stock[3] * stock[4]  # Quantity * Price_per_share
        return str(f"{total_investment:.2f}"), 200
    
    except Exception as e:
        return str(e), 500

@app.route('/exchange_rate', methods=['POST'])
def exchange_rate():
    print("exchange_rate")
    try:
        API_KEY = os.environ.get("EXCHANGE_RATE_API_KEY", "7eacc4a1b04c26d0169384a9")
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/codes"
        response = requests.get(url)
        data = response.json()

        codes = []
        if data['result'] == 'success':
            code_map = {item[1]: item[0] for item in data['supported_codes']}
            # Sort by currency name (the keys)
            sorted_code_map = dict(sorted(code_map.items()))
            return jsonify(sorted_code_map), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/exchange_rate_value', methods=['POST'])
def exchange_rate_value():
    print("exchange_rate_value")
    try:
        data = request.get_json()
        base_currency = data['base_currency']
        target_currency = data['target_currency']

        API_KEY = os.environ.get("EXCHANGE_RATE_API_KEY", "7eacc4a1b04c26d0169384a9")
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{base_currency}/{target_currency}"
        response = requests.get(url)
        result = response.json()
        if result['result'] == 'success':
            return str(result['conversion_rate'])
        
    except Exception as e:
        return None

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    print("get_stock_data")
    try:
        data = request.get_json()
        username = data['username']
        conn = sqlite3.connect("stock.db")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Stocks WHERE Username=?", (username,))
            stocks = cursor.fetchall()
        finally:
            conn.close()

        final_stocks = []
        for stock in stocks:
            temp =[]
            temp.append(stock[2])
            temp.append(stock[3])
            temp.append(stock[4])
            temp.append(stock[5])
            ticker_symbol = stock[6]
            if ticker_symbol is not None:
                live_price = get_live_price(ticker_symbol)
                if live_price is not None:
                    temp.append(live_price)
                    temp.append((live_price - stock[4]) * stock[3])

            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period="2d", interval="1m")
            if not data.empty:
                latest_price = data["Close"].iloc[-1]
                second_latest_price = data["Close"].iloc[-2]
                percantage_change = "%"
                percantage_change += str((latest_price - second_latest_price) / second_latest_price * 100)

                temp.append(percantage_change)
            else:
                temp.append("0.00%")
            # Append StockID last so the frontend can use it for delete actions
            temp.append(stock[0])
            final_stocks.append(temp)

        return jsonify(final_stocks), 200
    except Exception as e:
        print("Error in get_stock_data:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/delete_stock', methods=['POST'])
def delete_stock():
    print("delete_stock")
    try:
        data = request.get_json()
        username = data['username']
        stock_id = int(data['stock_id'])

        conn = sqlite3.connect('stock.db')
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Stocks WHERE StockID=? AND Username=?", (stock_id, username))
            conn.commit()
            deleted = cursor.rowcount
        finally:
            conn.close()

        if deleted == 0:
            return jsonify({"error": "Position not found"}), 404
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        print("Error in delete_stock:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/search_tickers', methods=['POST'])
def search_tickers():
    """Autocomplete endpoint - returns up to 8 ticker suggestions for the given query."""
    try:
        data = request.get_json() or {}
        query = (data.get('query') or '').strip()
        if len(query) < 1:
            return jsonify([]), 200
        results = search_ticker_suggestions(query, limit=8)
        return jsonify(results), 200
    except Exception as e:
        print("Error in search_tickers:", e)
        return jsonify([]), 200

@app.route('/detailed_stock_data', methods=['POST'])
def detailed_stock_data():
    print("detailed_stock_data")
    try:
        data = request.get_json()
        stock_name = data['stock_name']
        ticker_symbol = search_ticker(stock_name)
        if not ticker_symbol:
            return jsonify({"error": "Ticker symbol resolution failed"}), 404
            
        ticker = yf.Ticker(ticker_symbol)
        info = {}
        try:
            info = ticker.info
        except Exception as info_err:
            print(f"Failed to fetch ticker.info for {ticker_symbol}: {info_err}")
            
        if not info:
            info = {}

        current_price = info.get("currentPrice")
        if current_price is None:
            try:
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current_price = hist["Close"].iloc[-1]
            except Exception as hist_err:
                print("Failed to fetch history fallback for price:", hist_err)
                
        if current_price is None:
            current_price = info.get("regularMarketPreviousClose") or info.get("previousClose") or 0.0

        current_price_str = f"{float(current_price):.2f}"

        stock_data = {
            "symbol": info.get("symbol") or ticker_symbol,
            "exchange": info.get("exchange") or "N/A",
            "name": info.get("longName") or info.get("shortName") or stock_name,
            "industry": info.get("industry") or "General Equity",
            "currentPrice": current_price_str,
            "previousClose": info.get("regularMarketPreviousClose") or info.get("previousClose") or float(current_price),
            "open": info.get("regularMarketOpen") or info.get("open") or float(current_price),
            "high": info.get("regularMarketDayHigh") or info.get("dayHigh") or float(current_price),
            "low": info.get("regularMarketDayLow") or info.get("dayLow") or float(current_price),
            "Pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
            "EPS": info.get("trailingEps") or info.get("forwardEps"),
            "52_week_high": info.get("fiftyTwoWeekHigh") or float(current_price),
            "52_week_low": info.get("fiftyTwoWeekLow") or float(current_price),
            "bookValue": info.get("bookValue"),
            "200avg": info.get("twoHundredDayAverage") or info.get("fiftyDayAverage")
        }
        return jsonify(stock_data), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/plot_all_graphs', methods=['POST'])
def plot_all_graphs():
    print("plot_all_graphs")
    data = request.get_json()
    username = data.get('username')
    stock_name = data.get('stock_name')
    mode = data.get("mode")
    ticker_symbol = search_ticker(stock_name)

    # Resolve the date range for the selected mode
    if mode == "daily":
        start_date = data.get('start_date')
        end_date = data.get('end_date')
    elif mode == "monthly":
        month = data.get('month')
        year = data.get('year')
        start_date = f"{year}-{month}-01"
        end_date = f"{year}-{month}-28"
    elif mode == "yearly":
        year = data.get('year')
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
    else:
        return jsonify({"error": f"Unknown mode '{mode}'"}), 400

    # The three plots are independent (separate DB connections, downloads and
    # output files), so run them concurrently instead of back-to-back to cut
    # wall-clock time roughly to that of the slowest single plot.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [
            pool.submit(candle_stick_graph, stock_name, ticker_symbol, start_date, end_date),
            pool.submit(plot_profit_loss, username),
            pool.submit(portfolio_value, username, start_date=start_date, end_date=end_date),
        ]
        for f in futures:
            f.result()  # re-raise any exception from the worker threads

    return '',204

def candle_stick_graph(stock_name,ticker_symbol, start_date, end_date):
    print("candle_stick_graph",flush=True)
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    
    open_vals = get_column_data(data, 'Open', ticker_symbol)
    high_vals = get_column_data(data, 'High', ticker_symbol)
    low_vals = get_column_data(data, 'Low', ticker_symbol)
    close_vals = get_column_data(data, 'Close', ticker_symbol)

    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=open_vals,
        high=high_vals,
        low=low_vals,
        close=close_vals,
        increasing_line_color='#06d6a0',
        decreasing_line_color='#ff006e',
        increasing_fillcolor='rgba(6, 214, 160, 0.2)',
        decreasing_fillcolor='rgba(255, 0, 110, 0.2)'
    )])
    
    apply_premium_theme(fig, f"Candlestick Chart - {stock_name}", yaxis_title="Price", xaxis_title="Date", show_legend=False)
    fig.update_layout(
        xaxis_rangeslider_visible=False  # Hide range slider to save space and look cleaner
    )

    # Write to image
    fig.write_html(os.path.join(CHARTS_DIR, "candlestick_chart.html"),
                   include_plotlyjs=True, full_html=True, config={"responsive": True})

@app.route('/predict', methods=['POST'])
def predict():
    print("predict")
    data = request.get_json()
    stock_name = data.get('stock_name')
    
    ticker_symbol = search_ticker(stock_name)
    string = final_prediction_code.data(ticker_symbol)

    return jsonify({"message1": string})

@app.route('/export',methods = ['POST'])
def export():
    print("export")
    data = request.get_json()
    username = data.get('username')

    conn = sqlite3.connect('stock.db')
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Stocks WHERE Username=?", (username,))
        stocks = cursor.fetchall()
    finally:
        conn.close()

    final_stocks = []
    for stock in stocks:
        temp =[]
        temp.append(stock[2])
        temp.append(stock[3])
        temp.append(stock[4])
        temp.append(stock[5])
        ticker_symbol = stock[6]
        if ticker_symbol is not None:
            live_price = get_live_price(ticker_symbol)
            if live_price is not None:
                temp.append(live_price)
                temp.append((live_price - stock[4]) * stock[3])
        
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="2d", interval="1m")
        if not data.empty:
            latest_price = data["Close"].iloc[-1]
            second_latest_price = data["Close"].iloc[-2]
            percantage_change = "%"
            percantage_change += str((latest_price - second_latest_price) / second_latest_price * 100)

            temp.append(percantage_change)
        else:
            temp.append("0.00%")
        final_stocks.append(temp)

    df = pd.DataFrame(final_stocks, columns=['stock_name','qty','bprice','bdate','cprice','p&l','%change'])
    plot_profit_loss(username, export_png=True)
    portfolio_value(username, start_date="2024-01-01", end_date=date.today(), export_png=True)

    # Write the Excel report into the shared analytics_charts/ output folder
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    filepath = os.path.join(ANALYTICS_DIR, "report.xlsx")
 

    with pd.ExcelWriter(filepath,engine="xlsxwriter") as writer:
        df.to_excel(writer,sheet_name="portfolio report",index=False)
        
        workbook = writer.book
        worksheet = writer.sheets["portfolio report"]
        worksheet.set_column('A:A', 15)  # stock_name
        worksheet.set_column('B:B', 8)   # qty
        worksheet.set_column('C:C', 10)  # bprice
        worksheet.set_column('D:D', 12)  # bdate
        worksheet.set_column('E:E', 10)  # cprice
        worksheet.set_column('F:F', 12)  # p&l
        worksheet.set_column('G:G', 15)  # %change


        # Insert images (ensure these files were saved earlier)
        worksheet.insert_image("J2", os.path.join(CHARTS_DIR, "profit_loss.png"))
        worksheet.insert_image("J30", os.path.join(CHARTS_DIR, "portfolio_value.png"))

    return send_file(filepath, as_attachment=True)

@app.route('/import_contract_notes', methods=['POST'])
def import_contract_notes():
    """
    Scan the contract notes folder for CCN PDFs and import BUY trades into the portfolio.
    Body: { username, clear_existing (bool, default false) }
    """
    try:
        data = request.get_json() or {}
        username = data.get('username')
        clear    = bool(data.get('clear_existing', False))

        if not username:
            return jsonify({"error": "username is required"}), 400

        set_watcher_username(username)

        # First pull any new contract-note PDFs straight from Gmail, then scan
        # the folder. Gmail problems (offline, auth) must not block a manual
        # import of files already on disk, so this is best-effort.
        gmail_note = None
        try:
            fetched = fetch_new_contract_notes()
            if fetched:
                gmail_note = f"fetched {len(fetched)} new contract note(s) from Gmail"
        except Exception as gmail_exc:
            gmail_note = f"Gmail fetch skipped: {gmail_exc}"
            print(f"[gmail] fetch during import failed: {gmail_exc}")

        results, total = scan_and_import_all(username, clear_existing=clear)
        if gmail_note:
            results.insert(0, gmail_note)

        return jsonify({"total_imported": total, "results": results}), 200

    except Exception as exc:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


@app.route('/import_status', methods=['POST'])
def import_status():
    """Return the list of already-processed contract note files."""
    try:
        return jsonify(get_processed_files()), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# Start the background file-watcher (imports new CCN files automatically) and
# the Gmail poller (downloads new contract notes from e-mail into that folder).
start_watcher()
start_gmail_watcher()


if __name__ == "__main__":
    app.run(debug = True)

