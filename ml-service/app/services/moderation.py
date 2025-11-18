"""
Content moderation service.

Toxicity detection and content safety analysis.
"""
from typing import Dict, Any, List
import re


class ModerationService:
    """
    Content moderation and safety service.
    
    Detects toxic content, spam, and inappropriate language.
    Note: Uses simple heuristics for MVP. TODO: Integrate proper toxicity model.
    """
    
    def __init__(self):
        """Initialize moderation service."""
        # Simple keyword-based detection for MVP
        self.toxic_keywords = self._load_toxic_keywords()
        print("✅ Moderation service initialized (keyword-based MVP)")
    
    def check_toxicity(self, text: str) -> Dict[str, Any]:
        """
        Check text for toxic content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with toxicity scores and flags
        """
        text_lower = text.lower()
        
        # Count toxic keywords
        toxic_count = sum(
            1 for keyword in self.toxic_keywords
            if keyword in text_lower
        )
        
        # Simple scoring (TODO: Replace with ML model)
        toxicity_score = min(toxic_count / 10.0, 1.0)
        
        is_toxic = toxicity_score > 0.3
        
        return {
            'is_toxic': is_toxic,
            'toxicity_score': toxicity_score,
            'confidence': 0.7,  # Placeholder
            'categories': self._categorize_toxicity(text_lower),
            'action': 'flag_for_review' if is_toxic else 'approve'
        }
    
    def check_spam(self, text: str) -> Dict[str, Any]:
        """
        Check if text appears to be spam.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with spam indicators
        """
        # Simple heuristics
        url_count = len(re.findall(r'http[s]?://\S+', text))
        excessive_caps = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        repeated_chars = bool(re.search(r'(.)\1{4,}', text))
        
        spam_score = 0.0
        if url_count > 2:
            spam_score += 0.4
        if excessive_caps > 0.5:
            spam_score += 0.3
        if repeated_chars:
            spam_score += 0.3
        
        return {
            'is_spam': spam_score > 0.5,
            'spam_score': min(spam_score, 1.0),
            'indicators': {
                'excessive_urls': url_count > 2,
                'excessive_caps': excessive_caps > 0.5,
                'repeated_chars': repeated_chars
            }
        }
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive content analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with toxicity, spam, and safety scores
        """
        toxicity_result = self.check_toxicity(text)
        spam_result = self.check_spam(text)
        
        # Overall safety score
        safety_score = 1.0 - max(
            toxicity_result['toxicity_score'],
            spam_result['spam_score']
        )
        
        return {
            'safety_score': safety_score,
            'is_safe': safety_score > 0.7,
            'toxicity': toxicity_result,
            'spam': spam_result,
            'recommended_action': self._determine_action(toxicity_result, spam_result)
        }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple texts in batch.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of analysis results
        """
        return [self.analyze_content(text) for text in texts]
    
    def _categorize_toxicity(self, text_lower: str) -> List[str]:
        """Categorize types of toxicity detected."""
        categories = []
        
        # Simple category detection (TODO: Improve with ML)
        if any(word in text_lower for word in ['hate', 'stupid', 'idiot']):
            categories.append('insult')
        if any(word in text_lower for word in ['kill', 'die', 'hurt']):
            categories.append('threat')
        if any(word in text_lower for word in ['racist', 'sexist']):
            categories.append('identity_hate')
        
        return categories if categories else ['general']
    
    def _determine_action(
        self,
        toxicity_result: Dict[str, Any],
        spam_result: Dict[str, Any]
    ) -> str:
        """Determine recommended moderation action."""
        if toxicity_result['toxicity_score'] > 0.7 or spam_result['spam_score'] > 0.7:
            return 'block'
        elif toxicity_result['is_toxic'] or spam_result['is_spam']:
            return 'flag_for_review'
        else:
            return 'approve'
    
    def _load_toxic_keywords(self) -> List[str]:
        """Load toxic keywords list."""
        # Minimal set for MVP (TODO: Load from comprehensive list)
        return [
            'hate', 'stupid', 'idiot', 'dumb', 'kill', 'die',
            'racist', 'sexist', 'spam', 'scam', 'fake'
        ]


# Global instance
moderation_service = ModerationService()
