#!/usr/bin/env python3
"""
Sitemap Parser
==============

Automatically fetches and parses sitemap.xml from your website
and extracts URLs for Google Ads page feeds.
"""

import os
import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)

class SitemapParser:
    """Parses sitemap.xml and extracts URLs for Google Ads page feeds."""
    
    def __init__(self, base_url: str = "https://levine.realestate"):
        self.base_url = base_url
        self.sitemap_url = f"{base_url}/sitemap.xml"
        self.cache_file = "data/sitemap_cache.json"
        self.cache_duration_hours = 24  # Cache for 24 hours
        
        # URL exclusions (from your existing configuration)
        self.excluded_patterns = [
            "/sitemap/*",
            "/blog/*", 
            "/privacy/*",
            "/contact/*",
            "/terms/*",
            "/about/*",
            "/admin/*",
            "/wp-admin/*",
            "/wp-content/*",
            "/wp-includes/*",
            "/.well-known/*",
            "/robots.txt",
            "/favicon.ico"
        ]
        
        # URL inclusion patterns (prioritize these)
        self.priority_patterns = [
            "/property/",
            "/communities/",
            "/deer-valley",
            "/park-city",
            "/promontory",
            "/search/",
            "/listings/"
        ]
        
        self.load_cache()
    
    def load_cache(self):
        """Load cached sitemap data if available and not expired."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                cache_time = datetime.fromisoformat(cache_data.get('cached_at', '1970-01-01'))
                if datetime.now() - cache_time < timedelta(hours=self.cache_duration_hours):
                    self.cached_urls = cache_data.get('urls', [])
                    self.cached_lastmod = cache_data.get('lastmod', None)
                    logger.info(f"✅ Loaded {len(self.cached_urls)} URLs from cache")
                    return True
            except Exception as e:
                logger.warning(f"⚠️ Failed to load cache: {e}")
        
        self.cached_urls = []
        self.cached_lastmod = None
        return False
    
    def save_cache(self, urls: List[Dict], lastmod: Optional[str] = None):
        """Save sitemap data to cache."""
        os.makedirs('data', exist_ok=True)
        cache_data = {
            'urls': urls,
            'lastmod': lastmod,
            'cached_at': datetime.now().isoformat(),
            'total_urls': len(urls)
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        logger.info(f"💾 Cached {len(urls)} URLs")
    
    def fetch_sitemap(self) -> Optional[str]:
        """Fetch sitemap.xml from the website."""
        try:
            logger.info(f"🌐 Fetching sitemap from: {self.sitemap_url}")
            response = requests.get(self.sitemap_url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"✅ Successfully fetched sitemap ({len(response.content)} bytes)")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to fetch sitemap: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching sitemap: {e}")
            return None
    
    def parse_sitemap(self, sitemap_content: str) -> List[Dict]:
        """Parse sitemap XML content and extract URLs."""
        try:
            root = ET.fromstring(sitemap_content)
            
            # Handle different sitemap namespaces
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'sitemapindex': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            urls = []
            
            # Check if this is a sitemap index (contains multiple sitemaps)
            if root.tag.endswith('sitemapindex'):
                logger.info("📋 Found sitemap index, fetching individual sitemaps...")
                for sitemap in root.findall('.//sitemap:sitemap', namespaces):
                    loc_elem = sitemap.find('sitemap:loc', namespaces)
                    if loc_elem is not None:
                        sitemap_url = loc_elem.text
                        logger.info(f"🔄 Fetching sub-sitemap: {sitemap_url}")
                        
                        # Fetch and parse sub-sitemap
                        try:
                            sub_response = requests.get(sitemap_url, timeout=30)
                            sub_response.raise_for_status()
                            sub_urls = self.parse_sitemap(sub_response.text)
                            urls.extend(sub_urls)
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to fetch sub-sitemap {sitemap_url}: {e}")
            
            # Parse individual URLs
            for url_elem in root.findall('.//sitemap:url', namespaces):
                url_data = self.extract_url_data(url_elem, namespaces)
                if url_data:
                    urls.append(url_data)
            
            logger.info(f"📊 Parsed {len(urls)} URLs from sitemap")
            return urls
            
        except ET.ParseError as e:
            logger.error(f"❌ Failed to parse sitemap XML: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error parsing sitemap: {e}")
            return []
    
    def extract_url_data(self, url_elem, namespaces: Dict) -> Optional[Dict]:
        """Extract data from a single URL element."""
        try:
            loc_elem = url_elem.find('sitemap:loc', namespaces)
            if loc_elem is None:
                return None
            
            url = loc_elem.text.strip()
            
            # Extract optional fields
            lastmod_elem = url_elem.find('sitemap:lastmod', namespaces)
            lastmod = lastmod_elem.text if lastmod_elem is not None else None
            
            changefreq_elem = url_elem.find('sitemap:changefreq', namespaces)
            changefreq = changefreq_elem.text if changefreq_elem is not None else None
            
            priority_elem = url_elem.find('sitemap:priority', namespaces)
            priority = float(priority_elem.text) if priority_elem is not None else 0.5
            
            return {
                'url': url,
                'lastmod': lastmod,
                'changefreq': changefreq,
                'priority': priority,
                'domain': urlparse(url).netloc,
                'path': urlparse(url).path
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract URL data: {e}")
            return None
    
    def filter_urls(self, urls: List[Dict]) -> List[Dict]:
        """Filter URLs based on inclusion/exclusion patterns."""
        filtered_urls = []
        
        for url_data in urls:
            url = url_data['url']
            path = url_data['path']
            
            # Skip if URL doesn't match our domain
            if not url.startswith(self.base_url):
                continue
            
            # Skip excluded patterns
            if self.is_excluded(path):
                continue
            
            # Add priority score based on patterns
            url_data['priority_score'] = self.calculate_priority_score(path)
            filtered_urls.append(url_data)
        
        # Sort by priority score (highest first)
        filtered_urls.sort(key=lambda x: x['priority_score'], reverse=True)
        
        logger.info(f"🔍 Filtered to {len(filtered_urls)} relevant URLs")
        return filtered_urls
    
    def is_excluded(self, path: str) -> bool:
        """Check if a path should be excluded."""
        for pattern in self.excluded_patterns:
            # Convert pattern to regex-like matching
            if pattern.endswith('/*'):
                prefix = pattern[:-2]
                if path.startswith(prefix):
                    return True
            elif pattern in path:
                return True
        
        return False
    
    def calculate_priority_score(self, path: str) -> float:
        """Calculate priority score for URL based on patterns."""
        score = 0.0
        
        # Base score from sitemap priority
        # (will be added when we have the sitemap data)
        
        # Bonus for priority patterns
        for pattern in self.priority_patterns:
            if pattern in path:
                score += 1.0
        
        # Bonus for property-related content
        if '/property/' in path:
            score += 2.0
        elif '/communities/' in path:
            score += 1.5
        elif any(community in path for community in ['deer-valley', 'park-city', 'promontory']):
            score += 1.5
        
        # Penalty for generic pages
        if path in ['/', '/home', '/index']:
            score += 0.5
        
        return score
    
    def get_page_feed_urls(self, max_urls: int = 1000) -> List[Dict]:
        """Get URLs suitable for Google Ads page feeds."""
        # Try cache first
        if self.cached_urls and not self.is_cache_expired():
            logger.info("📋 Using cached URLs")
            return self.cached_urls[:max_urls]
        
        # Fetch fresh sitemap
        sitemap_content = self.fetch_sitemap()
        if not sitemap_content:
            logger.error("❌ Failed to fetch sitemap, using cached data if available")
            return self.cached_urls[:max_urls] if self.cached_urls else []
        
        # Parse and filter URLs
        all_urls = self.parse_sitemap(sitemap_content)
        filtered_urls = self.filter_urls(all_urls)
        
        # Limit to max_urls
        page_feed_urls = filtered_urls[:max_urls]
        
        # Cache the results
        self.save_cache(page_feed_urls)
        
        logger.info(f"🎯 Generated {len(page_feed_urls)} URLs for page feed")
        return page_feed_urls
    
    def is_cache_expired(self) -> bool:
        """Check if cache is expired."""
        if not os.path.exists(self.cache_file):
            return True
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cache_data.get('cached_at', '1970-01-01'))
            return datetime.now() - cache_time >= timedelta(hours=self.cache_duration_hours)
        except:
            return True
    
    def get_url_statistics(self, urls: List[Dict]) -> Dict:
        """Get statistics about the URLs."""
        if not urls:
            return {}
        
        stats = {
            'total_urls': len(urls),
            'domains': set(),
            'path_patterns': {},
            'priority_distribution': {},
            'lastmod_distribution': {}
        }
        
        for url_data in urls:
            # Domain stats
            stats['domains'].add(url_data['domain'])
            
            # Path pattern stats
            path = url_data['path']
            if '/' in path:
                pattern = '/' + path.split('/')[1] + '/'
                stats['path_patterns'][pattern] = stats['path_patterns'].get(pattern, 0) + 1
            
            # Priority stats
            priority = url_data.get('priority_score', 0)
            priority_range = f"{int(priority)}-{int(priority)+1}"
            stats['priority_distribution'][priority_range] = stats['priority_distribution'].get(priority_range, 0) + 1
            
            # Lastmod stats
            lastmod = url_data.get('lastmod', 'Unknown')
            if lastmod != 'Unknown':
                try:
                    mod_date = datetime.fromisoformat(lastmod.replace('Z', '+00:00'))
                    year_month = mod_date.strftime('%Y-%m')
                    stats['lastmod_distribution'][year_month] = stats['lastmod_distribution'].get(year_month, 0) + 1
                except:
                    pass
        
        # Convert sets to counts
        stats['unique_domains'] = len(stats['domains'])
        stats['domains'] = list(stats['domains'])
        
        return stats

def test_sitemap_parser():
    """Test the sitemap parser functionality."""
    print("🗺️ Testing Sitemap Parser")
    print("=" * 50)
    
    parser = SitemapParser()
    
    # Get URLs for page feed
    urls = parser.get_page_feed_urls(max_urls=50)
    
    if urls:
        print(f"✅ Successfully extracted {len(urls)} URLs")
        
        # Show top URLs by priority
        print(f"\n🎯 Top 10 URLs by Priority:")
        for i, url_data in enumerate(urls[:10], 1):
            print(f"  {i:2d}. {url_data['url']} (Score: {url_data['priority_score']:.1f})")
        
        # Show statistics
        stats = parser.get_url_statistics(urls)
        print(f"\n📊 URL Statistics:")
        print(f"  Total URLs: {stats.get('total_urls', 0)}")
        print(f"  Unique Domains: {stats.get('unique_domains', 0)}")
        print(f"  Top Path Patterns:")
        for pattern, count in sorted(stats.get('path_patterns', {}).items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {pattern}: {count} URLs")
    else:
        print("❌ No URLs extracted")

if __name__ == '__main__':
    test_sitemap_parser()
