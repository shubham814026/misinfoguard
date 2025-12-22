import spacy
import re
from typing import List, Dict
import logging
from langdetect import detect
from textblob import TextBlob

logger = logging.getLogger(__name__)


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
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {str(e)}")
            raise
    
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
