# ABD Borsası Hisse Takip Uygulaması

Bu proje, Python ve Flask kullanılarak geliştirilmiş bir ABD Borsası hisse takip uygulamasıdır. Uygulama, hisse senedi verilerini çeker, mum grafikleri oluşturur ve kullanıcıların belirli kategoriler altında hisse senedi listelerini kaydetmelerine olanak tanır.

## Özellikler

-   1'den 30'a kadar özelleştirilebilir hisse senedi kategorileri.
-   Her kategori için hisse senedi kodlarını kaydetme ve yükleme.
-   YFinance kütüphanesi ile güncel hisse senedi verilerini çekme.
-   Matplotlib ve MPLFinance ile mum grafikleri oluşturma.
-   Web tabanlı arayüz (Flask).

## Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

### 1. Python Kurulumu

Bilgisayarınızda Python 3.x kurulu olduğundan emin olun. Python'ı [resmi web sitesinden](https://www.python.org/downloads/) indirebilirsiniz.

Kurulumu doğrulamak için komut istemcisini (Command Prompt / Terminal) açın ve aşağıdaki komutu çalıştırın:

```bash
python --version
# veya
python3 --version
```

### 2. Proje Dosyalarını İndirme

Bu projenin tüm dosyalarını içeren `.zip` veya `.tar.gz` dosyasını indirin ve istediğiniz bir konuma çıkarın.

### 3. Sanal Ortam Oluşturma (Önerilen)

Proje bağımlılıklarını izole etmek için bir sanal ortam oluşturmanız önerilir. Proje klasörüne gidin ve aşağıdaki komutları çalıştırın:

```bash
cd /path/to/your/project
python -m venv venv
```

Sanal ortamı etkinleştirin:

-   **Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
-   **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 4. Bağımlılıkları Yükleme

Etkinleştirdiğiniz sanal ortamda, projenin gerektirdiği kütüphaneleri yüklemek için `requirements.txt` dosyasını kullanın:

```bash
pip install -r requirements.txt
```

### 5. Uygulamayı Çalıştırma

Tüm bağımlılıklar yüklendikten sonra, uygulamayı başlatmak için aşağıdaki komutu çalıştırın:

```bash
python main.py
```

Uygulama başlatıldığında, komut istemcisinde `http://127.0.0.1:5000/` gibi bir adres göreceksiniz. Bu adresi web tarayıcınızda açarak uygulamaya erişebilirsiniz.

### 6. Kullanım

-   Ana sayfada 1'den 30'a kadar butonlar bulunur. Her buton bir hisse senedi kategorisini temsil eder.
-   Bir kategoriye tıklayarak o kategoriye özel hisse senedi giriş sayfasına gidin.
-   Hisse senedi kodlarını (örneğin `AAPL, MSFT, GOOGL`) virgülle ayırarak girin.
-   `Kaydet` butonuna tıklayarak hisse senedi kodlarınızı kaydedin. Bu veriler `stock_data.json` dosyasında saklanır.
-   `Grafikleri Oluştur` butonuna tıklayarak girilen hisse senetlerinin son 10 günlük mum grafiklerini görüntüleyin.
-   Ana sayfaya dönmek için `Ana Sayfaya Dön` butonunu kullanın.

## Sorun Giderme

-   **`ModuleNotFoundError`**: `pip install -r requirements.txt` komutunu çalıştırdığınızdan ve sanal ortamı etkinleştirdiğinizden emin olun.
-   **Grafikler görünmüyor**: İnternet bağlantınızın olduğundan ve hisse senedi kodlarının doğru olduğundan emin olun. YFinance bazen belirli hisseler için veri sağlamayabilir.



