import spacy
import re
from typing import List, Dict, Tuple
import logging
from langdetect import detect
from textblob import TextBlob

logger = logging.getLogger(__name__)


class NewsContentClassifier:
    """
    Classifier to determine if content is actual news/claims or non-news content.
    Uses keyword analysis, structure patterns, and entity detection.
    IMPORTANT: This classifier is intentionally LENIENT - we prefer to fact-check
    content that might not be news rather than reject actual news.
    """
    
    def __init__(self):
        # News-related keywords and patterns (expanded list)
        self.news_keywords = [
            # English - common news words
            'reported', 'announced', 'according to', 'officials', 'government',
            'police', 'minister', 'president', 'election', 'breaking', 'update',
            'statement', 'investigation', 'sources', 'confirmed', 'denied',
            'claims', 'alleged', 'incident', 'protest', 'accident', 'court',
            'verdict', 'arrested', 'released', 'spokesperson', 'authority',
            'crisis', 'emergency', 'parliament', 'congress', 'senate',
            'news', 'report', 'today', 'yesterday', 'says', 'said',
            'death', 'killed', 'injured', 'attack', 'war', 'military',
            'economy', 'market', 'stock', 'price', 'inflation', 'tax',
            'health', 'covid', 'virus', 'vaccine', 'hospital', 'doctor',
            'school', 'university', 'education', 'students', 'teacher',
            'india', 'china', 'usa', 'america', 'russia', 'pakistan',
            'modi', 'trump', 'biden', 'putin', 'leader', 'pm', 'cm',
            # Hindi
            'समाचार', 'रिपोर्ट', 'घोषणा', 'सरकार', 'पुलिस', 'मंत्री', 'चुनाव',
            'खबर', 'आज', 'कल', 'बताया', 'कहा', 'मोदी', 'भारत',
            # Spanish  
            'informó', 'anunció', 'gobierno', 'policía', 'elección', 'noticia',
            # Common news source references
            'reuters', 'ap news', 'bbc', 'cnn', 'times', 'post', 'guardian',
            'ndtv', 'zee', 'aaj tak', 'india today', 'hindustan', 'dainik'
        ]
        
        # Patterns indicating news structure
        self.news_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # Dates like 12/28/2025
            r'\b\d{4}\b',  # Years like 2025
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'"\s*[^"]{5,}\s*"',  # Quoted statements (shorter quotes too)
            r'\b\d+\s*(percent|%|million|billion|thousand|crore|lakh|rupee|dollar)\b',
            r'\b(said|stated|told|announced|reported|claimed|added|mentioned)\b',
            r'\b(according to|sources say|officials said)\b',
            r'\b(breaking|exclusive|just in|update|alert)\b',
            r'@\w+',  # Twitter/social media handles (news often has these)
        ]
        
        # Non-news content indicators - ONLY STRONG INDICATORS
        # We want to be very careful not to reject actual news
        self.non_news_indicators = [
            # Personal/casual content - STRONG indicators only
            'selfie', 'my photo', 'pic of me', 'thats me',
            # Memes/entertainment - STRONG indicators
            'lmao', 'rofl', 'this meme', 'funny meme',
            # Commercial content - STRONG indicators
            'buy now', 'order now', 'limited offer', 'shop now', 'dm to order',
            # Food/lifestyle - STRONG indicators  
            'my recipe', 'homemade recipe', 'cooking tutorial',
            # Greetings - STRONG indicators
            'good morning everyone', 'good night everyone', 'happy birthday to',
        ]
        
        # Minimum thresholds - VERY LENIENT
        self.min_word_count = 10  # Lowered from 15
    
    def classify_content(self, text: str, entities: List[Dict] = None) -> Tuple[bool, str, float]:
        """
        Classify if content is news/verifiable claim or non-news content.
        IMPORTANT: We are LENIENT - prefer to analyze content rather than reject it.
        Only reject if we're very confident it's not news.
        
        Returns:
            Tuple of (is_news, content_type, confidence)
            - is_news: True if content is news/verifiable claim
            - content_type: Description of content type
            - confidence: Confidence score 0-1
        """
        if not text or len(text.strip()) < 10:
            return False, "empty_content", 0.95
        
        text_lower = text.lower()
        words = text.split()
        word_count = len(words)
        
        # LENIENT APPROACH: If text has 20+ words, assume it's worth analyzing
        # unless there are STRONG non-news indicators
        
        # First check for STRONG non-news indicators
        non_news_score = self._calculate_non_news_score(text_lower)
        
        # Only reject if VERY confident it's non-news (score > 0.7)
        if non_news_score > 0.7:
            content_type = self._identify_non_news_type(text_lower)
            return False, content_type, non_news_score
        
        # If we have substantial text (20+ words), treat as news
        if word_count >= 20:
            return True, "news_content", 0.7
        
        # For shorter text, check news indicators
        news_score = self._calculate_news_score(text_lower, entities or [], word_count)
        
        # LENIENT thresholds
        if news_score >= 0.15:  # Very low threshold
            return True, "news_content", max(0.5, news_score)
        elif word_count >= 10:
            # Even with low news score, 10+ words is worth analyzing
            return True, "possible_news", 0.4
        elif word_count < 10:
            return False, "insufficient_content", 0.6
        else:
            # Default to treating as news - better to analyze than reject
            return True, "possible_news", 0.4
    
    def _calculate_news_score(self, text_lower: str, entities: List[Dict], word_count: int) -> float:
        """Calculate how likely this is news content"""
        score = 0.0
        
        # Check for news keywords
        keyword_matches = sum(1 for kw in self.news_keywords if kw in text_lower)
        score += min(0.3, keyword_matches * 0.05)
        
        # Check for news patterns
        pattern_matches = sum(1 for pattern in self.news_patterns 
                             if re.search(pattern, text_lower, re.IGNORECASE))
        score += min(0.3, pattern_matches * 0.06)
        
        # Check for named entities (PERSON, ORG, GPE, DATE, EVENT)
        news_entities = [e for e in entities 
                        if e.get('type') in ['PERSON', 'ORG', 'GPE', 'DATE', 'EVENT', 'LOC']]
        score += min(0.25, len(news_entities) * 0.05)
        
        # Word count factor
        if word_count >= 30:
            score += 0.1
        elif word_count >= 20:
            score += 0.05
        
        # Check for quoted content (indicates sources/statements)
        quotes = re.findall(r'"[^"]{10,}"', text_lower)
        score += min(0.1, len(quotes) * 0.05)
        
        return min(1.0, score)
    
    def _calculate_non_news_score(self, text_lower: str) -> float:
        """
        Calculate how likely this is non-news content.
        CONSERVATIVE: Only give high score for STRONG indicators.
        """
        score = 0.0
        
        # Check for STRONG non-news indicators only
        indicator_matches = sum(1 for ind in self.non_news_indicators if ind in text_lower)
        
        # Need at least 2 strong indicators to consider as non-news
        if indicator_matches >= 2:
            score += min(0.5, indicator_matches * 0.2)
        elif indicator_matches == 1:
            score += 0.15
        
        # Check for excessive emojis (5+ emoji clusters = likely not news)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(text_lower)
        if len(emojis) > 5:  # Raised threshold
            score += 0.25
        
        # Check for excessive hashtags (8+ = likely not news)
        hashtag_count = len(re.findall(r'#\w+', text_lower))
        if hashtag_count > 8:
            score += 0.2
        
        # Very short text with no substance
        words = text_lower.split()
        if len(words) < 5:
            score += 0.3
        
        return min(1.0, score)
    
    def _identify_non_news_type(self, text_lower: str) -> str:
        """Identify the specific type of non-news content"""
        if any(kw in text_lower for kw in ['selfie', 'my photo', 'me and', 'pic of me']):
            return "personal_photo"
        elif any(kw in text_lower for kw in ['meme', 'funny', 'joke', 'lol', 'lmao']):
            return "meme_entertainment"
        elif any(kw in text_lower for kw in ['buy now', 'order', 'discount', 'sale', 'offer']):
            return "advertisement"
        elif any(kw in text_lower for kw in ['recipe', 'delicious', 'yummy', 'cooking']):
            return "food_lifestyle"
        elif any(kw in text_lower for kw in ['motivational', 'inspirational', 'quote']):
            return "motivational_quote"
        elif any(kw in text_lower for kw in ['good morning', 'good night', 'birthday']):
            return "greeting_social"
        else:
            return "non_news_content"


class NLPService:
    """Service for NLP analysis and claim extraction with multilingual support"""
    
    def __init__(self):
        try:
            # Load multilingual spaCy model
            # This supports 100+ languages
            try:
                self.nlp = spacy.load("xx_ent_wiki_sm")  # Multilingual model
                # Add sentencizer for sentence boundary detection
                if 'sentencizer' not in self.nlp.pipe_names:
                    self.nlp.add_pipe('sentencizer')
                logger.info("Loaded multilingual spaCy model: xx_ent_wiki_sm")
            except OSError:
                # Fallback to English model if multilingual not available
                logger.warning("Multilingual model not found, falling back to English model")
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    if 'sentencizer' not in self.nlp.pipe_names:
                        self.nlp.add_pipe('sentencizer')
                    logger.info("Loaded English spaCy model: en_core_web_sm")
                except OSError:
                    raise OSError(
                        "No spaCy models found. Please install: "
                        "python -m spacy download xx_ent_wiki_sm OR python -m spacy download en_core_web_sm"
                    )
            
            self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'ru', 'zh', 'ja', 'ar', 'hi']
            
            # Initialize content classifier
            self.content_classifier = NewsContentClassifier()
            
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {str(e)}")
            raise
    
    def classify_content(self, text: str, entities: List[Dict] = None) -> Dict:
        """
        Classify if content is news/verifiable claim or non-news content.
        
        Returns:
            Dict with is_news, content_type, confidence, and message
        """
        is_news, content_type, confidence = self.content_classifier.classify_content(text, entities)
        
        # Generate user-friendly message based on content type
        messages = {
            "empty_content": "The image doesn't contain readable text. Please upload an image with news or text content.",
            "personal_photo": "This appears to be a personal photo, not news content. Please upload news articles, screenshots of news, or text claims to verify.",
            "meme_entertainment": "This appears to be a meme or entertainment content, not a news article. Please upload actual news content for fact-checking.",
            "advertisement": "This appears to be an advertisement or promotional content, not news. Please upload news articles or claims to verify.",
            "food_lifestyle": "This appears to be food or lifestyle content, not news. Please upload news articles or claims to verify.",
            "motivational_quote": "This appears to be a motivational quote or inspirational content, not verifiable news. Please upload news articles or claims to verify.",
            "greeting_social": "This appears to be a social greeting or personal message, not news content. Please upload news articles or claims to verify.",
            "non_news_content": "This doesn't appear to be news or a verifiable claim. Please upload news articles, news screenshots, or specific claims to fact-check.",
            "insufficient_content": "The content is too short to analyze. Please upload content with more text or a complete news article.",
            "news_content": "News content detected. Proceeding with fact-checking.",
            "possible_news": "Content may contain news-related information. Proceeding with analysis."
        }
        
        return {
            "is_news": is_news,
            "content_type": content_type,
            "confidence": confidence,
            "message": messages.get(content_type, "Unable to classify content type.")
        }
    
    async def extract_claims(self, text: str) -> List[Dict]:
        """
        Extract factual claims from text (supports multiple languages)
        Groups related sentences about the same topic into single claims
        
        Args:
            text: Input text in any supported language
            
        Returns:
            List of claims with metadata including detected language
        """
        try:
            # Allow shorter text - minimum 5 words
            if not text or len(text.strip().split()) < 5:
                return []
            
            # Detect language
            detected_lang = self.detect_language(text)
            logger.info(f"Detected language: {detected_lang}")
            
            # For short text (< 50 words), treat entire text as single claim
            word_count = len(text.split())
            if word_count < 50:
                return [{
                    "text": text.strip(),
                    "language": detected_lang,
                    "entities": [],
                    "sentiment": self._analyze_sentiment(text),
                    "confidence": 0.75
                }]
            
            # For longer text, extract key claims but group related ones
            doc = self.nlp(text)
            
            all_sentences = []
            factual_sentences = []
            
            # First pass: identify factual sentences
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                
                # Filter out very short sentences
                if len(sentence_text.split()) < 5:
                    continue
                
                all_sentences.append(sentence_text)
                
                # Check if sentence contains factual indicators
                if self._is_factual_claim(sentence_text, detected_lang):
                    factual_sentences.append({
                        "text": sentence_text,
                        "entities": self._extract_entities(sent),
                        "sentiment": self._analyze_sentiment(sentence_text),
                        "confidence": self._calculate_confidence(sent)
                    })
            
            # If we have factual sentences, combine related ones about same topic
            if factual_sentences:
                # For articles about single topic (most news), return combined claim
                if len(factual_sentences) <= 3 or self._is_single_topic(factual_sentences):
                    # Combine all factual sentences into one claim
                    combined_text = " ".join([s["text"] for s in factual_sentences])
                    
                    # Merge entities
                    all_entities = []
                    seen_entities = set()
                    for s in factual_sentences:
                        for ent in s["entities"]:
                            ent_key = (ent["text"], ent["type"])
                            if ent_key not in seen_entities:
                                all_entities.append(ent)
                                seen_entities.add(ent_key)
                    
                    return [{
                        "text": combined_text[:1000],  # Limit length
                        "language": detected_lang,
                        "entities": all_entities,
                        "sentiment": self._analyze_sentiment(combined_text),
                        "confidence": sum(s["confidence"] for s in factual_sentences) / len(factual_sentences)
                    }]
                else:
                    # Multiple distinct topics - return top 3 most important claims
                    factual_sentences.sort(key=lambda x: x["confidence"], reverse=True)
                    return [{
                        "text": s["text"],
                        "language": detected_lang,
                        "entities": s["entities"],
                        "sentiment": s["sentiment"],
                        "confidence": s["confidence"]
                    } for s in factual_sentences[:3]]
            
            # No factual claims found - treat entire text as single claim
            return [{
                "text": text[:1000],
                "language": detected_lang,
                "entities": self._extract_entities(doc),
                "sentiment": self._analyze_sentiment(text),
                "confidence": 0.6
            }]
            
        except Exception as e:
            logger.error(f"Claim extraction failed: {str(e)}")
            detected_lang = self.detect_language(text) if text else "en"
            return [{
                "text": text[:1000] if text else "",
                "language": detected_lang,
                "entities": [],
                "sentiment": "neutral",
                "confidence": 0.5
            }]
    
    def _is_single_topic(self, sentences: List[Dict]) -> bool:
        """Check if sentences are about the same topic using entity overlap"""
        if len(sentences) <= 1:
            return True
        
        # Extract all entity texts
        entity_sets = []
        for sent in sentences:
            entities = {ent["text"].lower() for ent in sent["entities"]}
            entity_sets.append(entities)
        
        if not any(entity_sets):
            return True  # No entities to compare
        
        # Calculate average overlap
        total_overlap = 0
        comparisons = 0
        
        for i in range(len(entity_sets)):
            for j in range(i + 1, len(entity_sets)):
                if entity_sets[i] and entity_sets[j]:
                    intersection = len(entity_sets[i] & entity_sets[j])
                    union = len(entity_sets[i] | entity_sets[j])
                    overlap = intersection / union if union > 0 else 0
                    total_overlap += overlap
                    comparisons += 1
        
        avg_overlap = total_overlap / comparisons if comparisons > 0 else 0
        
        # If average overlap > 30%, consider same topic
        return avg_overlap > 0.3
    
    def _is_factual_claim(self, text: str, language: str = 'en') -> bool:
        """Determine if a sentence contains a factual claim (language-agnostic)"""
        # Universal factual indicators that work across languages
        
        # Numbers and dates indicate factual content (universal)
        has_numbers = bool(re.search(r'\d+', text))
        
        # Language-specific factual verbs
        factual_verbs = {
            'en': ['is', 'are', 'was', 'were', 'has', 'have', 'will', 'states', 'shows', 'proves', 'reveals'],
            'es': ['es', 'son', 'fue', 'fueron', 'tiene', 'tienen', 'será', 'muestra', 'prueba', 'revela'],
            'fr': ['est', 'sont', 'était', 'étaient', 'a', 'ont', 'sera', 'montre', 'prouve', 'révèle'],
            'de': ['ist', 'sind', 'war', 'waren', 'hat', 'haben', 'wird', 'zeigt', 'beweist'],
            'hi': ['है', 'हैं', 'था', 'थे', 'दिखाता', 'साबित'],
            'ar': ['هو', 'هي', 'كان', 'كانت', 'يظهر', 'يثبت'],
        }
        
        # Check for factual verbs in detected language (or default to universal check)
        text_lower = text.lower()
        verbs = factual_verbs.get(language, factual_verbs['en'])
        has_factual_verb = any(verb in text_lower for verb in verbs)
        
        # Avoid questions (universal)
        is_question = text.strip().endswith('?') or text.strip().endswith('؟')  # Arabic question mark
        
        # Opinion indicators (multilingual)
        opinion_words = ['think', 'believe', 'feel', 'opinion', 'maybe', 'perhaps',
                        'creo', 'pienso', 'opino', 'quizás',  # Spanish
                        'pense', 'crois', 'opinion', 'peut-être',  # French
                        'denke', 'glaube', 'meinung', 'vielleicht']  # German
        is_opinion = any(word in text_lower for word in opinion_words)
        
        # If has numbers or factual structure, likely a claim
        return (has_numbers or has_factual_verb) and not is_question and not is_opinion
    
    def _extract_entities(self, doc) -> List[Dict]:
        """Extract named entities from text"""
        entities = []
        
        for ent in doc.ents:
            # Focus on relevant entity types
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'EVENT', 'PRODUCT', 'MONEY', 'PERCENT']:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return "positive"
            elif polarity < -0.1:
                return "negative"
            else:
                return "neutral"
        except:
            return "neutral"
    
    def _calculate_confidence(self, doc) -> float:
        """Calculate confidence score for claim"""
        # Higher confidence for sentences with:
        # - Named entities
        # - Numbers
        # - Longer length
        
        num_entities = len([ent for ent in doc.ents])
        has_numbers = bool(re.search(r'\d+', doc.text))
        word_count = len([token for token in doc if not token.is_punct])
        
        confidence = 0.5
        
        if num_entities > 0:
            confidence += min(0.2, num_entities * 0.05)
        
        if has_numbers:
            confidence += 0.15
        
        if word_count > 10:
            confidence += 0.1
        
        return min(0.95, confidence)
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            return detect(text)
        except:
            return "en"
