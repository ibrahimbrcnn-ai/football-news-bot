import feedparser
import json
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import re
from news_filter import FootballNewsFilter
from translation_manager import TranslationManager
from x_automation_bot import XAutomationBot
import logging
import os

class FootballNewsAggregator:
    def __init__(self):
        self.filter = FootballNewsFilter()
        self.translator = TranslationManager()
        self.sources_file = 'global_football_sources.json'
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('football_news.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load sources
        self.sources = self.load_sources()
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        })
        
    def load_sources(self):
        """Load RSS sources from JSON file"""
        try:
            with open(self.sources_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load sources: {e}")
            return {}
    
    def extract_image_from_content(self, content, base_url):
        """Extract first image URL from HTML content"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for images in common news article patterns
            img_selectors = [
                'img.featured-image',
                'img.article-image', 
                'img.lead-image',
                '.article-content img',
                '.news-content img',
                'img[data-src]',
                'img[src]'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img:
                    img_url = img.get('data-src') or img.get('src')
                    if img_url:
                        # Convert relative URLs to absolute
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = urljoin(base_url, img_url)
                        
                        # Validate image URL
                        if self._is_valid_image_url(img_url):
                            return img_url
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Image extraction failed: {e}")
            return None
    
    def _is_valid_image_url(self, url):
        """Check if URL points to a valid image"""
        try:
            # Check file extension
            parsed = urlparse(url)
            path = parsed.path.lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
            
            if any(path.endswith(ext) for ext in valid_extensions):
                return True
            
            # Check content-type if no extension
            try:
                response = self.session.head(url, timeout=5)
                content_type = response.headers.get('content-type', '').lower()
                return content_type.startswith('image/')
            except:
                return False
                
        except:
            return False
    
    def fetch_rss_feed(self, feed_url, source_info):
        """Fetch and parse RSS feed"""
        try:
            self.logger.info(f"Fetching RSS: {source_info['name']}")
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                self.logger.warning(f"RSS parsing issues for {source_info['name']}: {feed.bozo_exception}")
            
            news_items = []
            
            for entry in feed.entries[:15]:  # Process max 15 items per source
                try:
                    # Extract basic info
                    title = entry.get('title', '').strip()
                    summary = entry.get('summary', entry.get('description', '')).strip()
                    url = entry.get('link', '')
                    
                    # Skip if missing essential data
                    if not title or not url:
                        continue
                    
                    # Clean HTML from summary
                    if summary:
                        summary = BeautifulSoup(summary, 'html.parser').get_text().strip()
                        summary = re.sub(r'\s+', ' ', summary)[:300]  # Limit length
                    
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()  # Fallback to now
                    
                    # Skip old news (older than 24 hours)
                    if datetime.now() - pub_date > timedelta(hours=24):
                        continue
                    
                    # Extract image
                    image_url = None
                    
                    # Try to get image from RSS enclosure
                    if hasattr(entry, 'enclosures') and entry.enclosures:
                        for enclosure in entry.enclosures:
                            if hasattr(enclosure, 'type') and enclosure.type.startswith('image/'):
                                image_url = enclosure.href
                                break
                    
                    # Try to get image from content
                    if not image_url and hasattr(entry, 'content'):
                        for content in entry.content:
                            image_url = self.extract_image_from_content(content.value, url)
                            if image_url:
                                break
                    
                    # Try to get image from summary
                    if not image_url and summary:
                        image_url = self.extract_image_from_content(summary, url)
                    
                    # Create news item
                    news_item = {
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'image_url': image_url,
                        'published': pub_date.isoformat(),
                        'source': source_info['name'],
                        'source_priority': source_info.get('priority', 5),
                        'region': source_info.get('region', 'global'),
                        'language': source_info.get('language', 'english'),
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    news_items.append(news_item)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing entry from {source_info['name']}: {e}")
                    continue
            
            self.logger.info(f"Fetched {len(news_items)} items from {source_info['name']}")
            return news_items
            
        except Exception as e:
            self.logger.error(f"Failed to fetch RSS {source_info['name']}: {e}")
            return []
    
    def fetch_all_news(self):
        """Fetch news from all sources"""
        all_news = []
        
        # Fetch English sources
        for category, sources in self.sources.get('english_sources', {}).items():
            for source in sources:
                news_items = self.fetch_rss_feed(source['rss'], source)
                all_news.extend(news_items)
                
                # Rate limiting
                time.sleep(random.uniform(2, 5))
        
        # Fetch Turkish sources
        for source in self.sources.get('turkish_sources', []):
            news_items = self.fetch_rss_feed(source['rss'], source)
            all_news.extend(news_items)
            time.sleep(random.uniform(2, 5))
        
        # Fetch regional sources
        for region, sources in self.sources.get('regional_sources', {}).items():
            for source in sources:
                news_items = self.fetch_rss_feed(source['rss'], source)
                all_news.extend(news_items)
                time.sleep(random.uniform(2, 5))
        
        self.logger.info(f"Total news fetched: {len(all_news)}")
        return all_news
    
    def process_and_filter_news(self, raw_news):
        """Process and filter news items"""
        self.logger.info("Processing and filtering news...")
        
        # Filter and rank news
        filtered_news = self.filter.filter_and_rank_news(raw_news, max_items=30)
        
        self.logger.info(f"Filtered to {len(filtered_news)} high-quality items")
        
        # Translate news items
        translated_news = []
        
        for item in filtered_news:
            try:
                # Translate if not already bilingual
                if item.get('language') != 'both':
                    translated_item = self.translator.translate_news_content(item)
                    translated_news.append(translated_item)
                else:
                    translated_news.append(item)
                    
                # Rate limiting for translation API
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                self.logger.warning(f"Translation failed for item: {e}")
                translated_news.append(item)  # Keep original
        
        return translated_news
    
    def save_news_to_file(self, news_items, filename=None):
        """Save news items to JSON file"""
        if not filename:
            filename = f"football_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_items': len(news_items),
                    'news': news_items
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"News saved to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to save news: {e}")
            return None
    
    def publish_to_social_media(self, news_items, max_posts=6):
        """Publish top news to social media"""
        if not news_items:
            self.logger.warning("No news items to publish")
            return False
        
        # Select top items for posting
        top_news = sorted(news_items, key=lambda x: x.get('priority_score', 0), reverse=True)[:max_posts]
        
        self.logger.info(f"Publishing {len(top_news)} items to social media")
        
        try:
            # Initialize X bot
            x_bot = XAutomationBot(headless=True)
            
            if x_bot.setup_driver():
                posts_count = x_bot.process_news_batch(top_news)
                x_bot.close()
                
                self.logger.info(f"Successfully published {posts_count} posts")
                return posts_count > 0
            else:
                self.logger.error("Failed to initialize X bot")
                return False
                
        except Exception as e:
            self.logger.error(f"Social media publishing failed: {e}")
            return False
    
    def run_news_cycle(self):
        """Run complete news aggregation cycle"""
        self.logger.info("🚀 Starting football news aggregation cycle")
        
        try:
            # 1. Fetch all news
            raw_news = self.fetch_all_news()
            
            if not raw_news:
                self.logger.warning("No news fetched, ending cycle")
                return False
            
            # 2. Process and filter
            processed_news = self.process_and_filter_news(raw_news)
            
            if not processed_news:
                self.logger.warning("No news passed filtering, ending cycle")
                return False
            
            # 3. Save to file
            saved_file = self.save_news_to_file(processed_news, 'latest_football_news.json')
            
            # 4. Publish to social media
            if processed_news:
                success = self.publish_to_social_media(processed_news)
                
                if success:
                    self.logger.info("✅ News cycle completed successfully")
                else:
                    self.logger.warning("⚠️ Social media publishing failed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ News cycle failed: {e}")
            return False
    
    def get_trending_summary(self):
        """Get trending topics summary"""
        try:
            with open('latest_football_news.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                news_items = data.get('news', [])
            
            if news_items:
                trending = self.filter.get_trending_topics(news_items)
                return trending
            
        except Exception as e:
            self.logger.error(f"Failed to get trending summary: {e}")
        
        return []

# Main execution
if __name__ == "__main__":
    aggregator = FootballNewsAggregator()
    
    # Run a single cycle
    success = aggregator.run_news_cycle()
    
    if success:
        # Show trending topics
        trending = aggregator.get_trending_summary()
        print("\n📈 Trending Football Topics:")
        for topic, score in trending:
            print(f"- {topic}: {score:.1f} points")
    
    print("\n✅ Football news aggregation complete!")