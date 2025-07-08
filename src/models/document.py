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
