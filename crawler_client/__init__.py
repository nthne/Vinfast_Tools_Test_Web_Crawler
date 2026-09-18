"""Crawler data access adapters."""

from .file_client import FileCrawlerClient
from .mapper import CrawlerPageMapper
from .schemas import CrawledPage

__all__ = ["CrawledPage", "CrawlerPageMapper", "FileCrawlerClient"]
