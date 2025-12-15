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
        results = []
        
        for claim in claims:
            claim_text = claim.get('text', '')
            
            if not claim_text:
                continue
            
            result = await self._check_single_claim(claim_text, claim)
            results.append(result)
        
        return results
    
    async def _check_single_claim(self, claim_text: str, claim_meta: Dict) -> Dict:
        """Check a single claim"""
        try:
            # Search Google for evidence
            search_results = await self._google_search(claim_text)
            
            # Check Google Fact Check API
            fact_check_results = await self._google_fact_check(claim_text)
            
            # Analyze results
            analysis = self._analyze_evidence(
                claim_text,
                search_results,
                fact_check_results,
                claim_meta
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Fact-checking failed for claim: {str(e)}")
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
            relevance = self._calculate_relevance(claim_text, snippet)
            
            if relevance > 0.3:
                credibility_scores.append(credibility)
                sources.append({
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'credibility': credibility,
                    'source_name': self._extract_domain(url)
                })
        
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
        avg_credibility = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0.5
        
        # Determine if claim is more likely true or false
        if fact_check_verdict:
            if any(word in fact_check_verdict for word in ['false', 'wrong', 'incorrect', 'fake']):
                verdict = "LIKELY FALSE"
                confidence = 0.85
            elif any(word in fact_check_verdict for word in ['true', 'correct', 'accurate']):
                verdict = "LIKELY TRUE"
                confidence = 0.85
            else:
                verdict = "LIKELY FALSE" if avg_credibility < 0.5 else "LIKELY TRUE"
                confidence = 0.65
        else:
            # No fact check data, rely on source credibility
            if avg_credibility >= 0.7 and red_flag_count == 0:
                verdict = "LIKELY TRUE"
                confidence = min(0.75, avg_credibility + 0.1)
            elif avg_credibility < 0.4 or red_flag_count > 0:
                verdict = "LIKELY FALSE"
                confidence = 0.70
            elif red_flag_count > 0:
                verdict = "LIKELY FALSE"
                confidence = 0.75
            else:
                # Slightly favor one side to avoid neutral
                verdict = "LIKELY TRUE" if avg_credibility >= 0.55 else "LIKELY FALSE"
                confidence = abs(avg_credibility - 0.5) + 0.5
        
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
        else:
            explanations.append("Based on our analysis, this claim appears to be accurate.")
        
        return " ".join(explanations)
    
    def _create_fallback_result(self, claim_text: str, claim_meta: Dict) -> Dict:
        """Create fallback result when fact-checking fails"""
        return {
            'claim': claim_text,
            'verdict': "LIKELY FALSE",
            'confidence': 50.0,
            'explanation': "Unable to verify this claim due to limited information. Exercise caution.",
            'sources': [],
            'total_sources_found': 0,
            'red_flags': 0,
            'timestamp': datetime.now().isoformat()
        }
