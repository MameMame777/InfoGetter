from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum


class DataSourceType(Enum):
    WEB_SCRAPING = "web_scraping"
    REST_API = "rest_api"
    RSS_FEED = "rss_feed"


class Document(BaseModel):
    name: str
    url: HttpUrl
    source: str
    source_type: DataSourceType
    search_url: Optional[str] = None  # 検索に使用したURL
    category: Optional[str] = None
    fpga_series: Optional[str] = None
    last_updated: Optional[datetime] = None
    file_type: Optional[str] = None
    scraped_at: datetime
    hash: str
    
    # API固有の追加フィールド
    api_metadata: Optional[dict] = None
    
    def to_dict(self) -> dict:
        """JSONシリアライズ用の辞書を作成（不要なフィールドを除外）"""
        return {
            "name": self.name,
            "url": str(self.url),
            "source": self.source,
            "source_type": str(self.source_type),
            "search_url": self.search_url,
            "category": self.category,
            "file_type": self.file_type,
            "api_metadata": self.api_metadata
        }
