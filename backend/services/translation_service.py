from typing import Dict, Any, Optional
import json
import hashlib
from datetime import datetime, timedelta
import os

class TranslationService:
    def __init__(self):
        self.cache_dir = "translation_cache"
        self.cache_expiry_days = 30

        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # Technical terminology dictionary (English to Urdu)
        self.technical_terms = {
            "ROS 2": "آر او ایس 2",
            "Robot Operating System": "روبوٹ آپریٹنگ سسٹم",
            "Gazebo": "گیزیبو",
            "Unity": "یونٹی",
            "NVIDIA Isaac": "این ویڈیا آئزک",
            "Vision-Language-Action": "ویژن-زبان-ایکشن",
            "Physical AI": "فزیکل اے آئی",
            "Humanoid Robotics": "ہیومینائیڈ روبوٹکس",
            "Digital Twin": "ڈیجیٹل ٹوئن",
            "Physics Simulation": "فزکس سیمولیشن",
            "Machine Learning": "مشین لرننگ",
            "Deep Learning": "ڈیپ لرننگ",
            "Neural Network": "نیورل نیٹ ورک",
            "Computer Vision": "کمپیوٹر ویژن",
            "Natural Language Processing": "نیچرل لینگوئج پروسیسنگ",
            "API": "اے پی آئی",
            "JSON": "جے ایس او این",
            "XML": "ایکس ایم ایل",
            "Python": "پائتھون",
            "JavaScript": "جاوا اسکرپٹ",
            "React": "ری ایکٹ",
            "FastAPI": "فاسٹ اے پی آئی",
            "PostgreSQL": "پوسٹگریس کیو ایل",
            "Qdrant": "کیوڈرنٹ",
            "OpenAI": "اوپن اے آئی",
            "Chatbot": "چیٹ بوٹ",
            "Authentication": "آتھینٹیکیشن",
            "Personalization": "پرسنلائزیشن",
            "Translation": "ترجمہ",
            "Embedding": "ایمبیڈنگ",
            "Vector Database": "ویکٹر ڈیٹا بیس",
            "RAG": "آر اے جی",
            "Retrieval-Augmented Generation": "ریٹریول-اگمنٹڈ جنریشن"
        }

    def _get_cache_key(self, text: str, target_lang: str) -> str:
        """Generate cache key for text and target language."""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{target_lang}_{text_hash}.json"

    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load translation from cache if exists and not expired."""
        cache_path = os.path.join(self.cache_dir, cache_key)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Check if cache is expired
            cached_at = datetime.fromisoformat(cache_data.get('cached_at', '2000-01-01'))
            expiry_date = cached_at + timedelta(days=self.cache_expiry_days)

            if datetime.now() > expiry_date:
                os.remove(cache_path)
                return None

            return cache_data

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None

    def _save_to_cache(self, cache_key: str, original_text: str, translated_text: str, target_lang: str):
        """Save translation to cache."""
        cache_path = os.path.join(self.cache_dir, cache_key)

        cache_data = {
            'original_text': original_text,
            'translated_text': translated_text,
            'target_lang': target_lang,
            'cached_at': datetime.now().isoformat()
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    def _translate_technical_terms(self, text: str) -> str:
        """Replace technical terms with Urdu equivalents."""
        translated = text

        # Sort terms by length (longest first) to avoid partial matches
        sorted_terms = sorted(self.technical_terms.items(), key=lambda x: len(x[0]), reverse=True)

        for english_term, urdu_term in sorted_terms:
            # Case-insensitive replacement
            translated = translated.replace(english_term, urdu_term)
            translated = translated.replace(english_term.lower(), urdu_term)
            translated = translated.replace(english_term.upper(), urdu_term)

        return translated

    def _mock_translate(self, text: str, target_lang: str = 'ur') -> str:
        """Mock translation for development."""
        if target_lang != 'ur':
            return f"[Mock {target_lang.upper()} translation]: {text}"

        # Simple mock translation with technical term replacement
        urdu_translation = self._translate_technical_terms(text)

        # Add Urdu-like prefix to indicate it's a mock translation
        if len(text) > 50:
            return f"[مترجم - ترجمہ]: {urdu_translation}"
        else:
            return f"[ترجمہ]: {urdu_translation}"

    def translate_text(self, text: str, target_lang: str = 'ur', use_cache: bool = True) -> Dict[str, Any]:
        """Translate text to target language."""
        if not text or not text.strip():
            return {
                'original_text': text,
                'translated_text': text,
                'target_lang': target_lang,
                'from_cache': False,
                'is_mock': True
            }

        # Check cache first
        cache_key = self._get_cache_key(text, target_lang)

        if use_cache:
            cached = self._load_from_cache(cache_key)
            if cached:
                return {
                    'original_text': cached['original_text'],
                    'translated_text': cached['translated_text'],
                    'target_lang': cached['target_lang'],
                    'from_cache': True,
                    'is_mock': False
                }

        # For now, use mock translation
        # In production, replace with actual translation API (Google Translate, DeepL, etc.)
        translated_text = self._mock_translate(text, target_lang)

        # Save to cache
        if use_cache:
            self._save_to_cache(cache_key, text, translated_text, target_lang)

        return {
            'original_text': text,
            'translated_text': translated_text,
            'target_lang': target_lang,
            'from_cache': False,
            'is_mock': True
        }

    def translate_batch(self, texts: list, target_lang: str = 'ur') -> list:
        """Translate multiple texts."""
        return [self.translate_text(text, target_lang) for text in texts]

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages for translation."""
        return {
            'en': 'English',
            'ur': 'Urdu',
            'ar': 'Arabic',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'hi': 'Hindi'
        }

    def clear_cache(self, older_than_days: Optional[int] = None):
        """Clear translation cache."""
        if not os.path.exists(self.cache_dir):
            return

        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                cache_path = os.path.join(self.cache_dir, filename)

                if older_than_days is not None:
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)

                        cached_at = datetime.fromisoformat(cache_data.get('cached_at', '2000-01-01'))
                        expiry_date = cached_at + timedelta(days=older_than_days)

                        if datetime.now() > expiry_date:
                            os.remove(cache_path)
                    except:
                        os.remove(cache_path)
                else:
                    os.remove(cache_path)

# Singleton instance
translation_service = TranslationService()