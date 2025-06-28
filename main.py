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

@app.route('/get_multiple_stocks_data', methods=['POST'])
def get_multiple_stocks_data():
    symbols = request.form.get('symbols', '')
    
    if not symbols:
        return jsonify({'error': 'Hisse kodları belirtilmedi.'}), 400

    # Hisse kodlarını ayır ve temizle
    symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
    
    if not symbol_list:
        return jsonify({'error': 'Geçerli hisse kodu bulunamadı.'}), 400
    
    if len(symbol_list) > 70:
        return jsonify({'error': 'En fazla 70 hisse kodu girebilirsiniz.'}), 400

    results = []
    
    for symbol in symbol_list:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="10d")
            info = stock.info

            if hist.empty:
                results.append({
                    'symbol': symbol,
                    'error': f'{symbol} için veri bulunamadı.'
                })
                continue

            # Veriyi hazırla
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })

            # Son fiyat ve değişim bilgileri
            last_close = float(hist['Close'].iloc[-1])
            prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else last_close
            price_change = last_close - prev_close
            price_change_pct = (price_change / prev_close) * 100 if prev_close != 0 else 0

            # Piyasa durumu
            market_status = "Piyasa Kapalı"
            try:
                if 'marketState' in info:
                    if info['marketState'] == 'REGULAR':
                        market_status = "Piyasa Açık"
                    elif info['marketState'] == 'PRE':
                        market_status = "Piyasa Öncesi"
                    elif info['marketState'] == 'POST':
                        market_status = "Piyasa Sonrası"
            except:
                pass

            results.append({
                'symbol': symbol,
                'data': data,
                'last_price': last_close,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'market_status': market_status
            })

        except Exception as e:
            results.append({
                'symbol': symbol,
                'error': f'{symbol} için hata: {str(e)}'
            })

    return jsonify({
        'success': True,
        'results': results
    })

@app.route('/save_stocks', methods=['POST'])
def save_stocks_form():
    page_number = request.form.get('page_number')
    symbols = request.form.get('symbols', '')
    
    if not page_number:
        return jsonify({'error': 'Sayfa numarası belirtilmedi.'}), 400
    
    # Hisse kodlarını ayır ve temizle
    symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
    
    if len(symbol_list) > 70:
        return jsonify({'error': 'En fazla 70 hisse kodu girebilirsiniz.'}), 400
    
    # Verileri kaydet
    stock_data = load_stock_data()
    stock_data[str(page_number)] = symbol_list
    save_stock_data(stock_data)
    
    return jsonify({
        'success': True,
        'stocks': symbol_list
    })

if __name__ == '__main__':
    # Ensure stock_data.json exists on first run
    if not os.path.exists(STOCK_DATA_FILE):
        save_stock_data({str(i): [] for i in range(1, 31)})
    
    # Create static directory if it doesn't exist
    os.makedirs(os.path.join(app.root_path, 'static'), exist_ok=True)

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)


