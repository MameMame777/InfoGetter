import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from typing import List
import time
import re
from urllib.parse import urljoin, urlparse
import sys
import os

# コンテンツフォールバック機能をインポート
try:
    from ..utils.content_fallback import ContentFallbackGenerator
except ImportError:
    # フォールバック用のダミークラス
    class ContentFallbackGenerator:
        def generate_content_from_title(self, title: str, url: str, source: str = "FPGA Documentation") -> str:
            return f"Title: {title}\nURL: {url}\nSource: {source}\nNote: Content could not be retrieved due to access restrictions."

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.scrapers.base_scraper import BaseScraper
from src.models.document import Document, DataSourceType


class AlteraScraper(BaseScraper):
    """Altera (Intel) ドキュメントサイトのスクレイパー"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        # コンテンツフォールバック生成器を初期化
        self.content_fallback = ContentFallbackGenerator()
    
    def get_source_type(self) -> DataSourceType:
        return DataSourceType.WEB_SCRAPING
    
    def scrape_documents(self) -> List[Document]:
        """Alteraのドキュメントをスクレイピング（Seleniumのみ）"""
        self.logger.info("Starting Altera document scraping with Selenium")
        
        # Seleniumで直接スクレイピング
        documents = self._scrape_with_selenium()
        
        return self.validate_data(documents)
    
    def _create_webdriver(self):
        """設定に基づいてWebDriverを作成"""
        browser_type = self.config.get('browser', {}).get('type', 'chrome').lower()
        headless = self.config.get('browser', {}).get('headless', True)
        
        self.logger.info(f"Creating WebDriver: {browser_type} (headless: {headless})")
        
        if browser_type == 'firefox':
            return self._create_firefox_driver(headless)
        else:
            return self._create_chrome_driver(headless)
    
    def _create_chrome_driver(self, headless=True):
        """Chrome WebDriverを作成"""
        try:
            chrome_options = ChromeOptions()
            
            if headless:
                chrome_options.add_argument('--headless')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # カスタムパスの確認
            custom_path = self.config.get('browser', {}).get('chromedriver_path')
            if custom_path and os.path.exists(custom_path):
                self.logger.info(f"Using custom ChromeDriver: {custom_path}")
                service = ChromeService(custom_path)
            else:
                service = ChromeService(ChromeDriverManager().install())
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # User-Agentを設定
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Chrome WebDriver作成エラー: {e}")
            raise
    
    def _create_firefox_driver(self, headless=True):
        """Firefox WebDriverを作成"""
        try:
            firefox_options = FirefoxOptions()
            
            if headless:
                firefox_options.add_argument('--headless')
            
            firefox_options.add_argument('--no-sandbox')
            firefox_options.add_argument('--disable-dev-shm-usage')
            firefox_options.add_argument('--disable-extensions')
            
            # User-Agentの設定
            firefox_options.set_preference("general.useragent.override", 
                                         "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0")
            
            # カスタムパスの確認
            custom_path = self.config.get('browser', {}).get('geckodriver_path')
            if custom_path and os.path.exists(custom_path):
                self.logger.info(f"Using custom GeckoDriver: {custom_path}")
                service = FirefoxService(custom_path)
            else:
                service = FirefoxService(GeckoDriverManager().install())
            
            driver = webdriver.Firefox(service=service, options=firefox_options)
            
            # タイムアウト設定
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Firefox WebDriver作成エラー: {e}")
            raise
    
    def _scrape_with_selenium(self) -> List[Document]:
        """Seleniumでスクレイピング"""
        driver = None
        
        try:
            driver = self._create_webdriver()
            
            url = self._build_search_url()  # 設定から動的にURLを構築
            self.logger.info(f"Accessing Altera search URL: {url}")
            driver.get(url)
            
            # ページが完全に読み込まれるまで待機
            page_timeout = self.config.get('page_load_timeout', 30)
            WebDriverWait(driver, page_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 検索結果が読み込まれるまで待機
            time.sleep(5)
            
            # ページのタイトルとURLを確認
            self.logger.info(f"Page title: {driver.title}")
            self.logger.info(f"Current URL: {driver.current_url}")
            
            # スクロールして追加の結果を読み込む
            documents = self._scroll_and_extract_documents_altera(driver, url)
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Selenium scraping error: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def _parse_altera_results(self, soup: BeautifulSoup, search_url: str, seen_urls: set = None) -> List[Document]:
        """Alteraの検索結果をパース"""
        documents = []
        if seen_urls is None:
            seen_urls = set()
        
        # Intel/Alteraサイトの検索結果構造に特化したセレクター
        # 実際の検索結果を取得するための具体的なセレクター
        link_selectors = [
            # Intel検索結果の主要セレクター
            '.search-results .search-result a',
            '.search-results .result-item a',
            '.search-results .result-link',
            '.search-results a[href*="docs.intel.com"]',
            '.search-results a[href*="/docs/programmable/"]',
            
            # 検索結果のタイトルリンク
            '.search-result-title a',
            '.result-title a',
            '.doc-title a',
            '.document-title a',
            
            # 検索結果リスト
            '.search-result-list a',
            '.result-list a',
            '.document-list a',
            '.docs-list a',
            
            # Intel固有の検索結果構造
            '[data-content-type="document"] a',
            '[data-content-type="user-guide"] a',
            '[data-content-type="datasheet"] a',
            
            # より具体的なドキュメントリンク
            'a[href*="/docs/programmable/"]',
            'a[href*="intel.com/content/www/us/en/docs/"]',
            'a[href*="intel.com/content/dam/"]',
            
            # PDF and document links
            'a[href$=".pdf"]',
            'a[href*=".pdf"]',
            'a[title*="User Guide"]',
            'a[title*="Handbook"]',
            'a[title*="Reference Manual"]',
            'a[title*="IP Core"]',
            'a[title*="DSP"]',
            
            # 検索結果内のテキストリンク
            'div[class*="search"] a[href*="docs"]',
            'div[class*="result"] a[href*="docs"]',
            'li[class*="result"] a',
            'li[class*="search"] a',
            
            # フォールバック: 一般的なドキュメントリンク
            'a[href*="guide"]',
            'a[href*="manual"]',
            'a[href*="handbook"]',
            'a[href*="reference"]'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                try:
                    href = link.get('href')
                    if not href:
                        continue
                    
                    # 相対URLを絶対URLに変換
                    if href.startswith('/'):
                        parsed_search = urlparse(search_url)
                        full_url = f"{parsed_search.scheme}://{parsed_search.netloc}{href}"
                    else:
                        full_url = href
                    
                    # 重複チェック（見つかった時点で処理を終了）
                    if full_url in seen_urls:
                        continue
                    
                    # タイトルを取得
                    title = link.get('title') or link.text.strip()
                    if not title:
                        continue
                    
                    # 特定の除外タイトルをチェック
                    if self._is_excluded_title(title):
                        continue
                    
                    # URL除外チェック
                    if self._is_excluded_url(full_url):
                        continue
                    
                    # FPGA関連のドキュメントかどうかをチェック
                    if not self._is_fpga_related(title + ' ' + full_url):
                        continue
                    
                    # URLを見つかったセットに追加
                    seen_urls.add(full_url)
                    
                    # FPGAシリーズを推定
                    fpga_series = self._extract_fpga_series(title + ' ' + full_url)
                    
                    # ファイルタイプを推定
                    file_type = self._extract_file_type(full_url)
                    
                    # カテゴリを推定
                    category = self._extract_category(title)
                    
                    # コンテンツを取得（高度なBot回避技術付き）
                    content = self._get_document_content(full_url, title)
                    
                    # 403エラーで取得できない場合はフォールバックコンテンツを生成
                    if not content or len(content.strip()) < 100:
                        self.logger.warning(f"Insufficient content for {title} ({full_url}), generating fallback content")
                        # フォールバックコンテンツを生成
                        content = self._generate_content_from_title(title, full_url)
                    
                    doc = self._create_document(
                        name=title,
                        url=full_url,
                        category=category,
                        fpga_series=fpga_series,
                        file_type=file_type,
                        search_url=search_url,  # 検索URLを追加
                        content=content  # コンテンツを渡す
                    )
                    
                    documents.append(doc)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing link: {e}")
                    continue
        
        self.logger.info(f"Found {len(documents)} documents from Altera using URL: {search_url}")
        return documents
    
    def _extract_fpga_series(self, text: str) -> str:
        """テキストからFPGAシリーズを抽出"""
        text_lower = text.lower()
        
        series_patterns = {
            'stratix': r'stratix',
            'arria': r'arria',
            'cyclone': r'cyclone',
            'max': r'max\s*10',
            'agilex': r'agilex'
        }
        
        for series, pattern in series_patterns.items():
            if re.search(pattern, text_lower):
                return series.capitalize()
        
        return None
    
    def _extract_file_type(self, url: str) -> str:
        """URLからファイルタイプを抽出"""
        if url.endswith('.pdf'):
            return 'pdf'
        elif url.endswith('.html') or url.endswith('.htm'):
            return 'html'
        elif 'pdf' in url.lower():
            return 'pdf'
        else:
            return 'html'
    
    def _extract_category(self, title: str) -> str:
        """タイトルからカテゴリを抽出"""
        title_lower = title.lower()
        
        if 'data sheet' in title_lower or 'datasheet' in title_lower:
            return 'Data Sheet'
        elif 'user guide' in title_lower or 'manual' in title_lower:
            return 'User Guide'
        elif ('ip' in title_lower and 'core' in title_lower) or 'ip core' in title_lower:
            return 'IP Core'
        elif 'reference' in title_lower:
            return 'Reference'
        elif 'dsp' in title_lower:
            return 'DSP'
        elif 'tutorial' in title_lower:
            return 'Tutorial'
        elif 'application note' in title_lower or 'app note' in title_lower:
            return 'Application Note'
        elif 'white paper' in title_lower:
            return 'White Paper'
        elif 'specification' in title_lower or 'spec' in title_lower:
            return 'Specification'
        else:
            return 'Document'
    
    def _is_fpga_related(self, text: str) -> bool:
        """FPGA関連のドキュメントかどうかを判定"""
        text_lower = text.lower()
        
        # FPGA関連のキーワード
        fpga_keywords = [
            'fpga', 'ip core', 'dsp', 'stratix', 'arria', 'cyclone', 'max', 'agilex',
            'altera', 'intel', 'quartus', 'platform designer', 'qsys', 'nios',
            'programmable logic', 'reconfigurable', 'hardware acceleration',
            'pcie', 'ddr', 'ethernet', 'axi', 'avalon', 'hdl', 'verilog', 'vhdl',
            'opencl', 'oneapi', 'soc', 'hps', 'arm', 'processor'
        ]
        
        # 除外キーワード
        exclude_keywords = [
            'privacy', 'legal', 'terms', 'conditions', 'policy', 'statement', 'corporate',
            'investor', 'financial', 'annual report', 'press release', 'news', 'career',
            'job', 'marketing', 'sales', 'contact', 'support',
            # 企業・法的文書の追加
            'modern slavery', 'forced labor', '強制労働', 'uk tax strategy', '英国税務戦略',
            'tax strategy', 'corporate governance', 'sustainability', 'social responsibility',
            'csr report', 'compliance', 'ethics', 'code of conduct', 'supplier code',
            'human rights', 'diversity', 'environmental', 'carbon footprint',
            # ナビゲーション要素
            'language selection', 'sign in', 'register', 'login', 'sitemap',
            'breadcrumb', 'navigation', 'menu', 'search results', 'home page',
            'back to top', 'contact us', 'about us', 'help', 'feedback'
        ]
        
        # 除外キーワードがある場合は除外
        for keyword in exclude_keywords:
            if keyword in text_lower:
                return False
        
        # FPGA関連キーワードがある場合は含める
        for keyword in fpga_keywords:
            if keyword in text_lower:
                return True
        
        # ドキュメントのパスが特定のパターンにマッチする場合は含める
        doc_patterns = [
            '/docs/programmable/',
            '/content/www/us/en/docs/',
            '.pdf',
            'user-guide',
            'handbook',
            'reference-manual'
        ]
        
        for pattern in doc_patterns:
            if pattern in text_lower:
                return True
        
        return False
    
    def _build_search_url(self) -> str:
        """設定から検索URLを構築"""
        base_url = self.config.get('base_url')
        search_params = self.config.get('search_params', {})
        
        # パラメータを構築
        params = []
        
        # クエリパラメータ
        query = search_params.get('query', 'DSP')
        params.append(f"q={query}")
        
        # ソートパラメータ
        sort = search_params.get('sort', 'Relevancy')
        params.append(f"s={sort}")
        
        # 完全なURLを構築
        full_url = f"{base_url}?{'&'.join(params)}"
        
        self.logger.info(f"Built Altera search URL: {full_url}")
        return full_url
    
    def _scroll_and_extract_documents_altera(self, driver, search_url: str) -> List[Document]:
        """スクロールしながらドキュメントを抽出（Altera用）"""
        documents = []
        seen_urls = set()  # 重複チェック用のセット
        max_results = self.config.get('max_results', 200)
        scroll_pages = self.config.get('scroll_pages', 10)
        load_more_attempts = self.config.get('load_more_attempts', 5)
        scroll_delay = self.config.get('scroll_delay', 2)
        
        self.logger.info(f"Starting Altera document extraction with max_results={max_results}, scroll_pages={scroll_pages}")
        
        # 初期ページを解析
        initial_documents = self._extract_current_page_altera(driver, search_url, seen_urls)
        documents.extend(initial_documents)
        self.logger.info(f"Initial page: {len(initial_documents)} documents")
        
        # スクロールとページネーションで追加のドキュメントを取得
        no_new_content_count = 0
        max_no_new_content = 3  # 連続して新しいコンテンツがない場合の最大回数
        
        for page in range(1, scroll_pages):
            if len(documents) >= max_results:
                self.logger.info(f"Reached max_results limit ({max_results}), stopping extraction")
                break
            
            self.logger.info(f"Processing page {page + 1}/{scroll_pages}")
            
            # ページを進める
            success = self._navigate_to_next_page_altera(driver, load_more_attempts, scroll_delay)
            if not success:
                self.logger.warning("Failed to navigate to next page")
                break
            
            # 現在のページからドキュメントを取得
            page_documents = self._extract_current_page_altera(driver, search_url, seen_urls)
            
            if not page_documents:
                no_new_content_count += 1
                self.logger.info(f"No new documents found on page {page + 1} (consecutive empty: {no_new_content_count})")
                
                if no_new_content_count >= max_no_new_content:
                    self.logger.info("Too many consecutive empty pages, stopping extraction")
                    break
            else:
                no_new_content_count = 0
                documents.extend(page_documents)
                self.logger.info(f"Page {page + 1}: {len(page_documents)} new documents (total: {len(documents)})")
        
        # 最大件数に制限
        if len(documents) > max_results:
            documents = documents[:max_results]
            self.logger.info(f"Trimmed results to max_results limit ({max_results})")
        
        self.logger.info(f"Total unique documents found: {len(documents)}")
        return documents
    
    def _extract_current_page_altera(self, driver, search_url: str, seen_urls: set) -> List[Document]:
        """現在のページからドキュメントを抽出（Altera用）"""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # デバッグ用：ページのHTMLをログに出力（最初の1000文字のみ）
        page_content = str(soup)[:1000]
        self.logger.debug(f"Page content preview: {page_content}")
        
        # ページ内のリンク数を確認
        all_links = soup.find_all('a')
        self.logger.info(f"Total links found on page: {len(all_links)}")
        
        # docs.intel.com を含むリンクをチェック
        intel_docs_links = [link for link in all_links if link.get('href') and 'docs.intel.com' in link.get('href')]
        self.logger.info(f"Intel docs links found: {len(intel_docs_links)}")
        
        # /docs/programmable/ を含むリンクをチェック
        programmable_links = [link for link in all_links if link.get('href') and '/docs/programmable/' in link.get('href')]
        self.logger.info(f"Programmable docs links found: {len(programmable_links)}")
        
        documents = self._parse_altera_results(soup, search_url, seen_urls)
        return documents
    
    def _navigate_to_next_page_altera(self, driver, max_attempts: int, delay: int) -> bool:
        """次のページに移動（Altera用）"""
        # Intel/Alteraサイト用のページネーション戦略
        strategies = [
            self._try_altera_pagination_buttons,
            self._try_altera_load_more_buttons,
            self._try_altera_scroll_loading
        ]
        
        for strategy in strategies:
            try:
                if strategy(driver, max_attempts, delay):
                    return True
            except Exception as e:
                self.logger.warning(f"Altera navigation strategy failed: {e}")
                continue
        
        return False
    
    def _try_altera_pagination_buttons(self, driver, max_attempts: int, delay: int) -> bool:
        """Alteraページネーションボタンを試す"""
        pagination_selectors = [
            '.pagination-next',
            '.next-page',
            'a[aria-label*="next"]',
            'a[aria-label*="Next"]',
            'button[aria-label*="next"]',
            'button[aria-label*="Next"]',
            '.page-next',
            '[data-testid="next-page"]',
            'a[href*="page="]',
            'button[onclick*="next"]',
            # Intel固有のセレクター
            '.intel-pagination .next',
            '.docs-pagination .next',
            '.search-pagination .next'
        ]
        
        for selector in pagination_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # スクロールして要素を表示
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1)
                        
                        # クリック
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(delay)
                        
                        # 新しいページの読み込み待機
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        
                        self.logger.info(f"Successfully clicked Altera pagination button: {selector}")
                        return True
            except Exception:
                continue
        
        return False
    
    def _try_altera_load_more_buttons(self, driver, max_attempts: int, delay: int) -> bool:
        """Altera「もっと見る」ボタンを試す"""
        load_more_selectors = [
            'button[contains(text(), "Load More")]',
            'button[contains(text(), "Show More")]',
            'button[contains(text(), "More")]',
            '.load-more-btn',
            '.show-more-btn',
            '[data-testid="load-more"]',
            'button[aria-label*="more"]',
            'button[class*="load"]',
            'button[class*="more"]',
            'a[class*="load"]',
            'a[class*="more"]',
            # Intel固有のセレクター
            '.intel-load-more',
            '.docs-load-more',
            '.search-load-more'
        ]
        
        # XPathセレクターも試す
        xpath_selectors = [
            "//button[contains(text(), 'Load More')]",
            "//button[contains(text(), 'Show More')]",
            "//button[contains(text(), 'More')]",
            "//a[contains(text(), 'Load More')]",
            "//a[contains(text(), 'Show More')]",
            "//a[contains(text(), 'More')]"
        ]
        
        # CSS セレクターを試す
        for selector in load_more_selectors:
            try:
                if 'contains(text()' in selector:
                    continue  # XPathは後で処理
                    
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # スクロールして要素を表示
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1)
                        
                        # クリック
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(delay)
                        
                        # 新しいコンテンツの読み込み待機
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        
                        self.logger.info(f"Successfully clicked Altera load more button: {selector}")
                        return True
            except Exception:
                continue
        
        # XPath セレクターを試す
        for selector in xpath_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # スクロールして要素を表示
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1)
                        
                        # クリック
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(delay)
                        
                        # 新しいコンテンツの読み込み待機
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        
                        self.logger.info(f"Successfully clicked Altera load more button: {selector}")
                        return True
            except Exception:
                continue
        
        return False
    
    def _try_altera_scroll_loading(self, driver, max_attempts: int, delay: int) -> bool:
        """Alteraスクロールによる自動読み込みを試す"""
        initial_height = driver.execute_script("return document.body.scrollHeight")
        
        for attempt in range(max_attempts):
            try:
                # ページの最下部にスクロール
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(delay)
                
                # 新しいコンテンツの読み込み待機
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(2)  # 追加の待機時間
                
                # ページの高さが変わったかチェック
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height > initial_height:
                    self.logger.info(f"New content loaded by Altera scrolling (height: {initial_height} -> {new_height})")
                    return True
                else:
                    self.logger.info(f"No new content after Altera scrolling (attempt {attempt + 1}/{max_attempts})")
                    
            except Exception as e:
                self.logger.warning(f"Error during Altera scroll attempt {attempt + 1}: {e}")
                continue
        
        return False
    
    def _build_search_url(self) -> str:
        """設定から検索URLを構築"""
        base_url = self.config.get('base_url')
        search_params = self.config.get('search_params', {})
        
        # パラメータを構築
        params = []
        
        # クエリパラメータ
        query = search_params.get('query', 'DSP')
        params.append(f"q={query}")
        
        # ソートパラメータ
        sort = search_params.get('sort', 'Relevancy')
        params.append(f"s={sort}")
        
        # 完全なURLを構築
        full_url = f"{base_url}?{'&'.join(params)}"
        
        self.logger.info(f"Built search URL: {full_url}")
        return full_url
    
    def _is_excluded_title(self, title: str) -> bool:
        """特定のタイトルを除外するかどうかを判定"""
        if not title:
            return True
        
        title_lower = title.lower().strip()
        
        # 除外するタイトルのリスト
        excluded_titles = [
            'search results',
            'documentation home',
            'documentation',
            'home',
            'back',
            'next',
            'previous',
            'more',
            'load more',
            'show more',
            'view all',
            'see all',
            'all results',
            'search',
            'filter',
            'sort',
            'page',
            'results',
            'found',
            'matches',
            'items',
            '検索結果',
            'glossary',
            '用語集',
            # 企業・法的文書
            'modern slavery statement',
            'forced labor statement',
            '強制労働に関する声明',
            'uk tax strategy',
            '英国税務戦略',
            'tax strategy',
            'corporate governance',
            'investor relations',
            'privacy policy',
            'terms and conditions',
            'legal notice',
            'cookie policy'
        ]
        
        # 完全一致チェック
        if title_lower in excluded_titles:
            return True
        
        # 部分一致チェック（特定のパターンのみ）
        if title_lower == '包括的な用語' or title_lower == 'comprehensive terms':
            return True
        
        # URL風のタイトルを除外
        if title_lower.startswith(('http://', 'https://', 'www.')):
            return True
        
        # 空または非常に短いタイトルを除外
        if len(title_lower) <= 2:
            return True
        
        return False
    
    def _is_excluded_url(self, url: str) -> bool:
        """特定のURLを除外するかどうかを判定"""
        if not url:
            return True
        
        url_lower = url.lower()
        
        # 除外すべきURLパターン
        excluded_url_patterns = [
            # 法的・企業文書
            '/modern-slavery',
            '/forced-labor',
            '/tax-strategy',
            '/uk-tax',
            '/compliance',
            '/governance',
            '/investor',
            '/annual-report',
            '/sustainability',
            '/social-responsibility',
            '/csr',
            '/ethics',
            '/code-of-conduct',
            '/supplier-code',
            '/human-rights',
            '/diversity',
            '/environmental',
            '/carbon',
            # 一般的なサイト機能
            '/contact',
            '/about',
            '/careers',
            '/jobs',
            '/news',
            '/press',
            '/events',
            '/training',
            '/support',
            '/help',
            '/feedback',
            '/search',
            '/login',
            '/register',
            '/profile',
            '/account',
            '/settings',
            '/language',
            '/locale',
            # ナビゲーション
            '/sitemap',
            '/navigation',
            '/menu',
            '/breadcrumb',
            # プライバシー関連
            '/privacy',
            '/terms',
            '/legal',
            '/cookie',
            '/disclaimer',
            '/copyright'
        ]
        
        # URLパターンをチェック
        for pattern in excluded_url_patterns:
            if pattern in url_lower:
                return True
        
        # PDFやHTMLファイル以外のファイル形式を除外
        excluded_extensions = [
            '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            '.zip', '.tar', '.gz', '.xml', '.json', '.csv', '.txt'
        ]
        
        for ext in excluded_extensions:
            if url_lower.endswith(ext):
                return True
        
        # 短すぎるURLを除外
        if len(url) < 20:
            return True
        
        return False

    def _get_document_content(self, url: str, title: str) -> str:
        """
        ドキュメントのコンテンツを取得（高度なBot回避技術付き）
        
        403エラーやその他の問題が発生した場合は、タイトルから基本情報を生成
        """
        try:
            # 複数の方法でコンテンツ取得を試行
            content = None
            
            # 方法1: より人間らしいrequestsヘッダー
            content = self._try_requests_with_human_headers(url)
            if content and len(content.strip()) > 0:
                return content
                
            # 方法2: Seleniumを使用してJavaScript対応
            content = self._try_selenium_content_fetch(url)
            if content and len(content.strip()) > 0:
                return content
                
            # すべて失敗した場合はタイトルベースの内容を生成
            self.logger.warning(f"All content fetch methods failed for {url}, generating title-based content")
            return self._generate_content_from_title(title, url)
            
        except Exception as e:
            self.logger.error(f"Error getting content for {url}: {e}, using title-based content")
            return self._generate_content_from_title(title, url)
    
    def _try_requests_with_human_headers(self, url: str) -> str:
        """より人間らしいヘッダーでrequestsを試行（robots.txt準拠）"""
        try:
            # robots.txtに基づいた遅延設定
            if 'intel.com' in url:
                self.logger.info(f"Intel URL detected, applying 10s crawl delay per robots.txt")
                time.sleep(10)  # Intel robots.txtのCrawl-Delay: 10
            elif 'amd.com' in url:
                self.logger.info(f"AMD URL detected, applying 3s crawl delay")
                time.sleep(3)   # AMD向けに慎重な遅延
            
            # より詳細で人間らしいヘッダー
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                # リファラーを追加してより自然に見せる
                'Referer': 'https://www.google.com/'
            }
            
            # セッションを使用してcookieを管理
            session = requests.Session()
            session.headers.update(headers)
            
            # 段階的リトライ戦略
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Attempting content fetch for {url} (attempt {attempt + 1})")
                    response = session.get(url, timeout=20, allow_redirects=True)
                    
                    if response.status_code == 200:
                        break
                    elif response.status_code == 403:
                        self.logger.warning(f"403 Forbidden for {url} (attempt {attempt + 1})")
                        return ""
                    elif response.status_code in [429, 503]:  # Rate limit
                        wait_time = 15 * (attempt + 1)
                        self.logger.warning(f"Rate limited ({response.status_code}) for {url}, waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        self.logger.warning(f"HTTP {response.status_code} for {url} (attempt {attempt + 1})")
                        if attempt == max_retries - 1:
                            return ""
                        time.sleep(5)
                        
                except requests.exceptions.Timeout:
                    self.logger.warning(f"Timeout for {url} (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                    continue
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Request failed for {url} (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                    continue
            else:
                # すべての試行が失敗
                return ""
            
            # BeautifulSoupでHTMLを解析
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ページタイトルを取得
            page_title = soup.find('title')
            title_text = page_title.get_text().strip() if page_title else ""
            
            # メタ説明を取得
            meta_description = ""
            try:
                meta_tag = soup.find('meta', attrs={'name': 'description'})
                if meta_tag:
                    meta_description = str(meta_tag.get('content', '')) if hasattr(meta_tag, 'get') else ""
            except:
                meta_description = ""
            
            # 主要コンテンツを抽出（Intel/AMD特有の構造に対応）
            content_parts = []
            
            if title_text:
                content_parts.append(f"Page Title: {title_text}")
            if meta_description:
                content_parts.append(f"Description: {meta_description}")
                
            # より具体的なコンテンツセレクター
            content_selectors = [
                # Intel/AMD固有のコンテンツエリア
                'main', 'article', '.content', '#content', '#main-content',
                '.document-content', '.doc-content', '.main-content',
                '[role="main"]', '.documentation-content', '.page-content',
                # Intel特有のセレクター
                '.doc-wrapper', '.documentation-wrapper', '.content-wrapper'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    self.logger.info(f"Found main content using selector: {selector}")
                    break
            
            if main_content:
                # メインコンテンツから段落を抽出
                for tag in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li'], text=True):
                    text = tag.get_text(strip=True)
                    if text and len(text) > 30:  # 十分な長さのテキストのみ
                        content_parts.append(text)
                        if len(content_parts) > 20:  # 最大20セクション
                            break
            else:
                # フォールバック：全体から段落を抽出
                for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'div'], text=True):
                    text = tag.get_text(strip=True)
                    if text and len(text) > 30:
                        content_parts.append(text)
                        if len(content_parts) > 15:
                            break
            
            content = '\n'.join(content_parts)
            
            # 最大長を制限
            if len(content) > 8000:
                content = content[:8000] + "..."
                
            return content if len(content.strip()) > 100 else ""
            
        except Exception as e:
            self.logger.warning(f"Advanced requests failed for {url}: {e}")
            return ""
    
    def _try_selenium_content_fetch(self, url: str) -> str:
        """Seleniumを使用してJavaScript対応でコンテンツを取得"""
        driver = None
        try:
            # 既存のWebDriverを再利用または新規作成
            driver = self._create_webdriver()
            
            # より人間らしい動作
            driver.implicitly_wait(3)
            driver.get(url)
            time.sleep(5)  # ページの完全な読み込みを待機
            
            # JavaScriptの実行完了を待機
            driver.execute_script("return document.readyState") == "complete"
            
            # ページタイトルを取得
            page_title = driver.title
            
            # ページソースを取得してBeautifulSoupで解析
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # メタ説明を取得
            meta_description = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_description = meta_tag.get('content', '')
            
            # 主要コンテンツを抽出
            content_parts = []
            
            if page_title:
                content_parts.append(f"Page Title: {page_title}")
            if meta_description:
                content_parts.append(f"Description: {meta_description}")
                
            # プライバシーポリシーページを検出
            if self._is_privacy_or_policy_page(page_title, soup):
                self.logger.warning(f"Detected privacy/policy page, skipping content extraction for {url}")
                return ""
                
            # 主要なテキストコンテンツを抽出
            for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'div'], text=True):
                text = tag.get_text(strip=True)
                if text and len(text) > 30:
                    # プライバシーポリシー関連のコンテンツを除外
                    if self._is_privacy_related_content(text):
                        continue
                    # FPGAに関連しないコンテンツを除外
                    if not self._is_technical_content(text):
                        continue
                    content_parts.append(text)
                    if len(content_parts) > 15:
                        break
            
            content = '\n'.join(content_parts)
            
            # 最大長を制限
            if len(content) > 8000:
                content = content[:8000] + "..."
                
            return content if len(content.strip()) > 100 else ""
            
        except Exception as e:
            self.logger.warning(f"Selenium content fetch failed for {url}: {e}")
            return ""
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _generate_content_from_title(self, title: str, url: str) -> str:
        """
        タイトルとURLから詳細なコンテンツを生成
        スクレイピングが失敗した場合のフォールバック（強化版）
        """
        try:
            # 新しいフォールバック生成器を使用
            return self.content_fallback.generate_content_from_title(
                title=title,
                url=url,
                source="Intel/Altera Documentation"
            )
        except Exception as e:
            self.logger.warning(f"Fallback content generation failed: {e}, using basic fallback")
            # 基本的なフォールバック
            return f"""Title: {title}
URL: {url}
Source: Intel/Altera Documentation

Document Type: Technical Documentation
Category: Intel FPGA Documentation
Description: Technical documentation from Intel's FPGA and programmable device portfolio.

Note: Content could not be retrieved due to access restrictions.
This document likely contains technical specifications, implementation guidelines, 
and best practices for Intel FPGA technologies."""
    
    def _is_privacy_or_policy_page(self, page_title: str, soup) -> bool:
        """ページがプライバシーポリシーや企業ポリシーページかどうかを判定"""
        title_lower = page_title.lower() if page_title else ""
        
        # プライバシー関連のページタイトルパターン
        privacy_patterns = [
            'privacy policy', 'cookie policy', 'data policy', 'consent',
            'terms and conditions', 'legal notice', 'legal information',
            'modern slavery', 'forced labor', 'tax strategy', 'governance',
            'プライバシーポリシー', 'クッキーポリシー', 'データポリシー',
            '利用規約', '法的告知', '企業統治'
        ]
        
        # タイトルチェック
        for pattern in privacy_patterns:
            if pattern in title_lower:
                return True
                
        # ページ内容からも判定
        page_text = soup.get_text().lower() if soup else ""
        privacy_indicators = [
            'this website uses cookies', 'we use cookies',
            'privacy policy', 'cookie consent',
            'personal data', 'data processing',
            'デバイス所有者', 'intel体験', '広告パートナー',
            'website experience', 'functional cookies'
        ]
        
        privacy_count = sum(1 for indicator in privacy_indicators if indicator in page_text)
        return privacy_count >= 3  # 3つ以上の指標がある場合はプライバシーページと判定
    
    def _is_privacy_related_content(self, text: str) -> bool:
        """テキストがプライバシー関連のコンテンツかどうかを判定"""
        text_lower = text.lower()
        
        privacy_keywords = [
            'privacy', 'cookie', 'consent', 'data collection', 'personal information',
            'website uses cookies', 'デバイス所有者', 'intel体験', '広告パートナー',
            'functional technologies', 'performance technologies', 'advertising technologies',
            'device owners', 'website experience', 'enhanced functionality',
            'third party providers', 'unique device identifiers'
        ]
        
        return any(keyword in text_lower for keyword in privacy_keywords)
    
    def _is_technical_content(self, text: str) -> bool:
        """テキストが技術的なコンテンツかどうかを判定"""
        text_lower = text.lower()
        
        # 技術的なキーワード
        technical_keywords = [
            'fpga', 'processor', 'architecture', 'instruction', 'memory',
            'dsp', 'signal processing', 'algorithm', 'implementation',
            'configuration', 'register', 'interface', 'protocol',
            'performance', 'optimization', 'design', 'system',
            'hardware', 'software', 'embedded', 'real-time',
            'nios', 'stratix', 'arria', 'cyclone', 'agilex',
            'risc-v', 'core', 'cache', 'pipeline', 'interrupt',
            'debug', 'trace', 'compiler', 'toolchain'
        ]
        
        # 長いテキストであれば、技術キーワードが含まれている可能性が高い
        if len(text) > 100:
            return any(keyword in text_lower for keyword in technical_keywords)
        
        # 短いテキストの場合はより厳密にチェック
        return sum(1 for keyword in technical_keywords if keyword in text_lower) >= 1
