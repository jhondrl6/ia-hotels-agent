"""AI Crawler Auditor for robots.txt analysis.

Analyzes robots.txt files to determine AI crawler access permissions.
Supports 14+ AI crawlers including GPTBot, ClaudeBot, PerplexityBot, etc.

Usage:
    from modules.auditors.ai_crawler_auditor import AICrawlerAuditor
    
    auditor = AICrawlerAuditor()
    report = auditor.audit_robots_txt("https://hotelexample.com")
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin
import re

import httpx


AI_CRAWLERS = {
    "GPTBot": {"user_agent": "GPTBot", "owner": "OpenAI"},
    "ChatGPT-User": {"user_agent": "ChatGPT-User", "owner": "OpenAI"},
    "ClaudeBot": {"user_agent": "Claude-Web", "owner": "Anthropic"},
    "Claude-User": {"user_agent": "Claude-User", "owner": "Anthropic"},
    "PerplexityBot": {"user_agent": "PerplexityBot", "owner": "Perplexity"},
    "Google-Extended": {"user_agent": "Google-Extended", "owner": "Google (AIO)"},
    "Bytespider": {"user_agent": "Bytespider", "owner": "ByteDance"},
    "FacebookBot": {"user_agent": "facebookexternalhit", "owner": "Meta"},
    "Applebot": {"user_agent": "Applebot", "owner": "Apple"},
    "DuckDuckBot": {"user_agent": "DuckDuckBot", "owner": "DuckDuckGo"},
    "Baiduspider": {"user_agent": "Baiduspider", "owner": "Baidu"},
    "YandexBot": {"user_agent": "YandexBot", "owner": "Yandex"},
    "Bingbot": {"user_agent": "Bingbot", "owner": "Microsoft"},
    "Googlebot": {"user_agent": "Googlebot", "owner": "Google"},
}


@dataclass
class CrawlerAccessResult:
    """Result of checking a single AI crawler's access."""
    crawler_name: str
    user_agent: str
    owner: str
    allowed: bool
    confidence: float
    source: str
    recommendation: str


@dataclass
class AICrawlerAuditReport:
    """Complete AI crawler audit report."""
    url: str
    robots_url: str
    robots_exists: bool
    crawler_results: List[CrawlerAccessResult]
    overall_score: float
    timestamp: str


class AICrawlerAuditor:
    """Auditor for AI crawler access via robots.txt analysis."""
    
    def __init__(self, timeout: float = 10.0):
        """Initialize auditor.
        
        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    def __del__(self):
        """Cleanup HTTP client."""
        if hasattr(self, 'client'):
            self.client.close()
    
    def audit_robots_txt(self, url: str) -> AICrawlerAuditReport:
        """Audit robots.txt for AI crawler access.
        
        Args:
            url: Website URL to audit.
            
        Returns:
            AICrawlerAuditReport with per-crawler analysis.
        """
        base_url = url.rstrip('/')
        robots_url = f"{base_url}/robots.txt"
        
        robots_content = self._fetch_robots_txt(robots_url)
        
        results = []
        for name, config in AI_CRAWLERS.items():
            allowed = self._check_crawler_allowed(robots_content, config["user_agent"])
            
            if robots_content:
                confidence = 1.0
                source = "robots.txt"
            else:
                confidence = 0.5
                source = "not_found"
            
            results.append(CrawlerAccessResult(
                crawler_name=name,
                user_agent=config["user_agent"],
                owner=config["owner"],
                allowed=allowed,
                confidence=confidence,
                source=source,
                recommendation=self._generate_recommendation(name, allowed, robots_exists=robots_content is not None)
            ))
        
        return AICrawlerAuditReport(
            url=url,
            robots_url=robots_url,
            robots_exists=robots_content is not None,
            crawler_results=results,
            overall_score=self._calculate_score(results),
            timestamp=datetime.now().isoformat()
        )
    
    def _fetch_robots_txt(self, robots_url: str) -> Optional[str]:
        """Fetch robots.txt content.
        
        Args:
            robots_url: URL of robots.txt file.
            
        Returns:
            Robots.txt content or None if not found.
        """
        try:
            response = self.client.get(robots_url)
            if response.status_code == 200:
                return response.text
            return None
        except Exception:
            return None
    
    def _check_crawler_allowed(self, robots_content: Optional[str], user_agent: str) -> bool:
        """Check if a specific crawler is allowed based on robots.txt.
        
        Args:
            robots_content: Content of robots.txt file.
            user_agent: User agent string to check.
            
        Returns:
            True if allowed, False if blocked, True if no robots.txt.
        """
        if not robots_content:
            return True
        
        lines = robots_content.split('\n')
        
        user_agent_lines = []
        in_user_agent_block = False
        matched_specific = False
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.lower().startswith('user-agent:'):
                ua = line.split(':', 1)[1].strip()
                if ua == user_agent:
                    in_user_agent_block = True
                    matched_specific = True
                    user_agent_lines = []
                elif ua == '*':
                    if not matched_specific:
                        in_user_agent_block = True
                        user_agent_lines = []
                    else:
                        in_user_agent_block = False
                else:
                    in_user_agent_block = False
                    if matched_specific:
                        break
            elif in_user_agent_block:
                if line.lower().startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        return False
                elif line.lower().startswith('allow:'):
                    pass
        
        return True
    
    def _generate_recommendation(self, crawler_name: str, allowed: bool, robots_exists: bool) -> str:
        """Generate recommendation for a crawler.
        
        Args:
            crawler_name: Name of the crawler.
            allowed: Whether crawler is allowed.
            robots_exists: Whether robots.txt exists.
            
        Returns:
            Recommendation string.
        """
        if not robots_exists:
            return f"Crear robots.txt para controlar acceso de {crawler_name}"
        
        if allowed:
            return f"{crawler_name} tiene acceso permitido - OK"
        else:
            return f"Bloqueado: Considerar permitir {crawler_name} para mejora en IA"
    
    def _calculate_score(self, results: List[CrawlerAccessResult]) -> float:
        """Calculate overall AI crawler accessibility score.
        
        Args:
            results: List of crawler access results.
            
        Returns:
            Score from 0.0 to 1.0.
        """
        if not results:
            return 0.0
        
        total_weight = 0.0
        weighted_score = 0.0
        
        priority_crawlers = ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended"]
        
        for result in results:
            weight = 2.0 if result.crawler_name in priority_crawlers else 1.0
            total_weight += weight
            
            if result.allowed:
                weighted_score += weight * result.confidence
            else:
                weighted_score += weight * 0.5 * result.confidence
        
        return weighted_score / total_weight if total_weight > 0 else 0.0


def get_ai_crawler_auditor() -> AICrawlerAuditor:
    """Factory function to get AICrawlerAuditor instance.
    
    Returns:
        AICrawlerAuditor instance.
    """
    return AICrawlerAuditor()
