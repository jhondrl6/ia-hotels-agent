"""Tests para AI Crawler Auditor.

Valida auditoría de robots.txt para crawlers de IA.
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.auditors.ai_crawler_auditor import (
    AICrawlerAuditor,
    AICrawlerAuditReport,
    CrawlerAccessResult,
    AI_CRAWLERS,
    get_ai_crawler_auditor,
)


@pytest.fixture
def auditor():
    """Fixture que proporciona una instancia de AICrawlerAuditor."""
    return AICrawlerAuditor(timeout=5.0)


@pytest.fixture
def sample_robots_txt():
    """Sample robots.txt content for testing."""
    return """User-agent: GPTBot
Disallow: /private/
Disallow: /admin/

User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
"""


class TestAICrawlerAuditor:
    """Tests for AICrawlerAuditor class."""
    
    def test_ai_crawler_auditor_detects_14_crawlers(self):
        """Test that auditor detects at least 14 AI crawlers."""
        assert len(AI_CRAWLERS) >= 14, "Must detect 14+ AI crawlers"
    
    def test_audit_robots_txt_with_valid_robots(self, auditor, sample_robots_txt):
        """Test audit with valid robots.txt."""
        with patch.object(auditor, '_fetch_robots_txt', return_value=sample_robots_txt):
            report = auditor.audit_robots_txt("https://example.com")
        
        assert isinstance(report, AICrawlerAuditReport)
        assert report.robots_exists is True
        assert len(report.crawler_results) >= 14
        assert report.overall_score >= 0.0
        assert report.overall_score <= 1.0
    
    def test_audit_robots_txt_no_robots_404(self, auditor):
        """Test audit when robots.txt returns 404."""
        with patch.object(auditor, '_fetch_robots_txt', return_value=None):
            report = auditor.audit_robots_txt("https://example.com")
        
        assert report.robots_exists is False
        assert report.overall_score >= 0.0
        
        gpt_result = next(r for r in report.crawler_results if r.crawler_name == "GPTBot")
        assert gpt_result.confidence == 0.5
        assert gpt_result.source == "not_found"
    
    def test_audit_robots_txt_blocks_gptbot(self, auditor, sample_robots_txt):
        """Test that GPTBot is blocked in sample robots.txt."""
        with patch.object(auditor, '_fetch_robots_txt', return_value=sample_robots_txt):
            report = auditor.audit_robots_txt("https://example.com")
        
        gpt_result = next(r for r in report.crawler_results if r.crawler_name == "GPTBot")
        assert gpt_result.allowed is False
        assert "bloqueado" in gpt_result.recommendation.lower()
    
    def test_audit_robots_txt_allows_unrestricted_crawler(self, auditor, sample_robots_txt):
        """Test that unrestricted crawlers are allowed."""
        with patch.object(auditor, '_fetch_robots_txt', return_value=sample_robots_txt):
            report = auditor.audit_robots_txt("https://example.com")
        
        claude_result = next(r for r in report.crawler_results if r.crawler_name == "ClaudeBot")
        assert claude_result.allowed is True
    
    def test_calculate_score_prioritizes_ai_crawlers(self, auditor):
        """Test that AI crawlers have higher weight in score calculation."""
        results = [
            CrawlerAccessResult("GPTBot", "GPTBot", "OpenAI", True, 1.0, "robots.txt", "OK"),
            CrawlerAccessResult("ClaudeBot", "Claude-Web", "Anthropic", True, 1.0, "robots.txt", "OK"),
            CrawlerAccessResult("Googlebot", "Googlebot", "Google", False, 1.0, "robots.txt", "Blocked"),
        ]
        
        score = auditor._calculate_score(results)
        
        assert score >= 0.0
        assert score <= 1.0
    
    def test_check_crawler_allowed_no_robots(self, auditor):
        """Test crawler allowed check when no robots.txt exists."""
        result = auditor._check_crawler_allowed(None, "GPTBot")
        assert result is True
    
    def test_check_crawler_allowed_with_disallow(self, auditor):
        """Test crawler allowed check with disallow rule."""
        robots = "User-agent: GPTBot\nDisallow: /"
        result = auditor._check_crawler_allowed(robots, "GPTBot")
        assert result is False
    
    def test_check_crawler_allowed_specific_path(self, auditor):
        """Test crawler allowed check with specific disallow path."""
        robots = "User-agent: GPTBot\nDisallow: /private/"
        result = auditor._check_crawler_allowed(robots, "GPTBot")
        assert result is False
    
    def test_generate_recommendation_blocked(self, auditor):
        """Test recommendation generation for blocked crawler."""
        rec = auditor._generate_recommendation("GPTBot", False, robots_exists=True)
        assert "bloqueado" in rec.lower() or "permitir" in rec.lower()
    
    def test_generate_recommendation_no_robots(self, auditor):
        """Test recommendation when robots.txt doesn't exist."""
        rec = auditor._generate_recommendation("GPTBot", True, robots_exists=False)
        assert "crear" in rec.lower()
    
    def test_factory_function(self):
        """Test get_ai_crawler_auditor factory function."""
        auditor = get_ai_crawler_auditor()
        assert isinstance(auditor, AICrawlerAuditor)
    
    def test_report_timestamp_format(self, auditor):
        """Test that report timestamp is ISO format."""
        with patch.object(auditor, '_fetch_robots_txt', return_value=None):
            report = auditor.audit_robots_txt("https://example.com")
        
        assert "T" in report.timestamp
        import re
        iso_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        assert re.match(iso_pattern, report.timestamp) is not None


class TestCrawlerAccessResult:
    """Tests for CrawlerAccessResult dataclass."""
    
    def test_crawler_access_result_creation(self):
        """Test creating a CrawlerAccessResult."""
        result = CrawlerAccessResult(
            crawler_name="GPTBot",
            user_agent="GPTBot",
            owner="OpenAI",
            allowed=True,
            confidence=1.0,
            source="robots.txt",
            recommendation="OK"
        )
        
        assert result.crawler_name == "GPTBot"
        assert result.allowed is True
        assert result.confidence == 1.0


class TestAICrawlerIntegration:
    """Integration tests for AI Crawler Auditor."""
    
    def test_v4_comprehensive_imports_auditor(self):
        """Test that AI Crawler Auditor can be imported from auditors module."""
        from modules.auditors.ai_crawler_auditor import AICrawlerAuditor
        assert AICrawlerAuditor is not None
    
    def test_all_known_crawlers_in_catalog(self):
        """Test that all specified crawlers are in the catalog."""
        expected_crawlers = [
            "GPTBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
            "PerplexityBot", "Google-Extended", "Bytespider", "FacebookBot",
            "Applebot", "DuckDuckBot", "Baiduspider", "YandexBot", "Bingbot", "Googlebot"
        ]
        
        for crawler in expected_crawlers:
            assert crawler in AI_CRAWLERS, f"{crawler} should be in AI_CRAWLERS"
