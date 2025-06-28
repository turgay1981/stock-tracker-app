import sys
import os
import json
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# JSON dosyasının yolu
STOCK_DATA_FILE = 'stock_data.json'

def load_stock_data():
    if os.path.exists(STOCK_DATA_FILE):
        with open(STOCK_DATA_FILE, 'r') as f:
            return json.load(f)
    return {str(i): [] for i in range(1, 31)}

def save_stock_data(data):
    with open(STOCK_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page/<int:page_id>')
def stock_page(page_id):
    stock_data = load_stock_data()
    stocks = stock_data.get(str(page_id), [])
    return render_template('stock_page.html', page_id=page_id, stocks=','.join(stocks))

@app.route('/save_stocks/<int:page_id>', methods=['POST'])
def save_stocks(page_id):
    data = request.get_json()
    stocks_str = data.get('stocks', '')
    stocks = [s.strip().upper() for s in stocks_str.split(',') if s.strip()]
    
    stock_data = load_stock_data()
    stock_data[str(page_id)] = stocks
    save_stock_data(stock_data)
    
    return jsonify({'status': 'success'})

@app.route('/get_chart_data', methods=['POST'])
def get_chart_data():
    data = request.get_json()
    ticker = data.get('ticker')
    
    if not ticker:
        return jsonify({'error': 'Hisse kodu belirtilmedi.'}), 400

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="10d")

        if hist.empty:
            return jsonify({'error': f'{ticker} için veri bulunamadı.'}), 404

        # Grafik oluşturma
        filename = f'{ticker}_chart.png'
        filepath = os.path.join(app.root_path, 'static', filename)
        
        # Ensure static directory exists
        os.makedirs(os.path.join(app.root_path, 'static'), exist_ok=True)

        mc = mpf.make_marketcolors(up='#00ff00', down='#ff0000', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)
        
        mpf.plot(hist, type='candle', style=s, savefig=filepath, figscale=1.5)

        return jsonify({'chart_url': f'/static/{filename}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure stock_data.json exists on first run
    if not os.path.exists(STOCK_DATA_FILE):
        save_stock_data({str(i): [] for i in range(1, 31)})
    
    # Create static directory if it doesn't exist
    os.makedirs(os.path.join(app.root_path, 'static'), exist_ok=True)

    app.run(host='127.0.0.1', port=5000, debug=True)


