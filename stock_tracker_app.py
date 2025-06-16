import tkinter as tk
from tkinter import scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import mplfinance as mpf
import time
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

class StockTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ABD Borsası Hisse Takip Uygulaması")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Ana çerçeve
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Giriş alanı çerçevesi
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=10)
        
        # Hisse kodu giriş alanı
        tk.Label(self.input_frame, text="Hisse Kodları (virgülle ayırın):").pack(side=tk.LEFT, padx=5)
        self.symbols_entry = scrolledtext.ScrolledText(self.input_frame, height=5, width=50)
        self.symbols_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Örnek hisse kodları
        default_symbols = "AAPL, MSFT, GOOGL, AMZN, TSLA"
        self.symbols_entry.insert(tk.END, default_symbols)
        
        # Butonlar çerçevesi
        self.button_frame = tk.Frame(self.input_frame)
        self.button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Çalıştır butonu
        self.run_button = tk.Button(self.button_frame, text="Grafikleri Oluştur", command=self.generate_charts)
        self.run_button.pack(side=tk.TOP, pady=2)
        
        # Yenile butonu
        self.refresh_button = tk.Button(self.button_frame, text="Verileri Yenile", command=self.refresh_data)
        self.refresh_button.pack(side=tk.TOP, pady=2)
        self.refresh_button.config(state=tk.DISABLED)  # Başlangıçta devre dışı
        
        # Durum çubuğu
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Grafik gösterim alanı
        self.chart_frame = tk.Frame(self.main_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Kaydırma çerçevesi
        self.canvas_container = tk.Canvas(self.chart_frame)
        self.scrollbar = tk.Scrollbar(self.chart_frame, orient="vertical", command=self.canvas_container.yview)
        self.scrollable_frame = tk.Frame(self.canvas_container)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_container.configure(
                scrollregion=self.canvas_container.bbox("all")
            )
        )
        
        self.canvas_container.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_container.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas_container.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Veri ve grafik değişkenleri
        self.stock_data = {}
        self.current_symbols = []
        self.is_market_open = False
        self.last_update_time = None
        
    def check_market_status(self):
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
        
    def generate_charts(self):
        # Önceki grafikleri temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Hisse kodlarını al
        symbols_text = self.symbols_entry.get("1.0", tk.END).strip()
        if not symbols_text:
            messagebox.showerror("Hata", "Lütfen en az bir hisse kodu girin.")
            return
            
        symbols = [s.strip().upper() for s in symbols_text.split(",")]
        
        # Çok fazla hisse kodu kontrolü
        if len(symbols) > 70:
            messagebox.showwarning("Uyarı", "En fazla 70 hisse kodu girebilirsiniz. İlk 70 kod işlenecek.")
            symbols = symbols[:70]
        
        self.current_symbols = symbols
        
        # Durum çubuğunu güncelle
        self.status_var.set(f"Veriler alınıyor... Lütfen bekleyin.")
        self.root.update()
        
        # Yenile butonunu aktifleştir
        self.refresh_button.config(state=tk.NORMAL)
        
        # Grafikleri ayrı bir thread'de oluştur
        threading.Thread(target=self._fetch_and_create_charts, args=(symbols,), daemon=True).start()
        
    def refresh_data(self):
        """Mevcut grafikleri güncel verilerle yeniler"""
        if not self.current_symbols:
            messagebox.showinfo("Bilgi", "Yenilenecek grafik bulunamadı.")
            return
            
        self.status_var.set(f"Veriler yenileniyor... Lütfen bekleyin.")
        self.root.update()
        
        # Grafikleri ayrı bir thread'de yenile
        threading.Thread(target=self._fetch_and_create_charts, args=(self.current_symbols, True), daemon=True).start()
        
    def _fetch_and_create_charts(self, symbols, is_refresh=False):
        """Verileri çeker ve grafikleri oluşturur"""
        # Piyasa durumunu kontrol et
        self.is_market_open = self.check_market_status()
        
        # Tüm hisseler için veri çek
        for i, symbol in enumerate(symbols):
            try:
                # Son 10 günlük veriyi al
                end_date = datetime.now()
                start_date = end_date - timedelta(days=15)  # Hafta sonları için birkaç gün fazla al
                
                # Yahoo Finance'dan veri çek
                data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                
                # Veri kontrolü
                if data.empty or len(data) < 2:
                    self.status_var.set(f"Hata: {symbol} için veri bulunamadı.")
                    continue
                    
                # Son 10 iş gününü al
                data = data.tail(10)
                
                # Veriyi sakla
                self.stock_data[symbol] = data
                
                # Durum çubuğunu güncelle
                self.status_var.set(f"{i+1}/{len(symbols)} hisse verisi alındı: {symbol}")
                self.root.update()
                
            except Exception as e:
                print(f"Veri çekme hatası ({symbol}): {str(e)}")
                continue
        
        # Son güncelleme zamanını kaydet
        self.last_update_time = datetime.now()
        
        # Grafikleri oluştur
        self._create_charts(symbols)
        
    def _create_charts(self, symbols):
        """Çekilen verilerle grafikleri oluşturur"""
        # Grafik boyutları (cm cinsinden)
        width_cm = 10
        height_cm = 20
        
        # cm'yi inç'e çevir (1 inç = 2.54 cm)
        width_inch = width_cm / 2.54
        height_inch = height_cm / 2.54
        
        # Her hisse için ayrı bir grafik oluştur
        for i, symbol in enumerate(symbols):
            if symbol not in self.stock_data:
                continue
                
            data = self.stock_data[symbol]
            
            # Grafik çerçevesi
            chart_frame = tk.Frame(self.scrollable_frame, borderwidth=1, relief=tk.RAISED)
            chart_frame.grid(row=i//5, column=i%5, padx=5, pady=5, sticky="nsew")
            
            # Grafik başlığı
            title_frame = tk.Frame(chart_frame)
            title_frame.pack(fill=tk.X)
            
            # Hisse adı ve son fiyat
            last_close = data['Close'].iloc[-1]
            last_open = data['Open'].iloc[-1]
            price_change = last_close - last_open
            price_change_pct = (price_change / last_open) * 100 if last_open != 0 else 0
            
            # Fiyat değişimi rengi
            price_color = "green" if price_change >= 0 else "red"
            
            title_label = tk.Label(title_frame, text=f"{symbol}", font=("Arial", 10, "bold"))
            title_label.pack(side=tk.LEFT, padx=2)
            
            price_label = tk.Label(title_frame, 
                                  text=f"{last_close:.2f} ({price_change:+.2f}, {price_change_pct:+.2f}%)", 
                                  fg=price_color)
            price_label.pack(side=tk.RIGHT, padx=2)
            
            # Mum grafiği için figür oluştur
            fig = Figure(figsize=(width_inch, height_inch), dpi=100)
            ax = fig.add_subplot(111)
            
            # Mum grafiği için veri hazırla
            ohlc = data[['Open', 'High', 'Low', 'Close']]
            
            # Tarih indeksini formatlı göster
            date_labels = [d.strftime('%m/%d') for d in ohlc.index]
            
            # Yükselen ve düşen günleri belirle
            up = data[data.Close >= data.Open]
            down = data[data.Close < data.Open]
            
            # X pozisyonları
            x = np.arange(len(ohlc.index))
            
            # Mum fitilleri (high-low)
            ax.vlines(x[up.index.isin(ohlc.index)], up.Low, up.High, color='green', linewidth=1)
            ax.vlines(x[down.index.isin(ohlc.index)], down.Low, down.High, color='red', linewidth=1)
            
            # Mum gövdeleri (open-close)
            width = 0.6
            ax.bar(x[up.index.isin(ohlc.index)], up.Close-up.Open, width, bottom=up.Open, color='green', alpha=0.7)
            ax.bar(x[down.index.isin(ohlc.index)], down.Close-down.Open, width, bottom=down.Open, color='red', alpha=0.7)
            
            # X ekseni etiketleri
            ax.set_xticks(x)
            ax.set_xticklabels(date_labels, rotation=45, fontsize=8)
            
            # Izgara ve kenar boşluklarını ayarla
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            
            # Canlı veri göstergesi
            if self.is_market_open:
                ax.set_title("Canlı Veri", fontsize=8, loc='right', color='blue')
            
            # Tkinter canvas'a grafikleri yerleştir
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Durum çubuğunu güncelle
            self.status_var.set(f"{i+1}/{len(symbols)} grafik oluşturuldu: {symbol}")
            self.root.update()
        
        # Tüm satırların ve sütunların eşit ağırlıkta olmasını sağla
        rows = (len(symbols) + 4) // 5  # Yukarı yuvarlama
        for r in range(rows):
            self.scrollable_frame.grid_rowconfigure(r, weight=1)
        for c in range(5):
            self.scrollable_frame.grid_columnconfigure(c, weight=1)
            
        # Son güncelleme bilgisini göster
        update_time = self.last_update_time.strftime("%H:%M:%S") if self.last_update_time else ""
        market_status = "Piyasa Açık - Canlı Veri" if self.is_market_open else "Piyasa Kapalı"
        self.status_var.set(f"Tamamlandı: {len(symbols)} hisse için grafikler oluşturuldu. Son güncelleme: {update_time} - {market_status}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockTrackerApp(root)
    root.mainloop()
