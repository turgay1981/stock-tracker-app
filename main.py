import sys
import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

app = Flask(__name__)

# JSON dosya yolu
STOCK_DATA_FILE = 'stock_data.json'

def load_stock_data():
    """JSON dosyasından hisse verilerini yükle"""
    try:
        with open(STOCK_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Dosya yoksa boş veri yapısı oluştur
        default_data = {str(i): [] for i in range(1, 31)}
        save_stock_data(default_data)
        return default_data
    except json.JSONDecodeError:
        # JSON bozuksa varsayılan veri yapısını döndür
        return {str(i): [] for i in range(1, 31)}

def save_stock_data(data):
    """Hisse verilerini JSON dosyasına kaydet"""
    try:
        with open(STOCK_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Veri kaydetme hatası: {str(e)}")
        return False

def check_market_status():
    """Piyasanın açık olup olmadığını kontrol eder"""
    now = datetime.now()
    # ABD Doğu saati (EST) - UTC-5 veya UTC-4 (yaz saati)
    # Basit bir kontrol: Pazartesi-Cuma ve 9:30-16:00 EST arası
    weekday = now.weekday()
    hour = now.hour
    
    # Hafta içi mi?
    if 0 <= weekday <= 4:
        # Saat kontrolü (basitleştirilmiş)
        # Gerçek uygulamada tatil günleri ve saat dilimi dönüşümleri eklenmelidir
        if 14 <= hour <= 21:  # UTC saatinde yaklaşık 9:30-16:00 EST
            return True
    
    return False

def fetch_stock_data(symbol):
    """Belirtilen hisse senedi için son 10 günlük veriyi çeker (saf HTTP API ile)"""
    try:
        # Son 10 günlük veriyi al
        end_date = datetime.now()
        start_date = end_date - timedelta(days=15)  # Hafta sonları için birkaç gün fazla al
        
        # Unix timestamp formatına dönüştür
        period1 = int(start_date.timestamp())
        period2 = int(end_date.timestamp())
        
        # Yahoo Finance API URL'si
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        
        # API parametreleri
        params = {
            "period1": period1,
            "period2": period2,
            "interval": "1d",
            "includePrePost": "false",
            "events": "div,split,earn"
        }
        
        # API isteği gönder
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, params=params, headers=headers)
        
        # Yanıtı kontrol et
        if response.status_code != 200:
            print(f"API hatası: {response.status_code}")
            return None
        
        # JSON yanıtını parse et
        data = response.json()
        
        # Veri kontrolü
        if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
            print(f"Veri formatı hatası: {symbol}")
            return None
        
        # Veriyi çıkar
        result = data["chart"]["result"][0]
        
        if "timestamp" not in result or not result["timestamp"]:
            print(f"Zaman damgası bulunamadı: {symbol}")
            return None
        
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
        
        # OHLC verilerini çıkar
        opens = quote.get("open", [])
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        closes = quote.get("close", [])
        volumes = quote.get("volume", [])
        
        # Veri uzunluklarını kontrol et
        if not opens or not highs or not lows or not closes:
            print(f"OHLC verileri eksik: {symbol}")
            return None
        
        # Son 10 günlük veriyi al
        data_points = []
        for i in range(len(timestamps)):
            # None değerleri atla
            if opens[i] is None or highs[i] is None or lows[i] is None or closes[i] is None:
                continue
                
            data_points.append({
                "date": datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                "open": opens[i],
                "high": highs[i],
                "low": lows[i],
                "close": closes[i],
                "volume": volumes[i] if i < len(volumes) and volumes[i] is not None else 0
            })
        
        # Son 10 günü al
        data_points = data_points[-10:] if len(data_points) > 10 else data_points
        
        # Veri kontrolü
        if not data_points:
            print(f"Veri noktası bulunamadı: {symbol}")
            return None
            
        return data_points
        
    except Exception as e:
        print(f"Veri çekme hatası ({symbol}): {str(e)}")
        return None

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/page/<int:page_number>')
def stock_page(page_number):
    """Belirli bir sayfa numarası için hisse takip sayfası"""
    # Sayfa numarası kontrolü
    if page_number < 1 or page_number > 30:
        return "Geçersiz sayfa numarası. 1-30 arası bir sayfa seçin.", 404
    
    # Kayıtlı hisse kodlarını yükle
    stock_data = load_stock_data()
    saved_stocks = stock_data.get(str(page_number), [])
    
    return render_template('stock_page.html', 
                         page_number=page_number, 
                         saved_stocks=saved_stocks)

@app.route('/save_stocks', methods=['POST'])
def save_stocks():
    """Hisse kodlarını kaydet"""
    try:
        page_number = request.form.get('page_number', '').strip()
        symbols_text = request.form.get('symbols', '').strip()
        
        # Sayfa numarası kontrolü
        if not page_number or not page_number.isdigit():
            return jsonify({'error': 'Geçersiz sayfa numarası.'})
        
        page_number = int(page_number)
        if page_number < 1 or page_number > 30:
            return jsonify({'error': 'Sayfa numarası 1-30 arasında olmalıdır.'})
        
        # Hisse kodlarını işle
        if symbols_text:
            symbols = [s.strip().upper() for s in symbols_text.split(',') if s.strip()]
            # Çok fazla hisse kodu kontrolü
            if len(symbols) > 70:
                return jsonify({'error': 'En fazla 70 hisse kodu girebilirsiniz.'})
        else:
            symbols = []
        
        # Mevcut veriyi yükle
        stock_data = load_stock_data()
        
        # Bu sayfa için hisse kodlarını güncelle
        stock_data[str(page_number)] = symbols
        
        # Veriyi kaydet
        if save_stock_data(stock_data):
            return jsonify({
                'success': True,
                'message': 'Hisse kodları başarıyla kaydedildi.',
                'stocks': symbols
            })
        else:
            return jsonify({'error': 'Kaydetme işlemi başarısız oldu.'})
            
    except Exception as e:
        return jsonify({'error': f'Bir hata oluştu: {str(e)}'})

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    """Hisse senedi verisini JSON formatında döndür"""
    symbol = request.form.get('symbol', '').strip().upper()
    
    if not symbol:
        return jsonify({'error': 'Lütfen bir hisse kodu girin.'})
    
    # Veriyi çek
    data = fetch_stock_data(symbol)
    
    if data is None:
        return jsonify({'error': f'{symbol} için veri bulunamadı.'})
    
    # Piyasa durumunu kontrol et
    is_market_open = check_market_status()
    market_status = "Piyasa Açık - Canlı Veri" if is_market_open else "Piyasa Kapalı"
    
    # Son fiyat bilgilerini hesapla
    last_price = data[-1]['close']
    price_change = last_price - data[-1]['open']
    price_change_pct = (price_change / data[-1]['open']) * 100 if data[-1]['open'] != 0 else 0
    
    return jsonify({
        'success': True,
        'data': data,
        'symbol': symbol,
        'market_status': market_status,
        'last_price': last_price,
        'price_change': price_change,
        'price_change_pct': price_change_pct
    })

@app.route('/get_multiple_stocks_data', methods=['POST'])
def get_multiple_stocks_data():
    """Birden fazla hisse senedi verisini JSON formatında döndür"""
    symbols_text = request.form.get('symbols', '').strip()
    
    if not symbols_text:
        return jsonify({'error': 'Lütfen en az bir hisse kodu girin.'})
    
    symbols = [s.strip().upper() for s in symbols_text.split(',')]
    
    # Çok fazla hisse kodu kontrolü
    if len(symbols) > 70:
        return jsonify({'error': 'En fazla 70 hisse kodu girebilirsiniz.'})
    
    results = []
    
    for symbol in symbols:
        # Veriyi çek
        data = fetch_stock_data(symbol)
        
        if data is None:
            results.append({
                'symbol': symbol,
                'error': f'{symbol} için veri bulunamadı.'
            })
            continue
        
        # Piyasa durumunu kontrol et
        is_market_open = check_market_status()
        market_status = "Piyasa Açık - Canlı Veri" if is_market_open else "Piyasa Kapalı"
        
        # Son fiyat bilgilerini hesapla
        last_price = data[-1]['close']
        price_change = last_price - data[-1]['open']
        price_change_pct = (price_change / data[-1]['open']) * 100 if data[-1]['open'] != 0 else 0
        
        results.append({
            'symbol': symbol,
            'data': data,
            'market_status': market_status,
            'last_price': last_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct
        })
    
    return jsonify({
        'success': True,
        'results': results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

