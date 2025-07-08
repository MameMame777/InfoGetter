import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
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


class XilinxScraper(BaseScraper):
    """Xilinx (AMD) ドキュメントサイトのスクレイパー"""
    
    def get_source_type(self) -> DataSourceType:
        return DataSourceType.WEB_SCRAPING
    
    def scrape_documents(self) -> List[Document]:
        """Xilinxのドキュメントをスクレイピング（Seleniumのみ）"""
        self.logger.info("Starting Xilinx document scraping with Selenium")
        
        # Seleniumで直接スクレイピング
        documents = self._scrape_with_selenium()
        
        return self.validate_data(documents)
    
    def _scrape_with_selenium(self) -> List[Document]:
        """Seleniumでスクレイピング"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # User-Agentを設定
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            url = self._build_search_url()
            self.logger.info(f"Accessing Xilinx search URL: {url}")
            driver.get(url)
            
            # ページが完全に読み込まれるまで待機
            page_timeout = self.config.get('page_load_timeout', 30)
            WebDriverWait(driver, page_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 検索結果の読み込み待機
            time.sleep(5)
            
            # ページのタイトルとURLを確認
            self.logger.info(f"Page title: {driver.title}")
            self.logger.info(f"Current URL: {driver.current_url}")
            
            # スクロールして追加の結果を読み込む
            documents = self._scroll_and_extract_documents(driver, url)
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Selenium scraping error: {e}")
            return []
        finally:
            driver.quit()
    
    def _scroll_and_extract_documents(self, driver, search_url: str) -> List[Document]:
        """スクロールしながらドキュメントを抽出"""
        documents = []
        seen_urls = set()  # 重複チェック用のセット
        max_results = self.config.get('max_results', 200)
        scroll_pages = self.config.get('scroll_pages', 10)
        load_more_attempts = self.config.get('load_more_attempts', 5)
        scroll_delay = self.config.get('scroll_delay', 2)
        
        self.logger.info(f"Starting document extraction with max_results={max_results}, scroll_pages={scroll_pages}")
        
        # 初期ページを解析
        initial_documents = self._extract_current_page(driver, search_url, seen_urls)
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
            success = self._navigate_to_next_page(driver, load_more_attempts, scroll_delay)
            if not success:
                self.logger.warning("Failed to navigate to next page")
                break
            
            # 現在のページからドキュメントを取得
            page_documents = self._extract_current_page(driver, search_url, seen_urls)
            
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
    
    def _try_load_more_content(self, driver, max_attempts: int, delay: int) -> bool:
        """コンテンツの追加読み込みを試行"""
        
        # 現在のページの高さを記録
        initial_height = driver.execute_script("return document.body.scrollHeight")
        
        for attempt in range(max_attempts):
            try:
                # 「もっと見る」ボタンを探してクリック
                load_more_selectors = [
                    'button[contains(text(), "Load More")]',
                    'button[contains(text(), "Show More")]',
                    'a[contains(text(), "Next")]',
                    '.load-more-btn',
                    '.show-more-btn',
                    '.pagination-next',
                    '[data-testid="load-more"]',
                    'button[aria-label*="more"]',
                    'button[class*="load"]',
                    'button[class*="more"]'
                ]
                
                clicked = False
                for selector in load_more_selectors:
                    try:
                        if 'contains(text()' in selector:
                            # XPathを使用してテキストを含む要素を見つける
                            text = selector.split('contains(text(), "')[1].split('")')[0]
                            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for element in elements:
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    # スクロールして要素を表示
                                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    time.sleep(1)
                                    
                                    # クリック
                                    driver.execute_script("arguments[0].click();", element)
                                    clicked = True
                                    self.logger.info(f"Clicked load more button: {selector}")
                                    break
                            except Exception:
                                continue
                        
                        if clicked:
                            break
                            
                    except Exception:
                        continue
                
                if clicked:
                    # ボタンクリック後の待機
                    time.sleep(delay)
                    
                    # 新しいコンテンツの読み込み確認
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    
                    # ページの高さが変わったかチェック
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height > initial_height:
                        self.logger.info(f"New content loaded (height: {initial_height} -> {new_height})")
                        return True
                    else:
                        self.logger.info("No new content after button click")
                        continue
                
                # ボタンが見つからない場合はスクロール
                self.logger.info(f"No load more button found, scrolling (attempt {attempt + 1}/{max_attempts})")
                
                # ページの最下部にスクロール
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(delay)
                
                # 新しいコンテンツの読み込み待機
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(2)
                
                # ページの高さが変わったかチェック
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height > initial_height:
                    self.logger.info(f"New content loaded by scrolling (height: {initial_height} -> {new_height})")
                    return True
                else:
                    self.logger.info("No new content after scrolling")
                    
            except Exception as e:
                self.logger.warning(f"Error during load more attempt {attempt + 1}: {e}")
                continue
        
        self.logger.info("All load more attempts failed")
        return False
    
    def _extract_current_page(self, driver, search_url: str, seen_urls: set) -> List[Document]:
        """現在のページからドキュメントを抽出"""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # デバッグ用：ページのHTMLをログに出力（最初の1000文字のみ）
        page_content = str(soup)[:1000]
        self.logger.debug(f"Page content preview: {page_content}")
        
        # ページ内のリンク数を確認
        all_links = soup.find_all('a')
        self.logger.info(f"Total links found on page: {len(all_links)}")
        
        # docs.amd.com を含むリンクをチェック
        amd_docs_links = [link for link in all_links if link.get('href') and 'docs.amd.com' in link.get('href')]
        self.logger.info(f"AMD docs links found: {len(amd_docs_links)}")
        
        # docs.xilinx.com を含むリンクをチェック
        xilinx_docs_links = [link for link in all_links if link.get('href') and 'docs.xilinx.com' in link.get('href')]
        self.logger.info(f"Xilinx docs links found: {len(xilinx_docs_links)}")
        
        documents = self._parse_xilinx_results(soup, search_url, seen_urls)
        return documents
    
    def _navigate_to_next_page(self, driver, max_attempts: int, delay: int) -> bool:
        """次のページに移動"""
        # 複数の戦略を試す
        strategies = [
            self._try_pagination_buttons,
            self._try_load_more_buttons,
            self._try_scroll_loading
        ]
        
        for strategy in strategies:
            try:
                if strategy(driver, max_attempts, delay):
                    return True
            except Exception as e:
                self.logger.warning(f"Navigation strategy failed: {e}")
                continue
        
        return False
    
    def _try_pagination_buttons(self, driver, max_attempts: int, delay: int) -> bool:
        """ページネーションボタンを試す"""
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
            'button[onclick*="next"]'
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
                        
                        self.logger.info(f"Successfully clicked pagination button: {selector}")
                        return True
            except Exception:
                continue
        
        return False
    
    def _try_load_more_buttons(self, driver, max_attempts: int, delay: int) -> bool:
        """「もっと見る」ボタンを試す"""
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
            'a[class*="more"]'
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
                        
                        self.logger.info(f"Successfully clicked load more button: {selector}")
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
                        
                        self.logger.info(f"Successfully clicked load more button: {selector}")
                        return True
            except Exception:
                continue
        
        return False
    
    def _try_scroll_loading(self, driver, max_attempts: int, delay: int) -> bool:
        """スクロールによる自動読み込みを試す"""
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
                    self.logger.info(f"New content loaded by scrolling (height: {initial_height} -> {new_height})")
                    return True
                else:
                    self.logger.info(f"No new content after scrolling (attempt {attempt + 1}/{max_attempts})")
                    
            except Exception as e:
                self.logger.warning(f"Error during scroll attempt {attempt + 1}: {e}")
                continue
        
        return False
    
    def _parse_xilinx_results(self, soup: BeautifulSoup, search_url: str, seen_urls: set = None) -> List[Document]:
        """Xilinxの検索結果をパース"""
        documents = []
        if seen_urls is None:
            seen_urls = set()
        
        # AMD/Xilinxサイトの構造に合わせて調整
        # より具体的なセレクターを使用
        link_selectors = [
            # 検索結果の構造
            '.search-result-item a',
            '.result-item a',
            '.document-item a',
            '.search-result a',
            # ドキュメントリンクの特定
            'a[href*="pdf"]',
            'a[href*="doc"]',
            'a[href*="guide"]',
            'a[href*="manual"]',
            'a[href*="datasheet"]',
            # タイトルベースの検索
            'a[title*="PDF"]',
            'a[title*="Document"]',
            'a[title*="Guide"]',
            'a[title*="Manual"]',
            'a[title*="Data Sheet"]',
            # 一般的なリンク
            '.document-link',
            'div[class*="search"] a',
            'div[class*="result"] a'
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
        
        self.logger.info(f"Found {len(documents)} documents from Xilinx using URL: {search_url}")
        return documents
    
    def _extract_fpga_series(self, text: str) -> str:
        """テキストからFPGAシリーズを抽出"""
        text_lower = text.lower()
        
        series_patterns = {
            'versal': r'versal',
            'zynq': r'zynq',
            'artix': r'artix',
            'kintex': r'kintex',
            'virtex': r'virtex',
            'spartan': r'spartan'
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
            'fpga', 'ip core', 'dsp', 'versal', 'zynq', 'artix', 'kintex', 'virtex', 'spartan',
            'adaptive soc', 'acap', 'vivado', 'vitis', 'hls', 'xilinx', 'programmable logic',
            'reconfigurable', 'hardware acceleration', 'ai engine', 'noc', 'processing system',
            'programmable logic', 'clock', 'memory', 'interface', 'protocol', 'ethernet',
            'pcie', 'ddr', 'axi', 'avalon', 'hdl', 'verilog', 'vhdl'
        ]
        
        # 除外キーワード
        exclude_keywords = [
            'privacy', 'legal', 'terms', 'conditions', 'policy', 'statement', 'corporate',
            'investor', 'financial', 'annual report', 'press release', 'news', 'career',
            'job', 'marketing', 'sales', 'contact', 'support'
        ]
        
        # 除外キーワードがある場合は除外
        for keyword in exclude_keywords:
            if keyword in text_lower:
                return False
        
        # FPGA関連キーワードがある場合は含める
        for keyword in fpga_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def _build_search_url(self) -> str:
        """設定から検索URLを構築"""
        base_url = self.config.get('base_url')
        search_params = self.config.get('search_params', {})
        
        # パラメータを構築
        params = []
        
        # クエリパラメータ
        query = search_params.get('query', 'Versal')
        params.append(f"query={query}")
        
        # ドキュメントタイプとプロダクトタイプを組み合わせた value-filters
        doc_types = search_params.get('document_types', ['Data Sheet', 'User Guides & Manuals'])
        prod_types = search_params.get('product_types', ['IP Cores (Adaptive SoC & FPGA)'])
        
        # URLエンコーディング
        import urllib.parse
        doc_types_encoded = []
        for doc_type in doc_types:
            doc_types_encoded.append(urllib.parse.quote(f'"{doc_type}"'))
        
        prod_types_encoded = []
        for prod_type in prod_types:
            prod_types_encoded.append(urllib.parse.quote(f'"{prod_type}"'))
        
        # value-filtersの構築
        value_filters = f"Document_Type_custom~{'_'.join(doc_types_encoded)}*Product_custom~{'_'.join(prod_types_encoded)}"
        params.append(f"value-filters={value_filters}")
        
        # 日付フィルター
        date_filter = search_params.get('date_filter', 'last_month')
        params.append(f"date-filters=ft%253AlastEdition~{date_filter}")
        
        # コンテンツ言語
        content_lang = search_params.get('content_lang', 'en-US')
        params.append(f"content-lang={content_lang}")
        
        # 完全なURLを構築
        full_url = f"{base_url}?{'&'.join(params)}"
        
        self.logger.info(f"Built search URL: {full_url}")
        return full_url
    
