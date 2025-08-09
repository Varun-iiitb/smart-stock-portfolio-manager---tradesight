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
- 🔮 **Price prediction** using Facebook Prophet model  
- 🧠 Backend-driven **data analysis**  
- 📤 **Excel report export** feature  

---

## 🛠️ Tech Stack

| Layer        | Technology                  |
|--------------|------------------------------|
| **Frontend** | Java, JavaFX                 |
| **Backend**  | Python (Flask)               |
| **Charts**   | Plotly                       |
| **Prediction**| Prophet                     |

---

## 🖥️ How to Run the Application

### ✅ End Users

1. Download both the **backend** and **frontend** (TradeSight) folders.  
2. Place them together inside a single directory.  


**Start the Frontend (JavaFX)**  
Open the `tradesight` frontend folder in **IntelliJ IDEA**, **Eclipse**, or any Java IDE that supports JavaFX, and run the main application class `Login_Page.java`.

3. Enter a valid stock symbol (e.g., `AAPL`, `TSLA`, `INFY.NS`).  
4. Click **Submit** to fetch charts and predictions.  
5. Click **Export** to generate a report in `report.xlsx`.  

> ⚠️ The **backend must be running before launching the frontend**.  
> ⚠️ Requires **internet access** to fetch stock data and generate predictions.

---

### 🧑‍💻 Developer Setup 

#### 🔧 Requirements

- JDK 17+  
- Python 3.10+  
- JavaFX SDK 17 or 21+  
- pip: Flask, Prophet, Plotly, pandas, numpy, yfinance, requests, openpyxl  

#### ⚙️ Run Backend (Python)

```bash
cd backend
pip install -r requirements.txt
python app.py
```
