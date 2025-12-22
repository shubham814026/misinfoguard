import os
import aiohttp
import logging
from typing import List, Dict
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class FactChecker:
    """Service for fact-checking claims using Google APIs"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cx_id = os.getenv("GOOGLE_CX_ID")
        
        # Trusted news sources for credibility scoring
        self.trusted_sources = {
            'reuters.com': 0.95,
            'apnews.com': 0.95,
            'bbc.com': 0.92,
            'npr.org': 0.90,
            'nytimes.com': 0.88,
            'washingtonpost.com': 0.88,
            'theguardian.com': 0.87,
            'wsj.com': 0.87,
            'cnn.com': 0.85,
            'bloomberg.com': 0.85,
            'factcheck.org': 0.98,
            'snopes.com': 0.95,
            'politifact.com': 0.96,
            'who.int': 0.97,
            'cdc.gov': 0.97,
            'nature.com': 0.96,
            'science.org': 0.96
        }
        
        # Keywords indicating misinformation
        self.red_flags = [
            'secret', 'they don\'t want you to know',
            'doctors hate', 'shocking truth',
            'miracle cure', 'guaranteed',
            'breaking news exclusive', 'this one trick'
        ]
    
    async def check_claims(self, claims: List[Dict]) -> List[Dict]:
        """
        Check multiple claims and return results
        
        Args:
            claims: List of claim dictionaries
            
        Returns:
            List of fact-check results
        """
        logger.info(f"Starting fact-check for {len(claims)} claim(s)")
        results = []
        
        for idx, claim in enumerate(claims):
            claim_text = claim.get('text', '')
            
            if not claim_text:
                logger.warning(f"Claim {idx+1}: Empty claim text, skipping")
                continue
            
            logger.info(f"Claim {idx+1}: Checking '{claim_text[:100]}...'")
            result = await self._check_single_claim(claim_text, claim)
            results.append(result)
            logger.info(f"Claim {idx+1}: Verdict = {result.get('verdict')}, Confidence = {result.get('confidence')}%")
        
        logger.info(f"Fact-check completed: {len(results)} results")
        return results
    
    async def _check_single_claim(self, claim_text: str, claim_meta: Dict) -> Dict:
        """Check a single claim"""
        try:
            logger.info(f"Creating search query from {len(claim_text.split())} words")
            
            # Create optimized search query (max 10-15 words for better results)
            search_query = self._create_search_query(claim_text, claim_meta)
            logger.info(f"Search query: '{search_query}'")
            
            # Search Google for evidence
            logger.info(f"Searching Google with query: '{search_query}'")
            search_results = await self._google_search(search_query)
            logger.info(f"Google Search returned {len(search_results)} results")
            
            # Check Google Fact Check API (also use optimized query)
            logger.info(f"Checking Google Fact Check API")
            fact_check_results = await self._google_fact_check(search_query)
            logger.info(f"Fact Check API returned {len(fact_check_results)} results")
            
            # Analyze results
            analysis = self._analyze_evidence(
                claim_text,
                search_results,
                fact_check_results,
                claim_meta
            )
            
            logger.info(f"Analysis complete: {analysis.get('verdict')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Fact-checking failed for claim: {str(e)}", exc_info=True)
            return self._create_fallback_result(claim_text, claim_meta)
    
    async def _google_search(self, query: str) -> List[Dict]:
        """Search Google Custom Search API"""
        if not self.google_api_key or not self.google_cx_id:
            logger.warning("Google API credentials not configured")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cx_id,
                'q': query,
                'num': 10
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('items', [])
                    else:
                        logger.error(f"Google Search API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Google Search failed: {str(e)}")
            return []
    
    def _create_search_query(self, claim_text: str, claim_meta: Dict) -> str:
        """
        Create optimized search query from claim text
        Extracts key entities and important words, limits to ~10 words
        """
        # If claim is short (< 15 words), use as-is
        words = claim_text.split()
        if len(words) <= 15:
            return claim_text
        
        # Strategy 1: Use first sentence if it's concise (max 12 words)
        sentences = claim_text.split('.')
        first_sentence = sentences[0].strip()
        first_sent_words = first_sentence.split()
        if len(first_sent_words) <= 12:
            # First sentence is good, use it
            logger.info(f"Using first sentence ({len(first_sent_words)} words)")
            return first_sentence
        
        # Strategy 2: Extract key information
        # Extract entities (people, organizations, locations, dates)
        entities = claim_meta.get('entities', [])
        entity_texts = [ent['text'] for ent in entities if ent['type'] in ['PERSON', 'ORG', 'GPE', 'EVENT', 'DATE']]
        
        # Extract ALL capitalized words and phrases (entities, proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', claim_text)
        
        # Extract numbers and dates
        numbers = re.findall(r'\b(?:\d{1,2}\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December|\d+)\b', claim_text)
        
        # Find quoted text (important statements)
        quotes = re.findall(r'"([^"]+)"', claim_text)
        
        # Combine unique important terms
        important_terms = []
        seen = set()
        
        # Priority 1: Entities from NLP (highest priority)
        for entity in entity_texts[:4]:  # Max 4 entities
            if entity.lower() not in seen:
                important_terms.append(entity)
                seen.add(entity.lower())
        
        # Priority 2: Capitalized words (likely proper nouns)
        for cap in capitalized[:5]:
            if cap.lower() not in seen:
                important_terms.append(cap)
                seen.add(cap.lower())
        
        # Priority 3: Dates and numbers
        for num in numbers[:2]:
            if num not in important_terms:
                important_terms.append(num)
        
        # Priority 4: Key action words from the text
        action_words = ['protest', 'announced', 'said', 'reported', 'claims', 'election', 
                       'government', 'security', 'attack', 'fled', 'exile', 'summoned']
        text_lower = claim_text.lower()
        for action in action_words:
            if action in text_lower and action not in seen:
                important_terms.append(action)
                seen.add(action)
                if len(important_terms) >= 12:
                    break
        
        # Build query
        if important_terms and len(important_terms) >= 3:
            query = ' '.join(important_terms[:15])  # Max 15 terms
            logger.info(f"Optimized search query ({len(important_terms)} terms): '{query}'")
        else:
            # Fallback: Extract most important words from first 50 words
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
                         'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 
                         'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 
                         'could', 'may', 'might', 'must', 'can', 'it', 'its', 'this', 'that'}
            
            first_50_words = ' '.join(words[:50])
            important_words = [w for w in first_50_words.split() 
                             if w.lower() not in stop_words and len(w) > 3]
            query = ' '.join(important_words[:12])
            logger.info(f"Fallback search query: '{query}'")
        
        return query
    
    async def _google_fact_check(self, query: str) -> List[Dict]:
        """Query Google Fact Check Tools API"""
        if not self.google_api_key:
            logger.warning("Google API key not configured")
            return []
        
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                'key': self.google_api_key,
                'query': query,
                'languageCode': 'en'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('claims', [])
                    else:
                        logger.error(f"Fact Check API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Fact Check API failed: {str(e)}")
            return []
    
    def _analyze_evidence(
        self,
        claim_text: str,
        search_results: List[Dict],
        fact_check_results: List[Dict],
        claim_meta: Dict
    ) -> Dict:
        """Analyze all evidence and generate verdict"""
        
        # Calculate credibility scores
        credibility_scores = []
        sources = []
        
        # Analyze search results
        for result in search_results[:10]:
            url = result.get('link', '')
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            credibility = self._calculate_source_credibility(url)
            relevance = self._calculate_relevance(claim_text, snippet + ' ' + title)
            
            logger.debug(f"Source: {url[:50]}... | Credibility: {credibility:.2f} | Relevance: {relevance:.2f}")
            
            # Lower relevance threshold for better results
            if relevance > 0.15:  # Reduced from 0.3 to 0.15
                credibility_scores.append(credibility)
                sources.append({
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'credibility': credibility,
                    'relevance': relevance,
                    'source_name': self._extract_domain(url)
                })
        
        logger.info(f"Found {len(sources)} relevant sources with avg credibility: {sum(credibility_scores)/len(credibility_scores) if credibility_scores else 0:.2f}")
        
        # Analyze fact check results
        fact_check_verdict = None
        if fact_check_results:
            for fc_result in fact_check_results:
                claim_review = fc_result.get('claimReview', [])
                if claim_review:
                    rating = claim_review[0].get('textualRating', '').lower()
                    fact_check_verdict = rating
                    
                    publisher = claim_review[0].get('publisher', {})
                    sources.append({
                        'url': claim_review[0].get('url', ''),
                        'title': f"Fact Check: {fc_result.get('text', '')}",
                        'snippet': f"Rating: {rating}",
                        'credibility': 0.95,
                        'source_name': publisher.get('name', 'Fact Checker')
                    })
        
        # Check for red flags
        red_flag_count = sum(
            1 for flag in self.red_flags
            if flag.lower() in claim_text.lower()
        )
        
        # Calculate final verdict
        avg_credibility = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0.6
        
        # Determine if claim is more likely true or false
        if fact_check_verdict:
            if any(word in fact_check_verdict for word in ['false', 'wrong', 'incorrect', 'fake']):
                verdict = "LIKELY FALSE"
                confidence = 0.85
            elif any(word in fact_check_verdict for word in ['true', 'correct', 'accurate']):
                verdict = "LIKELY TRUE"
                confidence = 0.85
            else:
                verdict = "NEEDS VERIFICATION"
                confidence = 0.60
        else:
            # No fact check data, rely on source credibility and analysis
            if not credibility_scores:
                # No sources found - use neutral stance
                verdict = "NEEDS VERIFICATION"
                confidence = 0.50
            elif avg_credibility >= 0.7 and red_flag_count == 0:
                verdict = "LIKELY TRUE"
                confidence = min(0.80, avg_credibility + 0.1)
            elif avg_credibility >= 0.6 and red_flag_count == 0:
                verdict = "LIKELY TRUE"
                confidence = 0.65
            elif avg_credibility < 0.4 or red_flag_count > 1:
                verdict = "LIKELY FALSE"
                confidence = 0.70
            elif red_flag_count > 0:
                verdict = "LIKELY FALSE"
                confidence = 0.65
            else:
                # Moderate credibility - default to verification needed
                verdict = "NEEDS VERIFICATION"
                confidence = 0.55
        
        # Generate explanation
        explanation = self._generate_explanation(
            verdict,
            avg_credibility,
            len(sources),
            red_flag_count,
            fact_check_verdict
        )
        
        # Sort sources by credibility
        sources.sort(key=lambda x: x['credibility'], reverse=True)
        
        return {
            'claim': claim_text,
            'verdict': verdict,
            'confidence': round(confidence * 100, 1),
            'explanation': explanation,
            'sources': sources[:5],  # Top 5 sources
            'total_sources_found': len(sources),
            'red_flags': red_flag_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_source_credibility(self, url: str) -> float:
        """Calculate credibility score for a source URL"""
        domain = self._extract_domain(url)
        
        # Check if in trusted sources
        for trusted_domain, score in self.trusted_sources.items():
            if trusted_domain in domain:
                return score
        
        # Default credibility based on TLD
        if domain.endswith('.gov'):
            return 0.90
        elif domain.endswith('.edu'):
            return 0.85
        elif domain.endswith('.org'):
            return 0.70
        else:
            return 0.60
    
    def _calculate_relevance(self, claim: str, snippet: str) -> float:
        """Calculate how relevant a search result is to the claim"""
        claim_words = set(claim.lower().split())
        snippet_words = set(snippet.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        claim_words -= common_words
        snippet_words -= common_words
        
        if not claim_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(claim_words & snippet_words)
        union = len(claim_words | snippet_words)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else url
    
    def _generate_explanation(
        self,
        verdict: str,
        credibility: float,
        source_count: int,
        red_flags: int,
        fact_check: str
    ) -> str:
        """Generate human-friendly explanation"""
        
        explanations = []
        
        if fact_check:
            if 'false' in fact_check.lower():
                explanations.append("Professional fact-checkers have rated this claim as false.")
            elif 'true' in fact_check.lower():
                explanations.append("Professional fact-checkers have verified this claim as true.")
        
        if source_count > 0:
            if credibility >= 0.8:
                explanations.append(f"Found {source_count} highly credible sources supporting this assessment.")
            elif credibility >= 0.6:
                explanations.append(f"Found {source_count} moderately credible sources.")
            else:
                explanations.append(f"Limited credible sources found ({source_count} sources analyzed).")
        else:
            explanations.append("No credible sources found to verify this claim.")
        
        if red_flags > 0:
            explanations.append(f"The claim contains {red_flags} red flag(s) commonly associated with misinformation.")
        
        if verdict == "LIKELY FALSE":
            explanations.append("Based on our analysis, this claim appears to be misleading or false.")
        elif verdict == "LIKELY TRUE":
            explanations.append("Based on our analysis, this claim appears to be accurate.")
        else:  # NEEDS VERIFICATION
            explanations.append("Unable to determine accuracy with confidence. Manual verification recommended.")
        
        return " ".join(explanations)
    
    def _create_fallback_result(self, claim_text: str, claim_meta: Dict) -> Dict:
        """Create fallback result when fact-checking fails - uses heuristic analysis"""
        
        # Check for red flags
        red_flag_count = sum(
            1 for flag in self.red_flags
            if flag.lower() in claim_text.lower()
        )
        
        # Check sentiment (negative/extreme sentiment often indicates misinformation)
        sentiment = claim_meta.get('sentiment', 'neutral')
        
        # Check for numbers/statistics (claims with specific numbers are more verifiable)
        has_numbers = bool(re.search(r'\d+', claim_text))
        
        # Check for entities (claims with entities are more concrete)
        entities = claim_meta.get('entities', [])
        has_entities = len(entities) > 0
        
        # Heuristic scoring (without API)
        base_confidence = 50
        
        # Adjust based on red flags (strong indicator)
        if red_flag_count > 0:
            verdict = "LIKELY FALSE"
            confidence = 70 + (red_flag_count * 5)  # Higher red flags = higher confidence it's false
            explanation = f"This claim contains {red_flag_count} red flag(s) commonly found in misinformation. " \
                         f"Exercise extreme caution. Fact-checking APIs unavailable - manual verification recommended."
        
        # Claims with extreme sentiment but no verifiable details
        elif sentiment in ['positive', 'negative'] and not has_numbers and not has_entities:
            verdict = "LIKELY FALSE"
            confidence = 60
            explanation = "This claim uses emotional language without specific verifiable details. " \
                         "Fact-checking APIs unavailable - manual verification recommended."
        
        # Claims with concrete details (numbers, entities)
        elif has_numbers and has_entities:
            verdict = "NEEDS VERIFICATION"
            confidence = 50
            explanation = "This claim contains specific details that can be verified. " \
                         "Fact-checking APIs unavailable - please verify through trusted news sources."
        
        # Generic claims
        else:
            verdict = "NEEDS VERIFICATION"
            confidence = 50
            explanation = "Unable to verify this claim automatically. " \
                         "Fact-checking APIs unavailable - please check trusted news sources manually."
        
        return {
            'claim': claim_text,
            'verdict': verdict,
            'confidence': min(confidence, 100),
            'explanation': explanation,
            'sources': [],
            'total_sources_found': 0,
            'red_flags': red_flag_count,
            'heuristic_analysis': {
                'has_numbers': has_numbers,
                'has_entities': has_entities,
                'sentiment': sentiment,
                'api_available': False
            },
            'timestamp': datetime.now().isoformat()
        }
