# 📊 Smart Stock Portfolio Manager - TradeSight

## 🧠 Overview

**TradeSight** is a smart stock portfolio management and research desktop application built to help users:

- 📈 Monitor live stock performance
- 📉 Analyze technical indicators like MACD, RSI, EMA
- 🤖 Generate machine learning-based price predictions
- 🧾 Export professional Excel-based stock reports

The app uses a **JavaFX GUI frontend** and a **Python backend** for powerful financial analysis and data visualization.

---

## 🚀 Features

- 🔍 **Searchable stock interface** with autocomplete
- 📊 **Real-time chart display** (via Plotly)
- 📉 **Technical metric visualizations** (MACD, RSI, EMA)
- 🔮 **Price prediction** using Prophet + scikit-learn
- 🧠 Backend-driven **data analysis**
- 📤 **Excel report export** feature
- 🖥️ Fully packaged as a `.exe` desktop application

---

## 🛠️ Tech Stack

| Layer        | Technology                  |
|--------------|------------------------------|
| **Frontend** | Java, JavaFX                 |
| **Backend**  | Python (Flask)               |
| **Charts**   | Plotly, Matplotlib           |
| **Prediction**| Prophet, scikit-learn        |
| **Packaging**| launch4j (JavaFX → .exe)     |

---

## 🖥️ How to Run the Application

### ✅ End Users (EXE File)

1. Download both the backend and frontend (TradeSight) folders, place them together inside a single directory, and then double-click the .exe file located inside the frontend folder to launch the app.

2. Enter a valid stock symbol (e.g., `AAPL`, `TSLA`, `INFY.NS`).
3. Click **Submit** to fetch charts and predictions.
4. Click **Export** to generate a report in `report.xlsx`.

> ⚠️ Requires **internet access** to fetch stock data and generate predictions.

---

### 🧑‍💻 Developer Setup 

If you want to build or modify the app locally:

#### 🔧 Requirements

- JDK 17+
- Python 3.10+
- JavaFX SDK 17 or 21+
- pip: Flask, Prophet, Plotly, pandas, numpy, yfinance,   requests, openpyxl.

#### ⚙️ Run Backend (Python)

```bash
cd backend
pip install -r requirements.txt
python app.py
