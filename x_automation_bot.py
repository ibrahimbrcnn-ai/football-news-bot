import time
import random
import os
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from urllib.parse import urlparse
import hashlib

class XAutomationBot:
    def __init__(self, headless=True, use_proxy=False):
        self.headless = headless
        self.use_proxy = use_proxy
        self.driver = None
        self.wait = None
        self.accounts = {
            'english': {
                'username': os.getenv('X_ENGLISH_USERNAME'),
                'password': os.getenv('X_ENGLISH_PASSWORD'),
                'logged_in': False
            },
            'turkish': {
                'username': os.getenv('X_TURKISH_USERNAME'), 
                'password': os.getenv('X_TURKISH_PASSWORD'),
                'logged_in': False
            }
        }
        self.posted_tweets = set()  # Track posted tweets to avoid duplicates
        self.daily_tweet_count = {'english': 0, 'turkish': 0}
        self.last_reset_date = datetime.now().date()
        
    def setup_driver(self):
        """Setup Chrome driver with stealth options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Stealth mode options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Window size randomization
        window_sizes = [(1366, 768), (1920, 1080), (1440, 900), (1600, 900)]
        width, height = random.choice(window_sizes)
        chrome_options.add_argument(f'--window-size={width},{height}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize driver: {e}")
            return False
    
    def human_like_delay(self, min_delay=1, max_delay=3):
        """Human-like random delays"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def human_typing(self, element, text):
        """Type text with human-like delays"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def random_mouse_movement(self):
        """Random mouse movements to appear human"""
        try:
            actions = ActionChains(self.driver)
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, viewport_width - 100)
                y = random.randint(100, viewport_height - 100)
                actions.move_by_offset(x, y)
                actions.pause(random.uniform(0.1, 0.3))
            
            actions.perform()
        except:
            pass
    
    def login_to_account(self, account_type):
        """Login to X account"""
        account = self.accounts[account_type]
        
        if not account['username'] or not account['password']:
            print(f"❌ Missing credentials for {account_type} account")
            return False
        
        try:
            print(f"🔐 Logging in to {account_type} account...")
            self.driver.get("https://twitter.com/i/flow/login")
            
            self.human_like_delay(3, 6)
            
            # Username input
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            self.human_typing(username_input, account['username'])
            
            # Next button
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]'))
            )
            next_button.click()
            
            self.human_like_delay(2, 4)
            
            # Password input
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            self.human_typing(password_input, account['password'])
            
            # Login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Log in"]'))
            )
            login_button.click()
            
            self.human_like_delay(5, 8)
            
            # Check if login successful
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]')))
                account['logged_in'] = True
                print(f"✅ Successfully logged in to {account_type} account")
                return True
            except TimeoutException:
                print(f"❌ Login failed for {account_type} account")
                return False
                
        except Exception as e:
            print(f"❌ Login error for {account_type}: {e}")
            return False
    
    def download_image(self, image_url, filename):
        """Download image from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"❌ Failed to download image: {e}")
            return False
    
    def post_tweet(self, content, image_path=None, account_type='english'):
        """Post a tweet with optional image"""
        if not self.accounts[account_type]['logged_in']:
            if not self.login_to_account(account_type):
                return False
        
        # Check daily limits
        if self._check_daily_limits(account_type):
            return False
        
        # Check for duplicates
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self.posted_tweets:
            print("⚠️ Duplicate tweet detected, skipping")
            return False
        
        try:
            print(f"📝 Posting tweet to {account_type} account...")
            
            # Navigate to home and click tweet button
            self.driver.get("https://twitter.com/home")
            self.human_like_delay(3, 5)
            
            # Click compose tweet
            tweet_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]'))
            )
            tweet_button.click()
            
            self.human_like_delay(2, 4)
            
            # Find tweet compose area
            tweet_compose = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            
            # Type the tweet content
            self.human_typing(tweet_compose, content)
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                try:
                    media_input = self.driver.find_element(By.CSS_SELECTOR, 'input[data-testid="fileInput"]')
                    media_input.send_keys(os.path.abspath(image_path))
                    self.human_like_delay(3, 6)  # Wait for upload
                    print("✅ Image uploaded successfully")
                except Exception as e:
                    print(f"⚠️ Image upload failed: {e}")
            
            # Random mouse movement before posting
            self.random_mouse_movement()
            self.human_like_delay(1, 3)
            
            # Click tweet button
            post_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButtonInline"]'))
            )
            post_button.click()
            
            self.human_like_delay(3, 6)
            
            # Verify tweet was posted
            try:
                # Look for success indicators or redirect to timeline
                self.wait.until(
                    EC.any_of(
                        EC.url_contains("/home"),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="toast"]'))
                    )
                )
                
                # Track successful post
                self.posted_tweets.add(content_hash)
                self.daily_tweet_count[account_type] += 1
                
                print(f"✅ Tweet posted successfully to {account_type} account!")
                
                # Clean up image file
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass
                
                return True
                
            except TimeoutException:
                print("❌ Tweet posting may have failed")
                return False
        
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            return False
    
    def _check_daily_limits(self, account_type):
        """Check if daily tweet limit reached"""
        # Reset counters if new day
        if datetime.now().date() > self.last_reset_date:
            self.daily_tweet_count = {'english': 0, 'turkish': 0}
            self.last_reset_date = datetime.now().date()
        
        # Daily limits (to stay under radar)
        DAILY_LIMITS = {'english': 30, 'turkish': 30}
        
        if self.daily_tweet_count[account_type] >= DAILY_LIMITS[account_type]:
            print(f"⚠️ Daily limit reached for {account_type} account ({self.daily_tweet_count[account_type]} tweets)")
            return True
        
        return False
    
    def format_tweet_content(self, news_item, language='en', max_length=270):
        """Format news item into tweet content"""
        if language == 'tr':
            title = news_item.get('title_tr', news_item.get('title', ''))
            summary = news_item.get('summary_tr', news_item.get('summary', ''))
        else:
            title = news_item.get('title_en', news_item.get('title', ''))
            summary = news_item.get('summary_en', news_item.get('summary', ''))
        
        url = news_item.get('url', '')
        
        # Add relevant hashtags
        hashtags = self._generate_hashtags(news_item, language)
        
        # Construct tweet
        tweet_text = f"{title}\n\n{hashtags}\n{url}"
        
        # Truncate if too long
        if len(tweet_text) > max_length:
            # Shorten title if needed
            available_length = max_length - len(hashtags) - len(url) - 5  # 5 for formatting
            if len(title) > available_length:
                title = title[:available_length-3] + "..."
            tweet_text = f"{title}\n\n{hashtags}\n{url}"
        
        return tweet_text
    
    def _generate_hashtags(self, news_item, language='en'):
        """Generate relevant hashtags for news item"""
        categories = news_item.get('categories', [])
        
        if language == 'tr':
            hashtag_map = {
                'transfers': '#Transfer #Futbol',
                'match_results': '#MacSonucu #Futbol',
                'breaking_news': '#SonDakika #Futbol',
                'premier_league': '#PremierLig',
                'la_liga': '#LaLiga',
                'serie_a': '#SerieA',
                'bundesliga': '#Bundesliga',
                'super_lig': '#SüperLig',
                'champions_league': '#ŞampiyonlarLigi'
            }
            base_tags = '#Futbol #Spor'
        else:
            hashtag_map = {
                'transfers': '#Transfer #Football',
                'match_results': '#MatchResult #Football',
                'breaking_news': '#Breaking #Football',
                'premier_league': '#PremierLeague',
                'la_liga': '#LaLiga',
                'serie_a': '#SerieA',
                'bundesliga': '#Bundesliga',
                'super_lig': '#SuperLig',
                'champions_league': '#ChampionsLeague'
            }
            base_tags = '#Football #Soccer'
        
        hashtags = [base_tags]
        
        for category in categories[:2]:  # Max 2 category hashtags
            if category in hashtag_map:
                hashtags.append(hashtag_map[category])
        
        return ' '.join(hashtags)
    
    def process_news_batch(self, news_items):
        """Process batch of news items and post to both accounts"""
        english_posts = 0
        turkish_posts = 0
        
        for news_item in news_items:
            try:
                # Download image if available
                image_path = None
                if news_item.get('image_url'):
                    image_filename = f"temp_image_{int(time.time())}.jpg"
                    if self.download_image(news_item['image_url'], image_filename):
                        image_path = image_filename
                
                # Post to English account
                if english_posts < 3:  # Limit per batch
                    english_content = self.format_tweet_content(news_item, 'en')
                    if self.post_tweet(english_content, image_path, 'english'):
                        english_posts += 1
                        self.human_like_delay(60, 180)  # 1-3 minutes between posts
                
                # Post to Turkish account
                if turkish_posts < 3:  # Limit per batch
                    turkish_content = self.format_tweet_content(news_item, 'tr')
                    if self.post_tweet(turkish_content, image_path, 'turkish'):
                        turkish_posts += 1
                        self.human_like_delay(60, 180)  # 1-3 minutes between posts
                
                # Clean up image
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass
                        
            except Exception as e:
                print(f"❌ Error processing news item: {e}")
                continue
        
        print(f"📊 Batch complete: {english_posts} English posts, {turkish_posts} Turkish posts")
        return english_posts + turkish_posts
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")

# Test the bot
if __name__ == "__main__":
    # Create sample news item for testing
    sample_news = {
        'title': 'Manchester United signs new striker from Brazil',
        'title_tr': 'Manchester United Brezilyalı forveti transfer etti',
        'summary': 'The English club announced the signing...',
        'summary_tr': 'İngiliz kulübü transferi açıkladı...',
        'url': 'https://example.com/news',
        'categories': ['transfers', 'premier_league'],
        'image_url': 'https://example.com/image.jpg'
    }
    
    bot = XAutomationBot(headless=False)  # Set to True for production
    
    if bot.setup_driver():
        bot.process_news_batch([sample_news])
        bot.close()