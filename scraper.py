import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urljoin, urlparse
import pandas as pd
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class NewsSiteConfig:
    def __init__(self,
                 base_url: str,
                 article_link_selectors: list,
                 title_selectors: list,
                 content_selectors: list,
                 date_selectors: list,
                 listing_page_paths: list = None,
                 turkish_date_parsing_enabled: bool = True):
        self.base_url = base_url
        self.article_link_selectors = article_link_selectors
        self.title_selectors = title_selectors
        self.content_selectors = content_selectors
        self.date_selectors = date_selectors
        self.listing_page_paths = listing_page_paths if listing_page_paths is not None else ["/"]
        self.turkish_date_parsing_enabled = turkish_date_parsing_enabled


class UniversalNewsScraper:
    def __init__(self, config: NewsSiteConfig = None):
        self.config = config
        self.base_url = config.base_url if config else None
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        self.session = requests.Session()
        
        # Retry mekanizması
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset({'GET', 'POST'})
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _get_random_user_agent(self):
        return random.choice(self.user_agents)

    def auto_detect_site_structure(self, url: str, status_callback=None):
        """Otomatik olarak site yapısını analiz eder ve uygun seçicileri bulur"""
        try:
            if status_callback:
                status_callback("Site yapısı analiz ediliyor...")
            
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            base_url = f"{parsed_url.scheme}://{domain}"
            
            # Site ana sayfasını çek
            self.session.headers.update({'User-Agent': self._get_random_user_agent()})
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Otomatik link seçicilerini bul
            link_selectors = self._find_article_link_selectors(soup, domain)
            
            # Otomatik başlık seçicilerini bul
            title_selectors = self._get_universal_title_selectors()
            
            # Otomatik içerik seçicilerini bul
            content_selectors = self._get_universal_content_selectors()
            
            # Otomatik tarih seçicilerini bul
            date_selectors = self._get_universal_date_selectors()
            
            # Liste sayfalarını tespit et
            listing_paths = self._detect_listing_paths(soup, domain)
            
            # Türkçe tarih parsing gerekip gerekmediğini tespit et
            turkish_parsing = self._detect_turkish_date_format(soup)
            
            if status_callback:
                status_callback(f"Site analizi tamamlandı. {len(link_selectors)} link seçici bulundu.")
            
            return NewsSiteConfig(
                base_url=base_url,
                listing_page_paths=listing_paths,
                article_link_selectors=link_selectors,
                title_selectors=title_selectors,
                content_selectors=content_selectors,
                date_selectors=date_selectors,
                turkish_date_parsing_enabled=turkish_parsing
            )
            
        except Exception as e:
            if status_callback:
                status_callback(f"Site analizi hatası: {e}")
            # Fallback: Genel seçiciler
            return self._get_fallback_config(url)

    def _find_article_link_selectors(self, soup, domain):
        """Haber linklerini bulan seçicileri otomatik tespit eder"""
        selectors = []
        
        # Yaygın haber link patternleri
        common_patterns = [
            'a[href*="/haber/"]',
            'a[href*="/gundem/"]',
            'a[href*="/son-dakika/"]',
            'a[href*="/news/"]',
            'a[href*="/article/"]',
            'a[href*="/story/"]',
            f'a[href*="{domain}"]'
        ]
        
        # Yapısal seçiciler
        structural_selectors = [
            '.news-item a',
            '.article-item a',
            '.post-item a',
            '.story-card a',
            '.news-card a',
            '.article-card a',
            '.headline a',
            '.news-title a',
            '.story-title a',
            'article a',
            '.entry-title a',
            '.post-title a'
        ]
        
        # Class ve id bazlı seçiciler
        class_id_selectors = []
        
        # Sayfadaki tüm linkleri analiz et
        all_links = soup.find_all('a', href=True)
        href_patterns = set()
        
        for link in all_links:
            href = link.get('href', '')
            if any(pattern in href.lower() for pattern in ['haber', 'news', 'article', 'story', 'gundem', 'son-dakika']):
                # Parent elementlerin class/id'lerini topla
                parent = link.parent
                while parent and parent.name != 'body':
                    if parent.get('class'):
                        for cls in parent.get('class'):
                            if any(keyword in cls.lower() for keyword in ['news', 'article', 'story', 'post', 'item', 'card']):
                                class_id_selectors.append(f'.{cls} a')
                    if parent.get('id'):
                        if any(keyword in parent.get('id').lower() for keyword in ['news', 'article', 'story', 'post']):
                            class_id_selectors.append(f'#{parent.get("id")} a')
                    parent = parent.parent
        
        # Tüm seçicileri birleştir
        selectors.extend(common_patterns)
        selectors.extend(structural_selectors)
        selectors.extend(list(set(class_id_selectors)))
        
        return list(set(selectors))  # Duplicate'leri kaldır

    def _get_universal_title_selectors(self):
        """Universal başlık seçicileri"""
        return [
            'h1',
            'h1.title',
            'h1.article-title',
            'h1.news-title',
            'h1.story-title',
            'h1.headline',
            '.article-title h1',
            '.news-title h1',
            '.story-title h1',
            '.entry-title h1',
            '.post-title h1',
            'meta[property="og:title"]',
            'meta[name="title"]',
            'title'
        ]

    def _get_universal_content_selectors(self):
        """Universal içerik seçicileri"""
        return [
            '.article-content',
            '.news-content',
            '.story-content',
            '.post-content',
            '.entry-content',
            '.content-body',
            '.article-body',
            '.news-body',
            '.story-body',
            '.post-body',
            'div[itemprop="articleBody"]',
            '[data-article-content]',
            '[data-news-content]',
            '.content',
            'article .content',
            '.main-content',
            '.article-text',
            '.news-text',
            '.story-text'
        ]

    def _get_universal_date_selectors(self):
        """Universal tarih seçicileri"""
        return [
            'time[datetime]',
            'time',
            '.date',
            '.publish-date',
            '.publication-date',
            '.article-date',
            '.news-date',
            '.story-date',
            '.post-date',
            '.timestamp',
            '[data-date]',
            '[data-timestamp]',
            'meta[property="article:published_time"]',
            'meta[name="datePublished"]',
            'meta[name="publishdate"]',
            '.date-time',
            '.pubdate',
            '.published'
        ]

    def _detect_listing_paths(self, soup, domain):
        """Site yapısından liste sayfalarını tespit eder"""
        paths = ["/"]
        
        # Navigation menüsünden önemli kategorileri bul
        nav_links = soup.find_all('a', href=True)
        important_categories = ['gundem', 'haber', 'son-dakika', 'news', 'breaking', 'latest']
        
        for link in nav_links:
            href = link.get('href', '').lower()
            if any(cat in href for cat in important_categories):
                # Relative URL'leri tam URL'ye çevir
                if href.startswith('/'):
                    paths.append(href)
                elif domain in href:
                    parsed = urlparse(href)
                    paths.append(parsed.path)
        
        return list(set(paths))

    def _detect_turkish_date_format(self, soup):
        """Türkçe tarih formatı kullanılıp kullanılmadığını tespit eder"""
        # HTML lang attribute kontrol et
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            lang = html_tag.get('lang').lower()
            if 'tr' in lang:
                return True
        
        # Meta tag'lerde Türkçe kontrol et
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            content = meta.get('content', '').lower()
            if any(word in content for word in ['türkiye', 'türkçe', 'turkish']):
                return True
        
        # Sayfa içeriğinde Türkçe ay isimleri ara
        page_text = soup.get_text().lower()
        turkish_months = ['ocak', 'şubat', 'mart', 'nisan', 'mayıs', 'haziran', 
                         'temmuz', 'ağustos', 'eylül', 'ekim', 'kasım', 'aralık']
        
        return any(month in page_text for month in turkish_months)

    def _get_fallback_config(self, url):
        """Fallback konfigürasyon"""
        parsed_url = urlparse(url)
        return NewsSiteConfig(
            base_url=f"{parsed_url.scheme}://{parsed_url.netloc}",
            listing_page_paths=["/"],
            article_link_selectors=['a[href]'],
            title_selectors=['h1', 'title'],
            content_selectors=['.content', 'article', '.main'],
            date_selectors=['time', '.date'],
            turkish_date_parsing_enabled=True
        )

    def parse_date_from_article(self, article_url):
        """Haber sayfasından tarih bilgisini çıkarır - geliştirilmiş versiyon"""
        try:
            self.session.headers.update({'User-Agent': self._get_random_user_agent()})
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(article_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')

            # Önce meta tag'leri kontrol et (en güvenilir)
            meta_selectors = [
                'meta[property="article:published_time"]',
                'meta[name="datePublished"]',
                'meta[name="publishdate"]',
                'meta[name="date"]',
                'meta[property="og:updated_time"]'
            ]
            
            for selector in meta_selectors:
                meta_tag = soup.select_one(selector)
                if meta_tag:
                    date_content = meta_tag.get('content', '')
                    parsed_date = self._parse_any_date_format(date_content)
                    if parsed_date:
                        return parsed_date

            # Sonra normal seçicileri dene
            for selector in self.config.date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    date_text = date_element.get('datetime') or date_element.get_text().strip()
                    parsed_date = self._parse_any_date_format(date_text)
                    if parsed_date:
                        return parsed_date

            # JSON-LD structured data kontrol et
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        date_published = data.get('datePublished') or data.get('dateCreated')
                        if date_published:
                            parsed_date = self._parse_any_date_format(date_published)
                            if parsed_date:
                                return parsed_date
                except:
                    continue

        except Exception as e:
            print(f"Tarih parse edilemedi {article_url}: {e}")
        return None

    def _parse_any_date_format(self, date_str):
        """Herhangi bir tarih formatını parse etmeye çalışır"""
        if not date_str:
            return None
            
        date_str = str(date_str).strip()
        
        # ISO format (en yaygın)
        try:
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            pass
        
        # Türkçe tarih formatları
        if self.config.turkish_date_parsing_enabled:
            turkish_date = self.parse_turkish_date(date_str)
            if turkish_date:
                return turkish_date
        
        # Diğer yaygın formatlar
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%d.%m.%Y %H:%M:%S',
            '%d.%m.%Y %H:%M',
            '%d.%m.%Y',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
                
        return None

    def parse_turkish_date(self, date_str):
        """Türkçe tarih formatını parse eder - geliştirilmiş"""
        try:
            # ISO format kontrolü
            if 'T' in date_str and ('Z' in date_str or '+' in date_str):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)

            # Türkçe ay isimleri
            months = {
                'ocak': '01', 'şubat': '02', 'mart': '03', 'nisan': '04',
                'mayıs': '05', 'haziran': '06', 'temmuz': '07', 'ağustos': '08',
                'eylül': '09', 'ekim': '10', 'kasım': '11', 'aralık': '12',
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }

            date_str = date_str.lower().strip()

            # Çeşitli Türkçe tarih formatları
            patterns = [
                r'(\d{1,2})\s+(\w+)\s+(\d{4})\s+(\d{1,2}):(\d{2})',  # 17 haziran 2025 15:30
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # 17 haziran 2025
                r'(\d{2})\.(\d{2})\.(\d{4})\s*-?\s*(\d{1,2}):(\d{2})',  # 17.06.2025 - 15:30
                r'(\d{2})\.(\d{2})\.(\d{4})',  # 17.06.2025
                r'(\d{2})/(\d{2})/(\d{4})\s+(\d{1,2}):(\d{2})',  # 17/06/2025 15:30
                r'(\d{2})/(\d{2})/(\d{4})'  # 17/06/2025
            ]

            for i, pattern in enumerate(patterns):
                match = re.search(pattern, date_str)
                if match:
                    groups = match.groups()
                    if i == 0:  # Türkçe ay isimli format
                        day, month_name, year, hour, minute = groups
                        month = months.get(month_name, '01')
                        return datetime(int(year), int(month), int(day), int(hour), int(minute))
                    elif i == 1:  # Türkçe ay isimli format (saat yok)
                        day, month_name, year = groups
                        month = months.get(month_name, '01')
                        return datetime(int(year), int(month), int(day))
                    elif i == 2:  # DD.MM.YYYY - HH:MM
                        day, month, year, hour, minute = groups
                        return datetime(int(year), int(month), int(day), int(hour), int(minute))
                    elif i == 3:  # DD.MM.YYYY
                        day, month, year = groups
                        return datetime(int(year), int(month), int(day))
                    elif i == 4:  # DD/MM/YYYY HH:MM
                        day, month, year, hour, minute = groups
                        return datetime(int(year), int(month), int(day), int(hour), int(minute))
                    elif i == 5:  # DD/MM/YYYY
                        day, month, year = groups
                        return datetime(int(year), int(month), int(day))

        except Exception as e:
            print(f"Türkçe tarih parse hatası: {e}")
        return None

    def get_article_content(self, article_url):
        """Haber içeriğini çeker - geliştirilmiş"""
        try:
            self.session.headers.update({'User-Agent': self._get_random_user_agent()})
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(article_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')

            # Reklamları ve gereksiz içerikleri temizle
            for unwanted in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', '.ad', '.advertisement', '.social-share']):
                unwanted.decompose()

            # İçerik seçicilerini dene
            for selector in self.config.content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # Paragrafları birleştir
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                        if len(content) > 100:  # Yeterince uzun içerik varsa
                            return content
                    else:
                        content = content_div.get_text().strip()
                        if len(content) > 100:
                            return content

            # Fallback: Tüm paragrafları al
            all_paragraphs = soup.find_all('p')
            if all_paragraphs:
                content = ' '.join([p.get_text().strip() for p in all_paragraphs if len(p.get_text().strip()) > 20])
                if len(content) > 100:
                    return content

            return "İçerik çekilemedi"
            
        except Exception as e:
            print(f"İçerik çekme hatası {article_url}: {e}")
            return "İçerik çekilemedi"

    def scrape_news_by_time_range(self, start_time, end_time, max_listing_pages: int = 3, status_callback=None):
        """Belirli zaman aralığındaki haberleri çeker - geliştirilmiş"""
        if not self.config:
            if status_callback:
                status_callback("Hata: Site konfigürasyonu bulunamadı")
            return []

        news_list = []
        pages_visited = 0
        processed_urls = set()  # Duplicate URL'leri önlemek için

        print(f"[SCRAPER] Başlangıç tarihi: {start_time}, Bitiş tarihi: {end_time}")
        print(f"[SCRAPER] Maksimum ziyaret edilecek listeleme sayfası: {max_listing_pages}")

        try:
            for page_path in self.config.listing_page_paths:
                if pages_visited >= max_listing_pages:
                    if status_callback:
                        status_callback(f"Maksimum {max_listing_pages} listeleme sayfası ziyaret edildi.")
                    break

                page_url = urljoin(self.config.base_url, page_path)
                if status_callback:
                    status_callback(f"Sayfa kontrol ediliyor: {page_url}")

                try:
                    self.session.headers.update({'User-Agent': self._get_random_user_agent()})
                    time.sleep(random.uniform(2, 4))

                    response = self.session.get(page_url, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Haber linklerini bul
                    news_links = set()
                    for selector in self.config.article_link_selectors:
                        try:
                            links = soup.select(selector)
                            for link in links:
                                href = link.get('href')
                                if href:
                                    full_url = urljoin(self.config.base_url, href)
                                    if self._is_valid_news_url(full_url):
                                        news_links.add(full_url)
                        except Exception as e:
                            continue  # Bu seçici çalışmadı, diğerini dene

                    if status_callback:
                        status_callback(f"Bulunan benzersiz haber linki: {len(news_links)}")

                    # Her haberi kontrol et
                    for i, news_url in enumerate(list(news_links)[:30]):  # İlk 30 haberi kontrol et
                        if news_url in processed_urls:
                            continue
                        processed_urls.add(news_url)

                        if status_callback:
                            status_callback(f"Haber kontrol ediliyor ({i + 1}/30): {news_url[:50]}...")

                        try:
                            # Haber sayfasını çek
                            self.session.headers.update({'User-Agent': self._get_random_user_agent()})
                            time.sleep(random.uniform(1, 3))

                            response = self.session.get(news_url, timeout=15)
                            response.raise_for_status()
                            
                            soup = BeautifulSoup(response.content, 'html.parser')

                            # Başlık
                            title = self._extract_title(soup)
                            
                            # Tarih
                            news_date = self.parse_date_from_article(news_url)
                            
                            if news_date and start_time <= news_date <= end_time:
                                if status_callback:
                                    status_callback(f"✓ Haber zaman aralığında: {title[:30]}...")

                                # İçeriği çek
                                content = self.get_article_content(news_url)
                                
                                # Kaynak bilgisi
                                source = self._extract_source(soup, content)

                                news_list.append({
                                    'Haber Başlığı': title,
                                    'Haber Metni': content,
                                    'Haber Linki': news_url,
                                    'Tarih': news_date.strftime('%Y-%m-%d %H:%M'),
                                    'Kaynak': source
                                })

                        except Exception as e:
                            if status_callback:
                                status_callback(f"Haber işleme hatası: {e}")
                            continue

                    pages_visited += 1

                except Exception as e:
                    if status_callback:
                        status_callback(f"Sayfa erişim hatası {page_url}: {e}")
                    continue

        except Exception as e:
            if status_callback:
                status_callback(f"Genel scraping hatası: {e}")

        print(f"[SCRAPER] Scraping tamamlandı. Toplam bulunan haber: {len(news_list)}")
        return news_list

    def _is_valid_news_url(self, url):
        """URL'nin geçerli bir haber URL'i olup olmadığını kontrol eder"""
        if not url or not url.startswith(('http://', 'https://')):
            return False
            
        # Hariç tutulacak URL türleri
        excluded_patterns = [
            '/galeri/', '/video/', '/canli-yayin/', '/fotogaleri/', '/multimedya/',
            '/infografik/', '/yazarlar/', '/kategori/', '/etiket/', '/tag/',
            '/search/', '/arama/', '/rss/', '/sitemap/', '/404/', '/hakkimizda/',
            '/projeler/', '/egitim/', '/iletisim/', '/reklam/', '/login/', '/kayit/'
        ]
        
        if any(pattern in url.lower() for pattern in excluded_patterns):
            return False
            
        return True

    def _extract_title(self, soup):
        """Sayfadan başlığı çıkarır"""
        for selector in self.config.title_selectors:
            try:
                title_elem = soup.select_one(selector)
                if title_elem:
                    if title_elem.name == 'meta':
                        title = title_elem.get('content', '').strip()
                    else:
                        title = title_elem.get_text().strip()
                    
                    if title and len(title) > 10:  # Çok kısa başlıkları atla
                        return title
            except:
                continue
        return "Başlık bulunamadı"

    def _extract_source(self, soup, content):
        """Kaynak bilgisini çıkarır"""
        # Meta tag'lerden yazar bilgisi
        author_selectors = [
            'meta[name="author"]',
            'meta[name="articleAuthor"]',
            'meta[property="article:author"]'
        ]
        
        for selector in author_selectors:
            meta_author = soup.select_one(selector)
            if meta_author:
                return meta_author.get('content', '').strip()
        
        # İçerik içinde yaygın haber ajansları
        if content and content != "İçerik çekilemedi":
            agencies = ['İHA', 'AA', 'DHA', 'Reuters', 'AP', 'AFP']
            for agency in agencies:
                if agency in content:
                    return agency
                    
        return "Kaynak bulunamadı"

    def save_to_csv(self, news_list, filename):
        """Haberleri CSV dosyasına kaydeder"""
        if not news_list:
            print("Kaydedilecek haber bulunamadı.")
            return

        df = pd.DataFrame(news_list)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✓ {len(news_list)} haber {filename} dosyasına kaydedildi.") 