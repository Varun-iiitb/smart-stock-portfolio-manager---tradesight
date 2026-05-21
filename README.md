# 📊 TradeSight — Smart Stock Portfolio Manager

## 🧠 Overview

**TradeSight** is a desktop stock portfolio manager and research tool. Track your
holdings, analyze price history, research any listed company, and get
machine-learning price forecasts — all from a clean web-based interface that
runs locally on your own machine.

---

## 🚀 Features

- 🔐 **User accounts** — register and log in
- 💼 **Portfolio tracking** — add positions with live ticker validation, view
  real-time P&L, and remove positions from the holdings table
- 📊 **Dashboard** — total portfolio value, today's profit/loss, total
  investment, and a built-in universal currency converter
- 📈 **Analysis** — candlestick charts, profit/loss distribution, and portfolio
  value trends over daily / monthly / yearly periods
- 🔍 **Research** — detailed company financials (P/E, EPS, book value, 52-week
  range, day high/low) plus interactive price-and-volume charts
- 🤖 **ML prediction** — an XGBoost classifier predicts next-day price direction
  from technical indicators, and an ARIMA model forecasts the 30-day price trend
- 🔎 **Autocomplete** — type a company name anywhere and pick from a live
  Yahoo Finance dropdown
- 📤 **Excel report export** — generate a formatted `report.xlsx` with charts

---

## 🛠️ Tech Stack

| Layer            | Technology                              |
|------------------|------------------------------------------|
| **Frontend**     | HTML, CSS, JavaScript                    |
| **Backend**      | Python, Flask                            |
| **Server**       | Waitress                                 |
| **Charts**       | Plotly                                   |
| **ML / Forecast**| XGBoost, scikit-learn, statsmodels (ARIMA) |
| **Market data**  | yfinance, Yahoo Finance API              |
| **Database**     | SQLite                                   |

---

## 🖥️ How to Run

### ▶️ Quick start (desktop app)

Double-click the **Tradesight** icon on your desktop. The server starts in the
background and the app opens in its own window — no terminal needed.

### 🧑‍💻 Setup (first time / developer)

**Requirements:** Python 3.10+ and an internet connection.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python run_app.py
```

`run_app.py` launches the Waitress server and opens the app automatically.
To run the raw Flask development server instead, use `python app.py`.

### 📝 Notes

- ⚠️ Requires **internet access** — live market data, predictions, and exchange
  rates are all fetched online.
- Your accounts and portfolios are stored locally in `backend/users.db` and
  `backend/stock.db`; these files are **not** committed to the repository.
- Optional: create a `backend/.env` file with `FMP_API_KEY` and
  `EXCHANGE_RATE_API_KEY` to use your own API keys.
