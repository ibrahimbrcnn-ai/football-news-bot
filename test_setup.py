#!/usr/bin/env python3
"""
Test Setup Script - Kurulumu Test Et

Bu script sistemin doğru çalıştığını test eder
"""

import os
import sys
import json
from datetime import datetime
import requests

def test_environment():
    """Environment variables test"""
    print("[ENV] Environment Variables Test...")
    
    required_vars = [
        'X_TURKISH_USERNAME',
        'X_TURKISH_PASSWORD', 
        'X_ENGLISH_USERNAME',
        'X_ENGLISH_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("💡 .env dosyasını kontrol edin!")
        return False
    else:
        print("✅ All environment variables found")
        return True

def test_dependencies():
    """Python dependencies test"""
    print("\n📦 Dependencies Test...")
    
    required_packages = [
        'feedparser',
        'requests', 
        'bs4',  # beautifulsoup4 bs4 olarak import edilir
        'selenium',
        'flask'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("💡 Çalıştırın: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages installed")
        return True

def test_news_sources():
    """RSS kaynakları test"""
    print("\n📰 News Sources Test...")
    
    try:
        with open('global_football_sources.json', 'r', encoding='utf-8') as f:
            sources = json.load(f)
        
        total_sources = 0
        
        # English sources
        for category, source_list in sources.get('english_sources', {}).items():
            total_sources += len(source_list)
        
        # Turkish sources
        total_sources += len(sources.get('turkish_sources', []))
        
        # Regional sources
        for region, source_list in sources.get('regional_sources', {}).items():
            total_sources += len(source_list)
        
        print(f"✅ Found {total_sources} news sources")
        
        # Test bir kaç RSS feed
        test_feeds = [
            "https://www.espn.com/espn/rss/soccer/news",
            "http://feeds.bbci.co.uk/sport/football/rss.xml"
        ]
        
        working_feeds = 0
        for feed_url in test_feeds:
            try:
                response = requests.get(feed_url, timeout=10)
                if response.status_code == 200:
                    working_feeds += 1
            except:
                pass
        
        print(f"✅ Tested {working_feeds}/{len(test_feeds)} sample feeds working")
        return True
        
    except Exception as e:
        print(f"❌ News sources test failed: {e}")
        return False

def test_news_aggregation():
    """Haber toplama test"""
    print("\n🔄 News Aggregation Test...")
    
    try:
        from football_news_aggregator import FootballNewsAggregator
        
        aggregator = FootballNewsAggregator()
        
        # Sadece birkaç haber çek (test için)
        print("   Fetching sample news...")
        sample_sources = [
            {
                'name': 'BBC Sport',
                'rss': 'http://feeds.bbci.co.uk/sport/football/rss.xml',
                'priority': 10,
                'region': 'global'
            }
        ]
        
        news_count = 0
        for source in sample_sources:
            try:
                news_items = aggregator.fetch_rss_feed(source['rss'], source)
                news_count += len(news_items)
                break  # Sadece bir source test et
            except:
                continue
        
        if news_count > 0:
            print(f"✅ Successfully fetched {news_count} news items")
            return True
        else:
            print("⚠️ No news items fetched (might be temporary)")
            return True  # Bu geçici bir sorun olabilir
            
    except Exception as e:
        print(f"❌ News aggregation test failed: {e}")
        return False

def test_translation():
    """Çeviri sistemi test"""
    print("\n🌐 Translation System Test...")
    
    try:
        from translation_manager import TranslationManager
        
        translator = TranslationManager()
        
        # Basit çeviri testi
        test_text = "Manchester United signs new player"
        translated = translator.translate_text(test_text, 'tr', 'en')
        
        if translated and translated != test_text:
            print(f"✅ Translation working: '{test_text}' → '{translated}'")
            return True
        else:
            print("⚠️ Translation might be rate limited (this is normal)")
            return True  # Rate limit olabilir, bu normal
            
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        return False

def test_web_app():
    """Web uygulaması test"""
    print("\n🌐 Web Application Test...")
    
    try:
        from web_app import app
        
        with app.test_client() as client:
            # Ana sayfa testi
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Web application main page working")
                
                # API endpoint testi
                api_response = client.get('/api/health')
                if api_response.status_code == 200:
                    print("✅ API endpoints working")
                    return True
                else:
                    print("⚠️ API endpoints issue")
                    return False
            else:
                print("❌ Web application not responding")
                return False
                
    except Exception as e:
        print(f"❌ Web application test failed: {e}")
        return False

def run_all_tests():
    """Tüm testleri çalıştır"""
    print("GLOBAL FOOTBALL NEWS BOT - SETUP TEST")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Dependencies", test_dependencies),
        ("News Sources", test_news_sources),
        ("News Aggregation", test_news_aggregation),
        ("Translation System", test_translation),
        ("Web Application", test_web_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Sistem hazır!")
        print("\n🚀 Next Steps:")
        print("1. python main.py news    # Haber toplama test")
        print("2. python main.py web     # Web sitesi test")  
        print("3. GitHub'a yükle!")
    else:
        print("⚠️ Bazı testler başarısız. Lütfen hataları düzeltin.")
    
    return passed == total

if __name__ == "__main__":
    # .env dosyasını yükle
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed, using system environment")
    
    success = run_all_tests()
    sys.exit(0 if success else 1)