import re
import hashlib
from datetime import datetime, timedelta
import json
from difflib import SequenceMatcher
from collections import defaultdict

class FootballNewsFilter:
    def __init__(self):
        # High priority keywords (transfers, results, etc.)
        self.priority_keywords = {
            'transfers': [
                'transfer', 'signs', 'joined', 'contract', 'deal', 'agreed',
                'official', 'confirmed', 'medical', 'fee', 'million',
                'transferi', 'imzaladı', 'anlaştı', 'bonservis', 'sözleşme'
            ],
            'match_results': [
                'wins', 'defeats', 'draws', 'scored', 'goals', 'result',
                'final score', 'match report', 'highlights',
                'kazandı', 'yenildi', 'berabere', 'gol', 'skor', 'maç sonucu'
            ],
            'breaking_news': [
                'breaking', 'urgent', 'just in', 'confirmed', 'official',
                'exclusive', 'first', 'son dakika', 'acil', 'özel haber'
            ],
            'injuries': [
                'injury', 'injured', 'surgery', 'recovery', 'medical',
                'out for', 'ruled out', 'fitness',
                'sakatlık', 'yaralı', 'ameliyat', 'tedavi'
            ]
        }
        
        # Top clubs and players for priority scoring
        self.top_clubs = [
            'manchester united', 'manchester city', 'arsenal', 'chelsea', 
            'liverpool', 'tottenham', 'barcelona', 'real madrid', 
            'atletico madrid', 'juventus', 'milan', 'inter', 'napoli',
            'bayern munich', 'dortmund', 'psg', 'galatasaray', 
            'fenerbahce', 'besiktas', 'trabzonspor'
        ]
        
        self.top_players = [
            'messi', 'ronaldo', 'mbappe', 'haaland', 'benzema',
            'lewandowski', 'modric', 'neymar', 'kane', 'salah',
            'de bruyne', 'pedri', 'bellingham', 'osimhen'
        ]
        
        # Spam/low-quality indicators
        self.spam_indicators = [
            'click here', 'subscribe', 'watch now', 'full video',
            'tıkla', 'abone ol', 'izle', 'tam video'
        ]
        
        # Recently processed news (avoid duplicates)
        self.processed_news = {}
        self.similarity_threshold = 0.7
        
    def calculate_priority_score(self, news_item):
        """
        Calculate priority score for news item (0-100)
        """
        title = news_item.get('title', '').lower()
        summary = news_item.get('summary', '').lower()
        content = f"{title} {summary}"
        source_priority = news_item.get('source_priority', 5)
        
        score = 0
        
        # Base score from source reliability
        score += source_priority * 2
        
        # Priority keyword bonuses
        for category, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    if category == 'breaking_news':
                        score += 25
                    elif category == 'transfers':
                        score += 20
                    elif category == 'match_results':
                        score += 15
                    elif category == 'injuries':
                        score += 10
        
        # Top club/player bonus
        for club in self.top_clubs:
            if club in content:
                score += 15
                break
        
        for player in self.top_players:
            if player in content:
                score += 10
                break
        
        # Recency bonus (newer = higher score)
        pub_date = news_item.get('published')
        if pub_date:
            hours_ago = self._hours_since_publication(pub_date)
            if hours_ago < 1:
                score += 20
            elif hours_ago < 6:
                score += 10
            elif hours_ago < 24:
                score += 5
        
        # Spam penalty
        for spam_word in self.spam_indicators:
            if spam_word in content:
                score -= 30
                break
        
        # Length penalty (too short or too long)
        title_length = len(news_item.get('title', ''))
        if title_length < 20 or title_length > 200:
            score -= 10
        
        return max(0, min(100, score))
    
    def is_duplicate(self, news_item):
        """
        Check if news is duplicate/similar to recently processed
        """
        title = news_item.get('title', '')
        content_hash = hashlib.md5(title.encode()).hexdigest()
        
        # Check exact hash match
        if content_hash in self.processed_news:
            return True
        
        # Check similarity with recent news
        for stored_title in self.processed_news.values():
            similarity = SequenceMatcher(None, title.lower(), stored_title.lower()).ratio()
            if similarity > self.similarity_threshold:
                return True
        
        # Store this news
        self.processed_news[content_hash] = title
        
        # Clean old entries (keep only last 1000)
        if len(self.processed_news) > 1000:
            old_keys = list(self.processed_news.keys())[:-500]
            for key in old_keys:
                del self.processed_news[key]
        
        return False
    
    def categorize_news(self, news_item):
        """
        Categorize news by type and region
        """
        title = news_item.get('title', '').lower()
        summary = news_item.get('summary', '').lower()
        content = f"{title} {summary}"
        
        categories = []
        
        # Type categorization
        for category, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    categories.append(category)
                    break
        
        # League categorization
        leagues = {
            'premier_league': ['premier league', 'epl', 'manchester', 'arsenal', 'chelsea'],
            'la_liga': ['la liga', 'barcelona', 'real madrid', 'atletico'],
            'serie_a': ['serie a', 'juventus', 'milan', 'inter', 'napoli'],
            'bundesliga': ['bundesliga', 'bayern', 'dortmund', 'leipzig'],
            'super_lig': ['süper lig', 'galatasaray', 'fenerbahçe', 'beşiktaş'],
            'champions_league': ['champions league', 'ucl', 'european cup'],
            'world_cup': ['world cup', 'fifa', 'dünya kupası'],
            'euros': ['euro 2024', 'european championship', 'avrupa şampiyonası']
        }
        
        for league, keywords in leagues.items():
            for keyword in keywords:
                if keyword in content:
                    categories.append(league)
                    break
        
        return categories or ['general']
    
    def filter_and_rank_news(self, news_items, max_items=50):
        """
        Filter, rank and return top news items
        """
        filtered_news = []
        
        for item in news_items:
            # Skip duplicates
            if self.is_duplicate(item):
                continue
            
            # Calculate priority score
            score = self.calculate_priority_score(item)
            
            # Skip low-quality news
            if score < 30:
                continue
            
            # Add metadata
            item['priority_score'] = score
            item['categories'] = self.categorize_news(item)
            item['processed_at'] = datetime.now().isoformat()
            
            filtered_news.append(item)
        
        # Sort by priority score (highest first)
        filtered_news.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Return top items, ensuring variety
        return self._ensure_variety(filtered_news[:max_items])
    
    def _ensure_variety(self, news_items):
        """
        Ensure variety in categories and sources
        """
        if len(news_items) <= 10:
            return news_items
        
        category_counts = defaultdict(int)
        source_counts = defaultdict(int)
        varied_items = []
        
        for item in news_items:
            categories = item.get('categories', ['general'])
            source = item.get('source', 'unknown')
            
            # Check if we have too many from this category/source
            main_category = categories[0] if categories else 'general'
            
            if category_counts[main_category] >= 3 or source_counts[source] >= 2:
                continue
            
            category_counts[main_category] += 1
            source_counts[source] += 1
            varied_items.append(item)
            
            if len(varied_items) >= 30:  # Limit variety check
                break
        
        # Add remaining items to fill quota
        for item in news_items:
            if item not in varied_items and len(varied_items) < len(news_items):
                varied_items.append(item)
        
        return varied_items
    
    def _hours_since_publication(self, pub_date):
        """
        Calculate hours since publication
        """
        try:
            if isinstance(pub_date, str):
                # Try to parse date string
                pub_datetime = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            else:
                pub_datetime = pub_date
            
            return (datetime.now() - pub_datetime.replace(tzinfo=None)).total_seconds() / 3600
        except:
            return 24  # Default to 24 hours if parsing fails
    
    def get_trending_topics(self, news_items):
        """
        Extract trending topics from recent news
        """
        topics = defaultdict(int)
        
        for item in news_items:
            categories = item.get('categories', [])
            for category in categories:
                topics[category] += item.get('priority_score', 0)
        
        # Sort by total score
        trending = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return trending[:10]

# Test the filter
if __name__ == "__main__":
    filter_system = FootballNewsFilter()
    
    # Sample news for testing
    test_news = [
        {
            'title': 'BREAKING: Messi signs new contract with Barcelona',
            'summary': 'Lionel Messi has agreed to a new deal...',
            'source': 'ESPN',
            'source_priority': 9,
            'published': datetime.now().isoformat()
        },
        {
            'title': 'Man United defeats Arsenal 3-1',
            'summary': 'Manchester United beat Arsenal in Premier League...',
            'source': 'BBC',
            'source_priority': 10,
            'published': datetime.now().isoformat()
        }
    ]
    
    filtered = filter_system.filter_and_rank_news(test_news)
    for news in filtered:
        print(f"Score: {news['priority_score']} - {news['title']}")
        print(f"Categories: {news['categories']}")
        print("---")