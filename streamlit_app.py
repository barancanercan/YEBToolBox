import streamlit as st
from datetime import datetime, time, timedelta, date
import pandas as pd
from urllib.parse import urlparse
from app.scraper import NewsSiteConfig, UniversalNewsScraper
import io
from app.streamlit_trend_app import run_trends_app


def get_site_config(url: str) -> NewsSiteConfig:
    # Bu fonksiyon, verilen URL'ye göre uygun NewsSiteConfig'i döndürür.
    # Gerçek bir uygulamada, bu kısım bir veritabanından veya yapılandırma dosyasından
    # siteye özgü seçicileri çekecek şekilde genişletilebilir.
    # Şimdilik, sadece Hurriyet için sabit bir konfigürasyon döndürüyoruz.
    # Gelecekte, burada daha akıllı bir URL analizi veya kullanıcıdan seçici girişi eklenebilir.

    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if "hurriyet.com.tr" in domain:
        return NewsSiteConfig(
            base_url=f"https://{domain}",
            listing_page_paths=["/gundem/", "/", "/son-dakika/"],
            article_link_selectors=[
                'a[href*="/gundem/"]',
                'a[href*="/haber/"]',
                '.news-item a',
                '.article-link'
            ],
            title_selectors=['h1', '.news-title', '.article-title'],
            content_selectors=[
                '.news-content',
                '.article-content',
                '.content',
                '.news-text',
                'div[data-news-content]'
            ],
            date_selectors=[
                'time[datetime]',
                '.news-datetime',
                '.article-date',
                '[data-date]',
                '.date-time'
            ],
            turkish_date_parsing_enabled=True
        )
    elif "ntv.com.tr" in domain:
        return NewsSiteConfig(
            base_url=f"https://{domain}",
            listing_page_paths=["/", "/son-dakika", "/turkiye", "/dunya"], # NTV için ana sayfalar
            article_link_selectors=[
                'a[data-story-channel="headline"]',
                'li.related-news-item a.card-link',
                'h3.ntv-main-slider-item-first-title a',
                'a[href*=".ntv.com.tr/"]' # Daha genel bir link seçici
            ],
            title_selectors=['h1', 'meta[property="og:title"]', 'meta[name="title"]'],
            content_selectors=['div.category-detail-content', 'div[itemprop="articleBody"]', 'div#contentBodyArea'],
            date_selectors=['meta[name="datePublished"]', 'span.date', 'time', '.pubdate'],
            turkish_date_parsing_enabled=False # NTV ISO formatını kullandığı için
        )
    else:
        # Varsayılan veya genel bir konfigürasyon, özelleştirme gerekebilir
        st.warning(f"\'{url}\' için özel bir yapılandırma bulunamadı. Genel seçiciler denenecektir. \n\n**Not:** Bu sitenin doğru çalışması için \'scraper.py\' dosyasında özel CSS seçicileri tanımlamanız gerekebilir.")
        return NewsSiteConfig(
            base_url=url,
            listing_page_paths=["/"] ,
            article_link_selectors=['a[href]', '.news-link a', '.article-card a', '.article-item a', '.post-link'],
            title_selectors=['h1', 'h2.title', '.article-title', 'meta[property="og:title"]', 'meta[name="title"]'],
            content_selectors=['div.content-body', '.article-content', 'div[itemprop="articleBody"]', 'div.entry-content', 'div.single-post-content'],
            date_selectors=['time', '.date', '.pubdate', '[data-timestamp]', 'span.post-date', 'div.date-time'],
            turkish_date_parsing_enabled=False # Varsayılan olarak Türkçe olmayan siteler için False
        )

# Ana uygulama mantığı
def main():
    st.set_page_config(
        page_title="YEB Uygulama Portalı", # Ana sayfanın başlığı
        page_icon="⭐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.sidebar.title("Uygulama Seçimi")
    app_mode = st.sidebar.radio(
        "Lütfen bir uygulama seçin:",
        ("Haber Scraper", "Google Trends Analizi")
    )

    if app_mode == "Haber Scraper":
        run_news_scraper_app()
    elif app_mode == "Google Trends Analizi":
        run_trends_app()

def run_news_scraper_app():
    st.title("📰 YEB Haber Scraper")
    st.markdown("Haber sitelerinden belirli tarih aralıklarındaki makaleleri çekin ve indirin.")

    # Session state'i başlat
    if 'news_df' not in st.session_state:
        st.session_state['news_df'] = pd.DataFrame()
    if 'button_clicked' not in st.session_state:
        st.session_state['button_clicked'] = False

    # --- Kullanıcı Girişleri ---

    st.header("1. Haber Sitesi Linki")
    news_site_url = st.text_input(
        "Lütfen haber sitesinin URL'sini girin (örneğin: https://www.hurriyet.com.tr)",
        "https://www.hurriyet.com.tr"
    )

    st.header("2. Tarih ve Saat Aralığı")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Başlangıç Tarihi", datetime.now() - timedelta(days=1))
        start_time_input = st.time_input("Başlangıç Saati", time(0, 0))

    with col2:
        end_date = st.date_input("Bitiş Tarihi", datetime.now())
        end_time_input = st.time_input("Bitiş Saati", time(23, 59))

    start_datetime = datetime.combine(start_date, start_time_input)
    end_datetime = datetime.combine(end_date, end_time_input)

    # Hata ve durum mesajları için yer tutucular
    error_placeholder = st.empty()
    status_placeholder = st.empty()

    if start_datetime >= end_datetime:
        error_placeholder.error("Başlangıç tarihi ve saati, bitiş tarihinden ve saatinden önce olmalıdır.")

    # --- Haber Çekme Butonu ---
    st.markdown("---")

    if not st.session_state['button_clicked']:
        if st.button("Haberleri Çek", type="primary", key='fetch_news_button'):
            if start_datetime < end_datetime:
                error_placeholder.empty() # Önceki hatayı temizle
                status_placeholder.info("Haberler çekiliyor, lütfen bekleyin...")
                st.session_state['button_clicked'] = True # Butona tıklandığını işaretle
                
                config = get_site_config(news_site_url)
                scraper = UniversalNewsScraper(config)
                
                # İlerleme raporlama fonksiyonu
                def update_status(message):
                    status_placeholder.info(message)

                with st.spinner('Haberler çekiliyor...'):
                    news_data = scraper.scrape_news_by_time_range(start_datetime, end_datetime, max_listing_pages=2, status_callback=update_status)
                
                if news_data:
                    st.success(f"✓ {len(news_data)} haber bulundu!")
                    df = pd.DataFrame(news_data)
                    st.session_state['news_df'] = df
                    st.rerun() # DataFrame güncellendiğinde uygulamayı yeniden çalıştır
                else:
                    st.warning("Belirtilen kriterlere uygun haber bulunamadı.")
                    st.session_state['button_clicked'] = False # Haber bulunamazsa butonu tekrar göster
            else:
                error_placeholder.error("Lütfen geçerli bir tarih aralığı seçin.")
                st.session_state['button_clicked'] = False # Hata olursa butonu tekrar göster

    # Eğer haberler çekildiyse, sonuçları ve indirme butonlarını göster
    if not st.session_state['news_df'].empty:
        st.header("3. Çekilen Haberler")
        st.dataframe(st.session_state['news_df'])

        st.subheader("4. Sonuçları İndir")
        df_to_download = st.session_state['news_df']

        col_csv, col_excel = st.columns(2)

        with col_csv:
            csv_buffer = io.StringIO()
            df_to_download.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            st.download_button(
                label="CSV Olarak İndir",
                data=csv_buffer.getvalue(),
                file_name=f"yeb_haberler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key='download_csv'
            )

        with col_excel:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df_to_download.to_excel(writer, index=False, sheet_name='Haberler')
            excel_buffer.seek(0)
            st.download_button(
                label="Excel Olarak İndir",
                data=excel_buffer.getvalue(),
                file_name=f"yeb_haberler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='download_excel'
            )

    # Eğer yeniden çekmek isterse butonu tekrar göster
    if st.session_state['button_clicked'] and not st.session_state['news_df'].empty:
        st.markdown("---")
        if st.button("Yeni Arama Yap", key='new_search_button'):
            st.session_state['news_df'] = pd.DataFrame() # Mevcut veriyi temizle
            st.session_state['button_clicked'] = False # Butonu tekrar göster
            st.rerun()

if __name__ == "__main__":
    main() 