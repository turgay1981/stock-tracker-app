# ABD Borsası Hisse Takip Uygulaması - Kullanım Kılavuzu

Bu uygulama, ABD borsalarında işlem gören şirketlerin hisse senetlerini takip etmek için geliştirilmiştir. Uygulama, girilen hisse kodlarının son 10 günlük işlem grafiklerini mum (candlestick) formatında gösterir.

## Özellikler

- 70'e kadar hisse senedinin aynı anda takibi
- Son 10 günlük işlem verilerinin gösterimi
- Mum (candlestick) formatında grafikler
- Yükselen barlar yeşil, düşen barlar kırmızı renkte gösterim
- Borsa açıksa son günün canlı verilerle gösterimi
- Her grafik 10cm x 20cm boyutunda gösterim
- Kolay kullanımlı arayüz

## Kurulum

Uygulamayı çalıştırmak için aşağıdaki kütüphanelerin kurulu olması gerekmektedir:

```bash
pip install yfinance pandas matplotlib tkinter
```

## Kullanım

Uygulamanın iki farklı sürümü bulunmaktadır:

### 1. Grafiksel Arayüz (GUI) Sürümü

GUI sürümünü çalıştırmak için:

```bash
python stock_tracker_app.py
```

- Açılan pencerede, hisse kodlarını virgülle ayırarak giriş kutusuna yazın.
- "Grafikleri Oluştur" butonuna tıklayarak grafikleri oluşturun.
- Veriler yenilenmek istendiğinde "Verileri Yenile" butonunu kullanın.

### 2. Komut Satırı Sürümü

Komut satırı sürümünü çalıştırmak için:

```bash
python non_gui_stock_tracker.py HISSE1 HISSE2 HISSE3 ...
```

Örnek:
```bash
python non_gui_stock_tracker.py AAPL MSFT GOOGL AMZN TSLA
```

Hisse kodu belirtilmezse, varsayılan olarak AAPL, MSFT, GOOGL, AMZN ve TSLA hisseleri işlenir.
Oluşturulan grafikler "charts" klasöründe kaydedilir.

## Notlar

- Borsa saatleri dışında çalıştırıldığında "Piyasa Kapalı" olarak gösterilir.
- Borsa saatleri içinde çalıştırıldığında son gün "Canlı Veri" olarak işaretlenir.
- Veri alınamayan hisseler için hata mesajı gösterilir.
- Bazı günlerde veri eksikliği olabilir, bu durumda uygulama otomatik olarak veri temizliği yapar.

## Teknik Detaylar

- Veriler Yahoo Finance API üzerinden çekilmektedir.
- Grafikler matplotlib kütüphanesi kullanılarak oluşturulmaktadır.
- Arayüz tkinter kütüphanesi ile geliştirilmiştir.
- Uygulama, eksik verileri otomatik olarak doldurur (forward fill ve backward fill yöntemleriyle).

## Bilinen Sorunlar ve Çözümleri

- Pandas kütüphanesinin gelecek sürümlerinde bazı uyarılar görülebilir, bunlar işlevselliği etkilemez.
- Bazı hisse senetleri için veri alınamayabilir, bu durumda farklı bir hisse kodu deneyin.
