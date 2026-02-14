"""
Integration tests for pipeline and configuration.
Validates that settings, clients, and pipeline can be imported and used.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from app.core.settings import get_settings, Settings, validate_required_keys


class TestSettings:
    """Test configuration loading."""
    
    def test_settings_defaults(self):
        """Test that settings have proper defaults."""
        settings = get_settings()
        assert settings.gemini_model == "gemini-1.5-flash"
        assert settings.newsapi_page_size == 5
        assert settings.newsapi_language == "en"
        assert settings.request_timeout_seconds == 20
        assert settings.max_claims == 5
    
    def test_settings_caching(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
    
    def test_validate_required_keys_missing(self):
        """Test that validation raises error when keys are missing."""
        # This test requires no env vars set, so we skip if they exist
        if not os.getenv("GEMINI_API_KEY") and not os.getenv("NEWS_API_KEY"):
            with pytest.raises(ValueError, match="MISSING REQUIRED API KEYS"):
                validate_required_keys()


class TestClaimExtractor:
    """Test claim extraction."""
    
    def test_extract_claims_with_valid_content(self):
        """Test extraction with mock Gemini client."""
        from app.pipeline.claim_extractor import _extract_claims_heuristic
        
        content = "The Eiffel Tower is 330 meters tall. Paris was founded in 259 BC. Studies show climate change is real."
        claims = _extract_claims_heuristic(content, max_claims=3)
        
        assert isinstance(claims, list)
        assert len(claims) <= 3
        assert all(isinstance(c, str) for c in claims)
    
    def test_parse_claims_json_valid(self):
        """Test JSON parsing from Gemini response."""
        from app.pipeline.claim_extractor import _parse_claims_json
        
        response = '["Claim 1", "Claim 2", "Claim 3"]'
        claims = _parse_claims_json(response, max_claims=5)
        
        assert len(claims) == 3
        assert "Claim 1" in claims
    
    def test_parse_claims_json_with_markdown(self):
        """Test parsing JSON with markdown code fences."""
        from app.pipeline.claim_extractor import _parse_claims_json
        
        response = '```json\n["Claim 1", "Claim 2"]\n```'
        claims = _parse_claims_json(response, max_claims=5)
        
        assert len(claims) == 2
    
    def test_parse_claims_json_invalid(self):
        """Test graceful failure with invalid JSON."""
        from app.pipeline.claim_extractor import _parse_claims_json
        
        response = "Not valid JSON"
        claims = _parse_claims_json(response, max_claims=5)
        
        # Should return empty list on parse failure
        assert claims == []


class TestNewsClient:
    """Test NewsAPI client."""
    
    def test_search_news_missing_key(self):
        """Test that search_news raises error when key is missing."""
        from app.clients.news_client import NewsAPIError, search_news
        
        # Ensure NEWS_API_KEY is not set for this test
        with patch.dict(os.environ, {"NEWS_API_KEY": ""}, clear=False):
            # Clear the settings cache
            from app.core import settings
            settings.Settings.cache_clear() if hasattr(settings.Settings, 'cache_clear') else None
            
            with pytest.raises(NewsAPIError, match="NEWS_API_KEY not configured"):
                search_news("test query")


class TestVerifier:
    """Test claim verification."""
    
    def test_verify_empty_claims(self):
        """Test verification with empty claims list."""
        from app.pipeline.verifier import verify_claims
        
        results = verify_claims([])
        assert results == []
    
    def test_verify_claims_structure(self):
        """Test that verification results have expected structure."""
        from app.pipeline.verifier import _verify_single_claim
        from unittest.mock import patch
        
        # Mock NewsAPI and Gemini responses
        mock_sources = [
            {
                "name": "BBC",
                "headline": "Test Item",
                "url": "http://example.com",
                "snippet": "Test snippet",
                "publishedAt": "2024-01-01T00:00:00Z"
            }
        ]
        
        with patch("app.pipeline.verifier.search_news_with_fallback", return_value=mock_sources):
            with patch("app.pipeline.verifier._classify_claim_with_gemini") as mock_classify:
                mock_classify.return_value = {
                    "claim": "Test claim",
                    "status": "verified",
                    "rationale": "Supported by sources",
                    "sources": mock_sources
                }
                
                result = _verify_single_claim("Test claim")
                
                assert "claim" in result
                assert "status" in result
                assert result["status"] in ["verified", "disputed", "uncertain"]
                assert "rationale" in result
                assert "sources" in result


class TestSummarizer:
    """Test summary generation."""
    
    def test_generate_summary_empty_results(self):
        """Test fallback summary with no results."""
        from app.pipeline.summarizer import generate_summary
        
        summary = generate_summary("test content", [], [])
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_format_evidence_summary(self):
        """Test evidence formatting."""
        from app.pipeline.summarizer import _format_evidence_summary
        
        results = [
            {
                "claim": "Test claim 1",
                "status": "verified",
                "rationale": "Evidence found",
                "sources": [{"name": "BBC"}]
            },
            {
                "claim": "Test claim 2",
                "status": "disputed",
                "rationale": "Contradicted",
                "sources": []
            }
        ]
        
        summary = _format_evidence_summary(results)
        assert "Test claim 1" in summary
        assert "Test claim 2" in summary
        assert "verified" in summary.lower()
        assert "disputed" in summary.lower()


class TestAnalyzeRoute:
    """Test the analyze endpoint helper functions."""
    
    def test_calculate_credibility(self):
        """Test credibility score calculation."""
        from app.routes.analyze import _calculate_credibility
        
        results = [
            {"status": "verified"},
            {"status": "verified"},
            {"status": "disputed"},
        ]
        
        score = _calculate_credibility(results)
        assert 0 <= score <= 100
    
    def test_extract_findings(self):
        """Test findings extraction."""
        from app.routes.analyze import _extract_findings
        
        results = [
            {
                "claim": "Paris is capital",
                "status": "verified"
            },
            {
                "claim": "Earth is flat",
                "status": "disputed"
            }
        ]
        
        findings = _extract_findings(results)
        assert isinstance(findings, list)
        assert len(findings) > 0
    
    def test_format_sources(self):
        """Test source formatting."""
        from app.routes.analyze import _format_sources
        
        results = [
            {
                "status": "verified",
                "sources": [
                    {
                        "name": "BBC",
                        "headline": "Article Title",
                        "url": "http://example.com",
                        "snippet": "Article snippet"
                    }
                ]
            }
        ]
        
        sources = _format_sources(results)
        assert isinstance(sources, list)
        assert all(hasattr(s, 'name') for s in sources)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
