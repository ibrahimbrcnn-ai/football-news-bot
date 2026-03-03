#!/usr/bin/env python3
"""
Global Football News Bot - Main Entry Point

Bu script projenin ana giriş noktasıdır. Farklı modlarda çalışabilir:
- news: Sadece haber toplama
- social: Sadece sosyal medya paylaşımı  
- web: Sadece web sitesi çalıştırma
- full: Tam otomatik döngü (haber + sosyal medya)
"""

import argparse
import sys
import os
import json
import time
import schedule
import logging
from datetime import datetime
from football_news_aggregator import FootballNewsAggregator
from x_automation_bot import XAutomationBot
from web_app import app

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('football_news_main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_news_cycle():
    """Haber toplama döngüsü çalıştır"""
    logger.info("🚀 Starting news aggregation cycle...")
    
    aggregator = FootballNewsAggregator()
    success = aggregator.run_news_cycle()
    
    if success:
        logger.info("✅ News cycle completed successfully")
        return True
    else:
        logger.error("❌ News cycle failed")
        return False

def run_social_media_posting():
    """Sosyal medya paylaşım döngüsü çalıştır"""
    logger.info("📱 Starting social media posting...")
    
    try:
        # Haber dosyasının varlığını kontrol et
        if not os.path.exists('latest_football_news.json'):
            logger.error("No news file found. Run news cycle first.")
            return False
        
        # Haberleri yükle
        with open('latest_football_news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        news_items = data.get('news', [])
        
        if not news_items:
            logger.warning("No news items found for posting")
            return False
        
        # X bot ile paylaş
        bot = XAutomationBot(headless=True)
        
        if bot.setup_driver():
            # En yüksek puanlı haberleri seç
            top_news = sorted(news_items, key=lambda x: x.get('priority_score', 0), reverse=True)[:6]
            
            posted_count = bot.process_news_batch(top_news)
            bot.close()
            
            if posted_count > 0:
                logger.info(f"✅ Posted {posted_count} items to social media")
                return True
            else:
                logger.warning("⚠️ No items were posted to social media")
                return False
        else:
            logger.error("❌ Failed to initialize social media bot")
            return False
            
    except Exception as e:
        logger.error(f"❌ Social media posting failed: {e}")
        return False

def run_web_server():
    """Web sunucusu çalıştır"""
    logger.info("🌐 Starting web server...")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)

def run_full_cycle():
    """Tam otomatik döngü: haber + sosyal medya"""
    logger.info("🔄 Running full automation cycle...")
    
    # 1. Haber toplama
    news_success = run_news_cycle()
    
    if news_success:
        # 2. Sosyal medya paylaşımı
        time.sleep(30)  # Kısa bekleme
        social_success = run_social_media_posting()
        
        return news_success and social_success
    else:
        logger.error("Skipping social media due to news cycle failure")
        return False

def run_scheduler():
    """Zamanlayıcı ile otomatik çalıştırma"""
    logger.info("⏰ Starting scheduled automation...")
    
    # Her 15 dakikada bir haber kontrolü
    schedule.every(15).minutes.do(run_news_cycle)
    
    # Her 30 dakikada bir sosyal medya paylaşımı
    schedule.every(30).minutes.do(run_social_media_posting)
    
    # İlk çalıştırma
    logger.info("Running initial cycle...")
    run_full_cycle()
    
    # Sürekli döngü
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol
            
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(300)  # 5 dakika bekle ve devam et

def show_status():
    """Sistem durumu göster"""
    print("\n" + "="*50)
    print("🏈 GLOBAL FOOTBALL NEWS BOT STATUS")
    print("="*50)
    
    # News file kontrolü
    if os.path.exists('latest_football_news.json'):
        try:
            with open('latest_football_news.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = data.get('timestamp', 'Unknown')
            news_count = len(data.get('news', []))
            
            print(f"📰 Latest News: {news_count} items")
            print(f"🕒 Last Update: {timestamp}")
            print("✅ News data available")
        except Exception as e:
            print(f"❌ News data error: {e}")
    else:
        print("❌ No news data found")
    
    # Environment variables kontrolü
    required_vars = [
        'X_ENGLISH_USERNAME',
        'X_ENGLISH_PASSWORD', 
        'X_TURKISH_USERNAME',
        'X_TURKISH_PASSWORD'
    ]
    
    print(f"\n🔐 Environment Variables:")
    for var in required_vars:
        status = "✅" if os.getenv(var) else "❌"
        print(f"{status} {var}")
    
    # Log dosyaları
    log_files = ['football_news.log', 'football_news_main.log']
    print(f"\n📋 Log Files:")
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✅ {log_file} ({size} bytes)")
        else:
            print(f"❌ {log_file} (not found)")
    
    print("="*50)

def main():
    """Ana program"""
    parser = argparse.ArgumentParser(
        description="Global Football News Bot - Otomatik Futbol Haber Sistemi"
    )
    
    parser.add_argument(
        'mode',
        choices=['news', 'social', 'web', 'full', 'schedule', 'status'],
        help='Çalışma modu seç'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Browser\'ı gizli modda çalıştır'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debug modu'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        os.environ['FLASK_ENV'] = 'development'
    
    # Mode'a göre çalıştır
    try:
        if args.mode == 'news':
            success = run_news_cycle()
            sys.exit(0 if success else 1)
            
        elif args.mode == 'social':
            success = run_social_media_posting() 
            sys.exit(0 if success else 1)
            
        elif args.mode == 'web':
            run_web_server()
            
        elif args.mode == 'full':
            success = run_full_cycle()
            sys.exit(0 if success else 1)
            
        elif args.mode == 'schedule':
            run_scheduler()
            
        elif args.mode == 'status':
            show_status()
            
    except KeyboardInterrupt:
        logger.info("⏹️ Program stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Program crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()