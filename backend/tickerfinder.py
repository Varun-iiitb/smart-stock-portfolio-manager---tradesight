import sqlite3
import requests
def search_ticker(company_name):
    API_KEY = "cImJHzsIgHTcT9OrLdHazXt1u9tvPdJa"
    url = "https://financialmodelingprep.com/api/v3/search"
    params = {
        "query": company_name,
        "limit": 10,
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    
    try:
        data = response.json()
    except Exception as e:
        print("Failed to parse JSON:", e)
        return None

    if not data:
        print("No results found for", company_name)
        return None
    
    return data[0].get("symbol")  # return the top match

# print(search_ticker("INFOSYS"))

conn = sqlite3.connect('stock.db')
cursor = conn.cursor()
cursor.execute('''DELETE FROM Stocks WHERE Username = 'v' AND (StockName = "INFOSYS")''') 
conn.commit()
