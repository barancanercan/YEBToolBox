# YEB Tool Box

YEB Tool Box, haber kazıyıcı ve Google Trends analiz modüllerini bir araya getiren profesyonel bir Streamlit uygulamasıdır. Kullanıcılar, haber sitelerinden belirli tarih aralıklarında makale çekebilir veya Google Trends verilerini analiz ederek anahtar kelimelerin arama eğilimlerini görselleştirebilir.

## Özellikler

- **Haber Scraper:**
  - Farklı haber sitelerinden (ör. Hurriyet, NTV) belirli tarih ve saat aralığında haber başlıkları, içerikleri ve yayın tarihlerini otomatik olarak çeker.
  - Sonuçları tablo olarak görüntüleyebilir ve CSV/Excel formatında indirebilirsiniz.

- **Google Trends Analizi:**
  - Google Trends'ten alınan CSV verilerini yükleyerek anahtar kelimelerin günlük ve saatlik arama hacimlerini analiz eder.
  - Toplam ve lider bazında aranma hacmi, ortalama değerler ve günlük zirve noktalarını interaktif grafiklerle sunar.

## Kullanım

1. Proje dizininde terminal açın ve sanal ortamı etkinleştirin:
   ```bash
   source .venv/bin/activate
   ```
2. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı başlatın:
   ```bash
   streamlit run streamlit_app.py
   ```
4. Tarayıcınızda açılan arayüzde sol menüden modül seçimi yapabilirsiniz.

## Modüller

- **Haber Scraper:**
  - Haber sitesi URL'si ve tarih aralığı girerek haberleri çekin.
  - Sonuçları tablo olarak inceleyin ve indirin.

- **Google Trends Analizi:**
  - Google Trends CSV dosyanızı yükleyin veya örnek veriyle analiz yapın.
  - Zaman aralığı seçin, ortalama ve zirve noktalarını tablo ve grafiklerle görüntüleyin.

## Proje Adı ve Uygulama

- Proje genel adı: **YEB Tool Box**
- Streamlit uygulama adı: **yebtoolbox**

---

Her türlü katkı ve geri bildirime açıktır! 