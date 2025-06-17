# 📰 YEB Haber Scraper

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Streamlit Version](https://img.shields.io/badge/Streamlit-1.x-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Haber sitelerinden belirli tarih aralıklarındaki makaleleri çekmenizi ve indirmenizi sağlayan modern ve kullanıcı dostu bir araç. Proje, farklı haber sitelerine kolayca uyum sağlayabilen modüler bir mimariyle tasarlanmıştır.

## ✨ Özellikler

*   **Esnek Web Kazıma**: Belirli tarih aralıklarındaki haber başlıklarını, içeriklerini ve yayın tarihlerini çeker.
*   **Çoklu Site Desteği**: Hürriyet ve NTV gibi popüler Türk haber siteleri için önceden yapılandırılmış destek. Yeni siteler kolayca eklenebilir.
*   **Otomatik Tarih Algılama**: Çeşitli formatlardaki tarih bilgilerini makale sayfalarından akıllıca ayrıştırır.
*   **Kullanıcı Dostu Arayüz**: Streamlit ile geliştirilmiş sezgisel web arayüzü sayesinde kolay kullanım.
*   **Veri Dışa Aktarımı**: Çekilen haberleri CSV veya Excel formatında indirme imkanı.
*   **Gelişmiş Güvenlik ve Robustness**: Bot algılamayı önlemek için rastgele User-Agent'lar ve hata toleransı için Retry mekanizmaları.
*   **Modüler Mimari**: Kazıma mantığı, farklı sitelerin kolayca eklenebilmesi için `NewsSiteConfig` ve `UniversalNewsScraper` sınıflarıyla ayrıştırılmıştır.

## 🚀 Kurulum

Projeyi yerel makinenizde kurmak ve çalıştırmak için aşağıdaki adımları izleyin:

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/KULLANICI_ADINIZ/yeb-haber-scraper.git
cd yeb-haber-scraper
```
**Not**: Lütfen `KULLANICI_ADINIZ` kısmını kendi GitHub kullanıcı adınızla veya depo URL'nizle değiştirin.

### 2. Sanal Ortam Oluşturun (Önerilen)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

Bu komut aşağıdaki bağımlılıkları yükleyecektir:
- `requests`
- `beautifulsoup4`
- `pandas`
- `streamlit`
- `xlsxwriter`

## 🏃‍♀️ Kullanım

Projeyi kurduktan sonra Streamlit uygulamasını başlatın:

```bash
streamlit run streamlit_app.py
```

Uygulama tarayıcınızda otomatik olarak açılacaktır (genellikle `http://localhost:8501` adresinde).

### Uygulama Arayüzü:

1.  **Haber Sitesi Linki**: Kazımak istediğiniz haber sitesinin URL'sini girin (örneğin, `https://www.ntv.com.tr`).
2.  **Tarih ve Saat Aralığı**: Haberleri çekmek istediğiniz başlangıç ve bitiş tarihlerini ve saatlerini seçin.
3.  **Haberleri Çek**: Belirtilen kriterlere göre haberleri çekmek için bu butona tıklayın. İşlem süresince bir ilerleme göstergesi ve durum mesajları göreceksiniz.
4.  **Çekilen Haberler**: Haberler bulunduğunda, bir tablo halinde gösterilecektir.
5.  **Sonuçları İndir**: Çekilen haberleri CSV veya Excel formatında indirmek için ilgili butonları kullanın.
6.  **Yeni Arama Yap**: Yeni bir kazıma işlemi başlatmak için bu butona tıklayarak mevcut veriyi temizleyin.

## ⚙️ Yapılandırma

`scraper.py` dosyasındaki `NewsSiteConfig` sınıfı, farklı haber siteleri için özel yapılandırmaları tanımlamanıza olanak tanır. Uygulama, girilen URL'ye göre otomatik olarak ilgili yapılandırmayı seçmeye çalışır.

Yeni bir haber sitesi eklemek için `streamlit_app.py` dosyasındaki `get_site_config` fonksiyonunu düzenleyerek yeni bir `elif` bloğu ekleyebilir ve sitenin makale linkleri, başlıkları, içerikleri ve tarihleri için uygun CSS seçicilerini tanımlayabilirsiniz.

```python
# Örnek: Yeni bir site ekleme
elif "yenisite.com" in domain:
    return NewsSiteConfig(
        base_url=f"https://{domain}",
        listing_page_paths=["/", "/haberler"],
        article_link_selectors=['.post-link a'],
        title_selectors=['h1.entry-title'],
        content_selectors=['div.post-content'],
        date_selectors=['span.post-date'],
        turkish_date_parsing_enabled=True # Sitenin diline göre ayarla
    )
```

## 🤝 Katkıda Bulunma

Katkılarınızı memnuniyetle karşılarız! Her türlü hata düzeltmesi, özellik iyileştirmesi veya yeni haber sitesi entegrasyonu için Pull Request göndermekten çekinmeyin.

1.  Depoyu forklayın.
2.  Yeni bir özellik dalı oluşturun (`git checkout -b feature/AmazingFeature`).
3.  Değişikliklerinizi yapın ve commit edin (`git commit -m 'Add some AmazingFeature'`).
4.  Dalı push edin (`git push origin feature/AmazingFeature`).
5.  Bir Pull Request açın.

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın (eğer ayrı bir `LICENSE` dosyanız varsa).

---
**YEB Haber Scraper** - Haberleri sizin için yakalıyor! 