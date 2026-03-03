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
        """Setup Chrome driver with ADVANCED stealth options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')  # New headless mode
        
        # ADVANCED Anti-detection options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Faster loading
        chrome_options.add_argument('--disable-javascript')  # Bypass some detections
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        
        # REAL browser behavior simulation
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("detach", True)
        
        # REAL user agent rotation (LATEST)
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # REAL window sizes
        window_sizes = [(1366, 768), (1920, 1080), (1440, 900), (1600, 900), (1280, 1024)]
        width, height = random.choice(window_sizes)
        chrome_options.add_argument(f'--window-size={width},{height}')
        
        # Memory and performance optimizations
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--max_old_space_size=4096')
        
        try:
            print("🚀 Initializing STEALTH Chrome driver...")
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # ADVANCED JavaScript stealth injections
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            self.driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => ({state: 'granted'})})})")
            self.driver.execute_script("window.chrome = {runtime: {}}")
            
            # Set realistic viewport
            self.driver.set_window_size(width, height)
            
            self.wait = WebDriverWait(self.driver, 30)  # Longer timeout
            
            print("✅ STEALTH Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize STEALTH driver: {e}")
            return False
    
    def human_like_delay(self, min_delay=1, max_delay=3):
        """ADVANCED human-like random delays with realistic patterns"""
        # Realistic delay patterns
        delay_patterns = [
            random.uniform(min_delay, max_delay),  # Normal
            random.uniform(min_delay * 0.5, min_delay),  # Quick
            random.uniform(max_delay, max_delay * 1.5),  # Slow/thinking
        ]
        delay = random.choice(delay_patterns)
        time.sleep(delay)
    
    def human_typing(self, element, text):
        """ULTRA-realistic human typing with mistakes and corrections"""
        element.clear()
        
        # Sometimes pause before typing (thinking)
        if random.random() < 0.3:
            time.sleep(random.uniform(0.5, 1.5))
        
        for i, char in enumerate(text):
            # Realistic typing speed variation
            if char.isalpha():
                delay = random.uniform(0.08, 0.25)  # Letters
            elif char.isdigit():
                delay = random.uniform(0.15, 0.35)  # Numbers (slower)
            else:
                delay = random.uniform(0.05, 0.20)  # Special chars
            
            # Occasionally make "mistakes" and correct (more human)
            if random.random() < 0.05 and i < len(text) - 1:  # 5% mistake chance
                wrong_chars = 'abcdefghijklmnopqrstuvwxyz'
                wrong_char = random.choice(wrong_chars)
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACK_SPACE)  # Correct mistake
                time.sleep(random.uniform(0.1, 0.2))
            
            element.send_keys(char)
            time.sleep(delay)
            
            # Random pauses during typing (thinking/reading)
            if random.random() < 0.1:  # 10% pause chance
                time.sleep(random.uniform(0.3, 0.8))
    
    def random_mouse_movement(self):
        """ADVANCED random mouse movements simulating real user behavior"""
        try:
            actions = ActionChains(self.driver)
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Current mouse position (start from random)
            current_x = random.randint(100, viewport_width - 100)
            current_y = random.randint(100, viewport_height - 100)
            
            # Realistic mouse movement patterns
            movement_count = random.randint(3, 8)
            
            for _ in range(movement_count):
                # Move to random position with curved path
                target_x = random.randint(50, viewport_width - 50)
                target_y = random.randint(50, viewport_height - 50)
                
                # Bezier-like curve simulation
                steps = random.randint(5, 15)
                for step in range(steps):
                    progress = step / steps
                    # Add some curve randomness
                    curve_offset_x = random.randint(-50, 50) * (1 - abs(progress - 0.5) * 2)
                    curve_offset_y = random.randint(-30, 30) * (1 - abs(progress - 0.5) * 2)
                    
                    next_x = current_x + (target_x - current_x) * progress + curve_offset_x
                    next_y = current_y + (target_y - current_y) * progress + curve_offset_y
                    
                    # Ensure within bounds
                    next_x = max(10, min(viewport_width - 10, next_x))
                    next_y = max(10, min(viewport_height - 10, next_y))
                    
                    actions.move_to_element_with_offset(self.driver.find_element(By.TAG_NAME, "body"), next_x, next_y)
                    actions.pause(random.uniform(0.01, 0.05))
                
                current_x, current_y = target_x, target_y
                
                # Sometimes pause at position (reading/thinking)
                if random.random() < 0.4:
                    actions.pause(random.uniform(0.2, 0.8))
                
                # Occasionally scroll (very human)
                if random.random() < 0.3:
                    scroll_amount = random.randint(-3, 3)
                    if scroll_amount != 0:
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount * 100})")
                        actions.pause(random.uniform(0.1, 0.3))
            
            actions.perform()
            
        except Exception as e:
            print(f"Mouse movement error: {e}")
            pass
    
    def login_to_account(self, account_type):
        """ADVANCED Human-like login to X account"""
        account = self.accounts[account_type]
        
        if not account['username'] or not account['password']:
            print(f"❌ Missing credentials for {account_type} account")
            return False
        
        try:
            print(f"🔐 STEALTH login to {account_type} account...")
            
            # First visit X.com homepage (more natural)
            self.driver.get("https://x.com")
            self.human_like_delay(2, 4)
            
            # Random mouse movements on homepage
            self.random_mouse_movement()
            self.human_like_delay(1, 3)
            
            # Now go to login
            self.driver.get("https://x.com/i/flow/login")
            self.human_like_delay(4, 7)
            
            # More random movements
            self.random_mouse_movement()
            
            # Multiple selectors for username (X changes them)
            username_selectors = [
                'input[autocomplete="username"]',
                'input[name="text"]',
                'input[data-testid="ocfEnterTextTextInput"]',
                'input[placeholder*="username"]',
                'input[placeholder*="email"]'
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not username_input:
                print("❌ Username input not found")
                return False
            
            # VERY human-like typing
            self.human_like_delay(1, 2)
            self.human_typing(username_input, account['username'])
            self.human_like_delay(1, 3)
            
            # Find Next button with multiple approaches
            next_selectors = [
                '//span[text()="Next"]',
                '//span[contains(text(),"Next")]',
                '//div[@role="button" and contains(.,"Next")]',
                '[data-testid="LoginForm_Login_Button"]'
            ]
            
            next_button = None
            for selector in next_selectors:
                try:
                    if selector.startswith('//'):
                        next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        next_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if next_button:
                self.random_mouse_movement()
                next_button.click()
                self.human_like_delay(3, 6)
            
            # Password input with multiple selectors
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[autocomplete="current-password"]',
                'input[data-testid="ocfEnterTextTextInput"]'
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not password_input:
                print("❌ Password input not found")
                return False
            
            self.human_like_delay(1, 2)
            self.human_typing(password_input, account['password'])
            self.human_like_delay(2, 4)
            
            # Login button with multiple approaches
            login_selectors = [
                '//span[text()="Log in"]',
                '//span[contains(text(),"Log in")]',
                '//div[@data-testid="LoginForm_Login_Button"]',
                '[data-testid="LoginForm_Login_Button"]'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if selector.startswith('//'):
                        login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if login_button:
                self.random_mouse_movement()
                login_button.click()
                self.human_like_delay(5, 10)  # Longer wait for login process
            
            # Check for success with multiple indicators
            success_selectors = [
                '[data-testid="SideNav_NewTweet_Button"]',
                '[data-testid="tweetButtonInline"]',
                '[aria-label="Post"]',
                '[data-testid="primaryColumn"]'
            ]
            
            login_successful = False
            for selector in success_selectors:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    login_successful = True
                    break
                except:
                    continue
            
            if login_successful:
                account['logged_in'] = True
                print(f"✅ STEALTH login successful for {account_type} account!")
                return True
            else:
                print(f"❌ STEALTH login failed for {account_type} account")
                return False
                
        except Exception as e:
            print(f"❌ STEALTH login error for {account_type}: {e}")
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