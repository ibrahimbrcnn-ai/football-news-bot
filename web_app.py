from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page - serve the football news website"""
    return render_template('index.html')

@app.route('/api/news')
def get_latest_news():
    """API endpoint to get latest football news"""
    try:
        # Try to load latest news from file
        news_file = os.path.join(os.path.dirname(__file__), 'latest_football_news.json')
        
        if os.path.exists(news_file):
            with open(news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify(data)
        else:
            # No news file exists, return sample data
            return jsonify({
                'timestamp': datetime.now().isoformat(),
                'total_items': 3,
                'news': [
                    {
                        'title_tr': '⚽ Futbol Haber Sistemi Aktif!',
                        'title_en': '⚽ Football News System Active!',
                        'summary_tr': 'Sistem her saat başı otomatik olarak dünya çapındaki futbol haberlerini topluyor. Telegram ve X hesaplarımızdan anlık takip edebilirsiniz!',
                        'summary_en': 'The system automatically collects football news from around the world every hour. Follow us on Telegram and X for instant updates!',
                        'url': 'https://github.com/ibrahimbrcnn-ai/football-news-bot',
                        'source': 'System',
                        'categories': ['breaking_news'],
                        'priority_score': 100,
                        'published_date': datetime.now().isoformat(),
                        'image_url': 'https://via.placeholder.com/800x400/2563eb/ffffff?text=Football+News+24/7'
                    },
                    {
                        'title_tr': '📱 Telegram Kanallarımız',
                        'title_en': '📱 Our Telegram Channels',
                        'summary_tr': 'Anlık haberler için Telegram kanallarımızı takip edin: @fubolhaber_live (Türkçe) ve @ftnewsaaa (English)',
                        'summary_en': 'Follow our Telegram channels for instant news: @fubolhaber_live (Turkish) and @ftnewsaaa (English)',
                        'url': 'https://t.me/fubolhaber_live',
                        'source': 'Telegram',
                        'categories': ['premier_league'],
                        'priority_score': 95,
                        'published_date': datetime.now().isoformat(),
                        'image_url': 'https://via.placeholder.com/800x400/0088cc/ffffff?text=Join+Telegram'
                    },
                    {
                        'title_tr': '🐦 X/Twitter Hesaplarımız',
                        'title_en': '🐦 Our X/Twitter Accounts',
                        'summary_tr': 'X üzerinden takip edin: @fubolhaber1 (Türkçe) ve @newsball_ (English)',
                        'summary_en': 'Follow us on X: @fubolhaber1 (Turkish) and @newsball_ (English)',
                        'url': 'https://twitter.com/fubolhaber1',
                        'source': 'X/Twitter',
                        'categories': ['la_liga'],
                        'priority_score': 90,
                        'published_date': datetime.now().isoformat(),
                        'image_url': 'https://via.placeholder.com/800x400/1DA1F2/ffffff?text=Follow+on+X'
                    }
                ],
                'message': 'Welcome! Live news will appear here once the system collects data from 90+ sources.'
            })
    
    except Exception as e:
        logger.error(f"Error loading news: {e}")
        return jsonify({
            'error': 'Failed to load news',
            'timestamp': datetime.now().isoformat(),
            'total_items': 0,
            'news': []
        }), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint to get website statistics"""
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'sources_count': 90,
            'languages_supported': 6,
            'regions_covered': ['Europe', 'South America', 'North America', 'Africa', 'Asia'],
            'total_news': 0,
            'last_update': None
        }
        
        # Try to get real news count
        news_file = os.path.join(os.path.dirname(__file__), 'latest_football_news.json')
        if os.path.exists(news_file):
            with open(news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats['total_news'] = len(data.get('news', []))
                stats['last_update'] = data.get('timestamp')
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'sources_count': 90,
            'languages_supported': 6,
            'total_news': 0
        })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Football News Bot',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
