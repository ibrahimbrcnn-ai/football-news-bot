import os
import json
import requests
import time
from datetime import datetime
import logging
from urllib.parse import quote

class TelegramBot:
    def __init__(self):
        self.bots = {
            'turkish': {
                'token': os.getenv('TELEGRAM_TURKISH_BOT_TOKEN'),
                'chat_id': os.getenv('TELEGRAM_TURKISH_CHANNEL_ID'),
                'name': 'Türkçe Futbol Haberleri'
            },
            'english': {
                'token': os.getenv('TELEGRAM_ENGLISH_BOT_TOKEN'),
                'chat_id': os.getenv('TELEGRAM_ENGLISH_CHANNEL_ID'),
                'name': 'English Football News'
            }
        }
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def send_message(self, bot_type, text, image_url=None, parse_mode='HTML'):
        """Send message to Telegram channel"""
        bot = self.bots[bot_type]
        
        if not bot['token']:
            self.logger.error(f"❌ Missing token for {bot_type} bot")
            return False
        
        if not bot['chat_id']:
            self.logger.error(f"❌ Missing chat_id for {bot_type} bot")
            return False
        
        base_url = f"https://api.telegram.org/bot{bot['token']}"
        
        try:
            # Try with image first, fallback to text only if image fails
            if image_url:
                try:
                    url = f"{base_url}/sendPhoto"
                    data = {
                        'chat_id': bot['chat_id'],
                        'photo': image_url,
                        'caption': text[:1024],  # Telegram caption limit
                        'parse_mode': parse_mode
                    }
                    response = requests.post(url, json=data, timeout=15)
                    
                    if response.status_code == 200:
                        self.logger.info(f"✅ Photo sent successfully to {bot_type} channel")
                        return True
                    else:
                        self.logger.warning(f"⚠️ Failed to send photo to {bot_type}, trying text only: {response.text[:100]}")
                        # Fall through to text-only
                        image_url = None
                except Exception as img_error:
                    self.logger.warning(f"⚠️ Image error for {bot_type}, sending text only: {img_error}")
                    image_url = None
            
            # Send text message (either originally text-only or fallback from image failure)
            if not image_url:
                url = f"{base_url}/sendMessage"
                data = {
                    'chat_id': bot['chat_id'],
                    'text': text[:4096],  # Telegram message limit
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': False
                }
                response = requests.post(url, json=data, timeout=15)
                
                if response.status_code == 200:
                    self.logger.info(f"✅ Message sent successfully to {bot_type} channel")
                    return True
                else:
                    self.logger.error(f"❌ Failed to send message to {bot_type}: {response.text[:200]}")
                    return False
                
        except requests.exceptions.Timeout:
            self.logger.error(f"❌ Timeout sending to {bot_type} (15s)")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error sending message to {bot_type}: {str(e)[:200]}")
            return False
    
    def format_news_message(self, news_item, language='tr'):
        """Format news item for Telegram"""
        if language == 'tr':
            title = news_item.get('title_tr', news_item.get('title', ''))
            summary = news_item.get('summary_tr', news_item.get('summary', ''))
        else:
            title = news_item.get('title_en', news_item.get('title', ''))
            summary = news_item.get('summary_en', news_item.get('summary', ''))
        
        url = news_item.get('url', '')
        source = news_item.get('source', 'Unknown')
        categories = news_item.get('categories', [])
        
        # Create message with HTML formatting
        message = f"<b>⚽ {title}</b>\n\n"
        
        if summary:
            message += f"{summary[:300]}...\n\n"
        
        # Add categories as hashtags
        if categories:
            hashtags = self._generate_hashtags(categories, language)
            message += f"{hashtags}\n\n"
        
        # Add source and link
        message += f"📰 <i>{source}</i>\n"
        message += f"🔗 <a href='{url}'>Haberin Devamı</a>" if language == 'tr' else f"🔗 <a href='{url}'>Read More</a>"
        
        return message
    
    def _generate_hashtags(self, categories, language='tr'):
        """Generate hashtags from categories"""
        if language == 'tr':
            hashtag_map = {
                'transfers': '#Transfer',
                'match_results': '#MacSonucu',
                'breaking_news': '#SonDakika',
                'injuries': '#Sakatlık',
                'premier_league': '#PremierLeague',
                'la_liga': '#LaLiga',
                'serie_a': '#SerieA',
                'bundesliga': '#Bundesliga',
                'super_lig': '#SüperLig',
                'champions_league': '#ŞampiyonlarLigi'
            }
        else:
            hashtag_map = {
                'transfers': '#Transfer',
                'match_results': '#MatchResult',
                'breaking_news': '#BreakingNews',
                'injuries': '#Injury',
                'premier_league': '#PremierLeague',
                'la_liga': '#LaLiga',
                'serie_a': '#SerieA',
                'bundesliga': '#Bundesliga',
                'super_lig': '#SuperLig',
                'champions_league': '#ChampionsLeague'
            }
        
        hashtags = []
        for category in categories[:3]:  # Max 3 hashtags
            if category in hashtag_map:
                hashtags.append(hashtag_map[category])
        
        return ' '.join(hashtags) if hashtags else '#Football' if language == 'en' else '#Futbol'
    
    def post_news_batch(self, news_items, max_posts=10):
        """Post batch of news to both channels"""
        turkish_posts = 0
        english_posts = 0
        
        # Sort by priority
        sorted_news = sorted(news_items, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        self.logger.info(f"📰 Starting to post {min(len(sorted_news), max_posts)} news items...")
        
        for idx, news_item in enumerate(sorted_news[:max_posts], 1):
            try:
                self.logger.info(f"📝 Processing news {idx}/{min(len(sorted_news), max_posts)}")
                
                # Post to Turkish channel
                tr_message = self.format_news_message(news_item, 'tr')
                if self.send_message('turkish', tr_message, news_item.get('image_url')):
                    turkish_posts += 1
                    self.logger.info(f"✅ Turkish: {idx}/{min(len(sorted_news), max_posts)}")
                else:
                    self.logger.warning(f"⚠️ Turkish post {idx} failed, continuing...")
                
                time.sleep(2)  # Rate limiting
                
                # Post to English channel
                en_message = self.format_news_message(news_item, 'en')
                if self.send_message('english', en_message, news_item.get('image_url')):
                    english_posts += 1
                    self.logger.info(f"✅ English: {idx}/{min(len(sorted_news), max_posts)}")
                else:
                    self.logger.warning(f"⚠️ English post {idx} failed, continuing...")
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"❌ Error posting news {idx}: {str(e)[:200]}")
                self.logger.info(f"⏭️ Skipping to next news...")
                continue
        
        self.logger.info(f"📊 FINAL: Posted {turkish_posts} Turkish + {english_posts} English messages")
        return turkish_posts + english_posts
    
    def send_daily_summary(self, news_count, language='tr'):
        """Send daily summary message"""
        if language == 'tr':
            message = f"""
<b>📊 Günlük Özet</b>

✅ Bugün <b>{news_count}</b> haber paylaştık!

⚽ Premier League
🔴 La Liga
⚪ Serie A
🟡 Bundesliga

📱 Anlık haberler için kanalımızı takip edin!
            """
            bot_type = 'turkish'
        else:
            message = f"""
<b>📊 Daily Summary</b>

✅ We posted <b>{news_count}</b> news today!

⚽ Premier League
🔴 La Liga
⚪ Serie A
🟡 Bundesliga

📱 Follow us for instant football news!
            """
            bot_type = 'english'
        
        return self.send_message(bot_type, message.strip())

# Test function
if __name__ == "__main__":
    bot = TelegramBot()
    
    # Test message
    test_news = {
        'title': 'Test Haber: Manchester United Transfer Haberi',
        'title_tr': 'Test Haber: Manchester United Transfer Haberi',
        'title_en': 'Test News: Manchester United Transfer News',
        'summary': 'Bu bir test haberidir.',
        'summary_tr': 'Bu bir test haberidir.',
        'summary_en': 'This is a test news.',
        'url': 'https://example.com',
        'source': 'Test Source',
        'categories': ['transfers', 'premier_league'],
        'priority_score': 85
    }
    
    print("🧪 Testing Telegram Bot...")
    print(f"Turkish Token: {'✅' if bot.bots['turkish']['token'] else '❌'}")
    print(f"English Token: {'✅' if bot.bots['english']['token'] else '❌'}")
    
    bot.post_news_batch([test_news], max_posts=1)
