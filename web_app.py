from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta
import logging
from football_news_aggregator import FootballNewsAggregator

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global news aggregator instance
aggregator = FootballNewsAggregator()

@app.route('/')
def index():
    """Main page - serve the football news website"""
    return render_template('index.html')

@app.route('/api/news')
def get_latest_news():
    """API endpoint to get latest football news"""
    try:
        # Try to load latest news from file
        if os.path.exists('latest_football_news.json'):
            with open('latest_football_news.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify(data)
        else:
            # No news file exists, return empty response
            return jsonify({
                'timestamp': datetime.now().isoformat(),
                'total_items': 0,
                'news': [],
                'message': 'No news available yet. Please wait for the next update cycle.'
            })
    
    except Exception as e:
        logger.error(f"Error loading news: {e}")
        return jsonify({
            'error': 'Failed to load news',
            'timestamp': datetime.now().isoformat(),
            'total_items': 0,
            'news': []
        }), 500

@app.route('/api/news/refresh')
def refresh_news():
    """API endpoint to manually trigger news refresh"""
    try:
        logger.info("Manual news refresh triggered")
        success = aggregator.run_news_cycle()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'News refreshed successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to refresh news',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error refreshing news: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint to get website statistics"""
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'sources_count': 120,
            'languages_supported': 6,
            'regions_covered': ['Europe', 'South America', 'North America', 'Africa', 'Asia', 'Oceania']
        }
        
        # Try to get real news count
        if os.path.exists('latest_football_news.json'):
            with open('latest_football_news.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats['total_news'] = len(data.get('news', []))
                stats['last_update'] = data.get('timestamp')
        else:
            stats['total_news'] = 0
            stats['last_update'] = None
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'error': 'Failed to get stats',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/trending')
def get_trending():
    """API endpoint to get trending topics"""
    try:
        trending = aggregator.get_trending_summary()
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'trending_topics': [
                {'topic': topic, 'score': score} 
                for topic, score in trending
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        return jsonify({
            'error': 'Failed to get trending topics',
            'timestamp': datetime.now().isoformat(),
            'trending_topics': []
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/latest_football_news.json')
def serve_news_json():
    """Serve the latest news JSON file directly"""
    try:
        return send_from_directory('.', 'latest_football_news.json')
    except FileNotFoundError:
        # Return empty news structure if file doesn't exist
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'total_items': 0,
            'news': []
        })

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap for SEO"""
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://your-domain.com/</loc>
        <lastmod>{}</lastmod>
        <changefreq>hourly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://your-domain.com/api/news</loc>
        <lastmod>{}</lastmod>
        <changefreq>hourly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>'''.format(
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%Y-%m-%d')
    )
    
    response = app.response_class(
        sitemap_xml,
        mimetype='application/xml'
    )
    return response

@app.route('/robots.txt')
def robots():
    """Robots.txt for search engines"""
    robots_txt = '''User-agent: *
Allow: /
Allow: /api/news
Allow: /api/stats
Allow: /api/trending

Disallow: /api/news/refresh
Disallow: /api/health

Sitemap: https://your-domain.com/sitemap.xml
'''
    
    response = app.response_class(
        robots_txt,
        mimetype='text/plain'
    )
    return response

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500

# CORS headers for API endpoints
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Initialize with a sample news cycle if no data exists
    if not os.path.exists('latest_football_news.json'):
        logger.info("No existing news data found, running initial news cycle...")
        try:
            aggregator.run_news_cycle()
            logger.info("Initial news cycle completed")
        except Exception as e:
            logger.error(f"Initial news cycle failed: {e}")
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Football News Web App on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)