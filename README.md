# 🚀 YEB Tool Box

YEB Tool Box, haber kazıyıcı ve Google Trends analiz modüllerini bir araya getiren, modern ve profesyonel bir **Streamlit** uygulamasıdır. Bu araç, medya ve veri analizi alanında çalışanlar için hızlı, esnek ve kullanıcı dostu bir çözüm sunar.

---

## 📦 İçindekiler
- [Özellikler](#özellikler)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Modüller](#modüller)
- [Klasör Yapısı](#klasör-yapısı)
- [Mimari ve Genişletilebilirlik](#mimari-ve-genişletilebilirlik)
- [Katkı ve Destek](#katkı-ve-destek)
- [Lisans](#lisans)

---

## ✨ Özellikler

- **Çoklu Modül:** Tek arayüzde hem haber kazıyıcı hem de Google Trends analiz aracı.
- **Kullanıcı Dostu:** Modern, sade ve etkileşimli Streamlit arayüzü.
- **Veri Dışa Aktarımı:** Sonuçları kolayca CSV veya Excel olarak indirin.
- **Gelişmiş Tarih/Saat Filtreleme:** Esnek zaman aralığı seçimiyle hassas analiz.
- **Görselleştirme:** Plotly tabanlı interaktif grafikler ve özet tablolar.
- **Kolay Genişletilebilirlik:** Yeni haber siteleri veya analiz modülleri kolayca eklenebilir.

---

## ⚡ Kurulum

1. **Depoyu Klonlayın:**
   ```bash
   git clone https://github.com/barancanercan/yebtoolbox.git
   cd yebtoolbox
   ```
2. **Sanal Ortamı Aktifleştirin:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Bağımlılıkları Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Kullanım

Uygulamayı başlatmak için:
```bash
streamlit run streamlit_app.py
```
Tarayıcınızda açılan arayüzde sol menüden modül seçimi yapabilirsiniz.

---

## 🧩 Modüller

### 1. Haber Scraper
- **Amaç:** Farklı haber sitelerinden (ör. Hurriyet, NTV) belirli tarih ve saat aralığında haber başlıkları, içerikleri ve yayın tarihlerini otomatik olarak çekmek.
- **Kullanım:**
  - Haber sitesi URL'si ve tarih aralığı girin.
  - "Haberleri Çek" butonuna tıklayın.
  - Sonuçları tablo olarak inceleyin ve CSV/Excel olarak indirin.
- **Teknik:**
  - Esnek CSS seçici mimarisi ile yeni siteler kolayca eklenebilir.
  - Otomatik tarih algılama ve hata toleransı.

### 2. Google Trends Analizi
- **Amaç:** Google Trends'ten alınan CSV verilerini analiz ederek anahtar kelimelerin günlük ve saatlik arama hacimlerini, ortalama değerleri ve zirve noktalarını görselleştirmek.
- **Kullanım:**
  - Google Trends CSV dosyanızı yükleyin veya örnek veriyle analiz yapın.
  - Zaman aralığı seçin.
  - Ortalama ve zirve noktalarını tablo ve grafiklerle görüntüleyin.
- **Teknik:**
  - IQR yöntemiyle otomatik zirve (outlier) tespiti.
  - Plotly ile etkileşimli grafikler.

---

## 📁 Klasör Yapısı

```
yebtoolbox/
│
├── app/                       # Uygulama ana kodları
│   ├── __init__.py
│   ├── scraper.py             # Haber kazıyıcı modülü
│   ├── trend_analyzer.py      # Google Trends analiz modülü
│   └── streamlit_trend_app.py # Trends arayüz fonksiyonu
│
├── main.py                    # (Opsiyonel) Ana giriş noktası
├── streamlit_app.py           # Tümleşik Streamlit arayüzü
├── requirements.txt           # Bağımlılıklar
├── README.md                  # Dokümantasyon
├── ornekdata.csv              # (Opsiyonel) Örnek veri
│
└── .venv/                     # Sanal ortam (git ile takip edilmez)
└── .idea/                     # IDE ayarları (git ile takip edilmez)
└── __pycache__/               # Derlenmiş dosyalar (git ile takip edilmez)
└── .devcontainer/             # (Varsa) Geliştirici konteyner ayarları
```

- Tüm ana modüller `app/` klasöründe toplanmıştır.
- Sanal ortam, derlenmiş dosyalar, IDE ayarları ve geliştirme konteynerleri `.gitignore` ile hariç tutulur.

### Hariç Tutulanlar (.gitignore)

Aşağıdaki dosya ve klasörler git ile takip edilmez:

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual environment
.venv/
venv/
env/

# IDE/editor
.idea/
.vscode/
*.swp

# OS
.DS_Store

# Dev containers
.devcontainer/
```

---

## 🏗️ Mimari ve Genişletilebilirlik

- **Modüler Yapı:**
  - Her modül bağımsız fonksiyonlar ve sınıflar ile geliştirilmiştir.
  - Yeni bir haber sitesi eklemek için `app/scraper.py` ve `get_site_config` fonksiyonuna yeni bir blok eklemeniz yeterlidir.
- **Kolay Entegrasyon:**
  - Yeni analiz modülleri veya veri kaynakları eklemek için mevcut yapıyı kullanabilirsiniz.
- **Örnek:**
  ```python
  # Yeni bir haber sitesi eklemek için:
  elif "yenisite.com" in domain:
      return NewsSiteConfig(
          base_url=f"https://{domain}",
          listing_page_paths=["/", "/haberler"],
          article_link_selectors=['.post-link a'],
          title_selectors=['h1.entry-title'],
          content_selectors=['div.post-content'],
          date_selectors=['span.post-date'],
          turkish_date_parsing_enabled=True
      )
  ```

---

## 🤝 Katkı ve Destek

- Katkılarınızı memnuniyetle karşılıyoruz! Hataları bildirin, yeni özellikler önerin veya doğrudan Pull Request gönderin.
- Soru ve önerileriniz için [issue açabilirsiniz](https://github.com/KULLANICI_ADINIZ/yebtoolbox/issues) veya doğrudan iletişime geçebilirsiniz.

---

## 📄 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Ayrıntılar için `LICENSE` dosyasına bakınız.

---

**YEB Tool Box** ile veri ve haber analizinde profesyonel çözümler! ✨ 