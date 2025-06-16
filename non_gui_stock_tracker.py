import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import os
import sys

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

def fetch_stock_data(symbols):
    """Belirtilen hisse senetleri için son 10 günlük veriyi çeker"""
    stock_data = {}
    
    for symbol in symbols:
        try:
            # Son 10 günlük veriyi al
            end_date = datetime.now()
            start_date = end_date - timedelta(days=15)  # Hafta sonları için birkaç gün fazla al
            
            # Yahoo Finance'dan veri çek
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            # Veri kontrolü
            if data.empty or len(data) < 2:
                print(f"Hata: {symbol} için veri bulunamadı.")
                continue
                
            # Son 10 iş gününü al
            data = data.tail(10)
            
            # NaN değerleri temizle
            data = data.ffill().bfill()
            
            # Veriyi sakla
            stock_data[symbol] = data
            
            print(f"Veri alındı: {symbol}")
            
        except Exception as e:
            print(f"Veri çekme hatası ({symbol}): {str(e)}")
            continue
    
    return stock_data

def create_candlestick_charts(stock_data, output_dir="charts"):
    """Mum grafikleri oluşturur ve kaydeder"""
    # Çıktı dizinini oluştur
    os.makedirs(output_dir, exist_ok=True)
    
    # Piyasa durumunu kontrol et
    is_market_open = check_market_status()
    market_status = "Piyasa Açık - Canlı Veri" if is_market_open else "Piyasa Kapalı"
    print(f"Piyasa durumu: {market_status}")
    
    # Grafik boyutları (cm cinsinden)
    width_cm = 10
    height_cm = 20
    
    # cm'yi inç'e çevir (1 inç = 2.54 cm)
    width_inch = width_cm / 2.54
    height_inch = height_cm / 2.54
    
    # Her hisse için grafik oluştur
    charts_created = 0
    for symbol, data in stock_data.items():
        try:
            # Veri kontrolü - Ticker sütununu kaldır
            if 'Ticker' in data.columns:
                data = data.drop('Ticker', axis=1)
                
            # Grafik oluştur
            fig = Figure(figsize=(width_inch, height_inch))
            ax = fig.add_subplot(111)
            
            # Tarih indeksini formatlı göster
            date_labels = [d.strftime('%m/%d') for d in data.index]
            
            # X pozisyonları
            x = np.arange(len(data.index))
            
            # Her bir gün için mum çiz
            for i in range(len(data)):
                # Her bir günün verilerini al
                open_val = float(data['Open'].iloc[i])
                close_val = float(data['Close'].iloc[i])
                high_val = float(data['High'].iloc[i])
                low_val = float(data['Low'].iloc[i])
                
                # Yükselen mi düşen mi?
                is_up = close_val >= open_val
                color = 'green' if is_up else 'red'
                
                # Mum fitili (high-low)
                ax.plot([i, i], [low_val, high_val], color=color, linewidth=1)
                
                # Mum gövdesi (open-close)
                width_bar = 0.6
                if is_up:
                    height = close_val - open_val
                    bottom = open_val
                else:
                    height = open_val - close_val
                    bottom = close_val
                
                ax.bar(i, height, width_bar, bottom=bottom, color=color, alpha=0.7)
            
            # X ekseni etiketleri
            ax.set_xticks(x)
            ax.set_xticklabels(date_labels, rotation=45, fontsize=8)
            
            # Son fiyat bilgisi
            last_close = float(data['Close'].iloc[-1])
            last_open = float(data['Open'].iloc[-1])
            price_change = last_close - last_open
            price_change_pct = (price_change / last_open) * 100 if last_open != 0 else 0
            
            # Başlık
            title = f"{symbol} - Son: {last_close:.2f} ({price_change:+.2f}, {price_change_pct:+.2f}%)"
            ax.set_title(title, fontsize=10)
            
            # Canlı veri göstergesi
            if is_market_open:
                ax.text(0.95, 0.05, "Canlı Veri", transform=ax.transAxes, 
                        fontsize=8, color='blue', ha='right')
            
            # Izgara ve kenar boşluklarını ayarla
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            
            # Grafiği kaydet
            output_file = os.path.join(output_dir, f"{symbol}_chart.png")
            fig.savefig(output_file, dpi=100)
            plt.close(fig)
            
            print(f"Grafik oluşturuldu: {output_file}")
            charts_created += 1
            
        except Exception as e:
            print(f"Grafik oluşturma hatası ({symbol}): {str(e)}")
            continue
    
    print(f"\nToplam {charts_created} hisse için grafikler oluşturuldu.")
    print(f"Grafikler '{os.path.abspath(output_dir)}' dizininde kaydedildi.")

def main():
    # Örnek hisse kodları
    default_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    # Komut satırı argümanlarını kontrol et
    if len(sys.argv) > 1:
        symbols = [s.strip().upper() for s in sys.argv[1:]]
    else:
        symbols = default_symbols
        print(f"Hisse kodları belirtilmedi, varsayılan kodlar kullanılıyor: {', '.join(symbols)}")
    
    print(f"İşlenecek hisse kodları: {', '.join(symbols)}")
    
    # Verileri çek
    stock_data = fetch_stock_data(symbols)
    
    # Grafikleri oluştur
    if stock_data:
        create_candlestick_charts(stock_data)
    else:
        print("İşlenecek veri bulunamadı.")

if __name__ == "__main__":
    main()
