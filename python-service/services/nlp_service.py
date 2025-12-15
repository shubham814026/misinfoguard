import spacy
import re
from typing import List, Dict
import logging
from langdetect import detect
from textblob import TextBlob

logger = logging.getLogger(__name__)


class NLPService:
    """Service for NLP analysis and claim extraction"""
    
    def __init__(self):
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {str(e)}")
            raise
    
    async def extract_claims(self, text: str) -> List[Dict]:
        """
        Extract factual claims from text
        
        Args:
            text: Input text
            
        Returns:
            List of claims with metadata
        """
        try:
            if not text or len(text.strip()) < 10:
                return []
            
            # Process text with spaCy
            doc = self.nlp(text)
            
            claims = []
            
            # Extract sentences
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                
                # Filter out very short sentences
                if len(sentence_text.split()) < 5:
                    continue
                
                # Check if sentence contains factual indicators
                if self._is_factual_claim(sentence_text):
                    claim = {
                        "text": sentence_text,
                        "entities": self._extract_entities(sent),
                        "sentiment": self._analyze_sentiment(sentence_text),
                        "confidence": self._calculate_confidence(sent)
                    }
                    claims.append(claim)
            
            # If no claims found but text is substantial, treat entire text as claim
            if not claims and len(text.split()) > 10:
                claims.append({
                    "text": text[:500],  # Limit length
                    "entities": self._extract_entities(doc),
                    "sentiment": self._analyze_sentiment(text),
                    "confidence": 0.7
                })
            
            return claims
            
        except Exception as e:
            logger.error(f"Claim extraction failed: {str(e)}")
            return [{
                "text": text[:500],
                "entities": [],
                "sentiment": "neutral",
                "confidence": 0.5
            }]
    
    def _is_factual_claim(self, text: str) -> bool:
        """Determine if a sentence contains a factual claim"""
        # Factual indicators
        factual_verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'will', 'states', 'shows', 'proves', 'reveals']
        
        # Numbers and dates indicate factual content
        has_numbers = bool(re.search(r'\d+', text))
        
        # Check for factual verbs
        text_lower = text.lower()
        has_factual_verb = any(verb in text_lower for verb in factual_verbs)
        
        # Avoid questions and opinions
        is_question = text.strip().endswith('?')
        is_opinion = any(word in text_lower for word in ['think', 'believe', 'feel', 'opinion', 'maybe', 'perhaps'])
        
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
