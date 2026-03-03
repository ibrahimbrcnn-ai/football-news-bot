import requests
import json
from urllib.parse import quote
import time
import random

class TranslationManager:
    def __init__(self):
        self.services = {
            'google_free': self._google_translate_free,
            'mymemory': self._mymemory_translate,
            'libretranslate': self._libretranslate
        }
        
        # Service rotation for high availability
        self.current_service = 0
        self.service_list = list(self.services.keys())
        
    def translate_text(self, text, target_lang='tr', source_lang='auto'):
        """
        Translate text using multiple free services with failover
        """
        max_attempts = len(self.service_list)
        
        for attempt in range(max_attempts):
            service_name = self.service_list[self.current_service]
            
            try:
                result = self.services[service_name](text, target_lang, source_lang)
                if result and len(result.strip()) > 0:
                    return result
                    
            except Exception as e:
                print(f"Translation failed with {service_name}: {e}")
            
            # Rotate to next service
            self.current_service = (self.current_service + 1) % len(self.service_list)
            time.sleep(1)  # Brief pause between attempts
        
        return text  # Return original if all services fail
    
    def _google_translate_free(self, text, target_lang, source_lang):
        """
        Free Google Translate (web scraping method)
        """
        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': source_lang,
            'tl': target_lang,
            'dt': 't',
            'q': text
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            translated_text = ''.join([x[0] for x in result[0]])
            return translated_text
        
        raise Exception(f"Google Translate failed: {response.status_code}")
    
    def _mymemory_translate(self, text, target_lang, source_lang):
        """
        MyMemory API - 10k words/day free
        """
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': text,
            'langpair': f'{source_lang}|{target_lang}'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('responseData', {}).get('translatedText'):
                return data['responseData']['translatedText']
        
        raise Exception(f"MyMemory failed: {response.status_code}")
    
    def _libretranslate(self, text, target_lang, source_lang):
        """
        LibreTranslate - Self-hosted or public instances
        """
        # Public LibreTranslate instances (free but limited)
        instances = [
            "https://libretranslate.de",
            "https://translate.argosopentech.com",
            "https://libretranslate.com"
        ]
        
        for instance in instances:
            try:
                url = f"{instance}/translate"
                data = {
                    'q': text,
                    'source': source_lang if source_lang != 'auto' else 'en',
                    'target': target_lang,
                    'format': 'text'
                }
                
                response = requests.post(url, json=data, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('translatedText', '')
                    
            except Exception as e:
                continue
        
        raise Exception("All LibreTranslate instances failed")
    
    def translate_news_content(self, news_item):
        """
        Translate news item with smart content handling
        """
        if news_item.get('language') == 'tr':
            # Turkish to English
            translated_item = news_item.copy()
            translated_item['title_en'] = self.translate_text(
                news_item['title'], 'en', 'tr'
            )
            translated_item['summary_en'] = self.translate_text(
                news_item['summary'], 'en', 'tr'
            )
            translated_item['language'] = 'both'
            
        else:
            # Other language to Turkish
            translated_item = news_item.copy()
            translated_item['title_tr'] = self.translate_text(
                news_item['title'], 'tr', 'auto'
            )
            translated_item['summary_tr'] = self.translate_text(
                news_item['summary'], 'tr', 'auto'
            )
            translated_item['language'] = 'both'
        
        return translated_item
    
    def smart_translate_batch(self, news_items, batch_size=5):
        """
        Batch translate with rate limiting
        """
        translated_items = []
        
        for i in range(0, len(news_items), batch_size):
            batch = news_items[i:i+batch_size]
            
            for item in batch:
                try:
                    translated = self.translate_news_content(item)
                    translated_items.append(translated)
                    
                    # Random delay to avoid rate limits
                    time.sleep(random.uniform(0.5, 2.0))
                    
                except Exception as e:
                    print(f"Translation error for item: {e}")
                    translated_items.append(item)  # Keep original
            
            # Longer pause between batches
            if i + batch_size < len(news_items):
                time.sleep(random.uniform(3, 8))
        
        return translated_items

# Test the translation manager
if __name__ == "__main__":
    translator = TranslationManager()
    
    # Test translations
    test_en = "Manchester United signs new striker from Brazil"
    test_tr = "Galatasaray yeni transferini açıkladı"
    
    print("English to Turkish:", translator.translate_text(test_en, 'tr'))
    print("Turkish to English:", translator.translate_text(test_tr, 'en'))