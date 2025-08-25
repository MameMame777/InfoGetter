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

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.scrapers.base_scraper import BaseScraper
from src.models.document import Document, DataSourceType


class AlteraScraper(BaseScraper):
    """Altera (Intel) ドキュメントサイトのスクレイパー"""
    
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
                    
                    doc = self._create_document(
                        name=title,
                        url=full_url,
                        category=category,
                        fpga_series=fpga_series,
                        file_type=file_type,
                        search_url=search_url  # 検索URLを追加
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
