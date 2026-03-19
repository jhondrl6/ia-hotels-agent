from dataclasses import dataclass
from typing import Any, Dict, List
import re
from bs4 import BeautifulSoup


@dataclass
class ContentBlock:
    text: str
    word_count: int
    has_question: bool
    has_answer: bool
    is_self_contained: bool
    factual_density: float


@dataclass
class CitabilityScore:
    overall_score: float
    blocks_analyzed: int
    high_citability_blocks: int
    recommendations: List[str]
    block_scores: List[Dict[str, Any]]


class CitabilityScorer:
    OPTIMAL_WORD_RANGE = (134, 167)

    def score_content(self, html_content: str, url: str) -> CitabilityScore:
        blocks = self._extract_content_blocks(html_content)
        block_scores = []
        
        for block in blocks:
            score = self._score_block(block)
            block_scores.append({
                "text_preview": block.text[:100] + "..." if len(block.text) > 100 else block.text,
                "word_count": block.word_count,
                "score": score,
                "has_question": block.has_question,
                "has_answer": block.has_answer,
                "is_self_contained": block.is_self_contained,
                "factual_density": block.factual_density,
            })
        
        high_citability = sum(1 for bs in block_scores if bs["score"] >= 70)
        overall = sum(bs["score"] for bs in block_scores) / len(block_scores) if block_scores else 0
        
        recommendations = self._generate_recommendations(block_scores)
        
        return CitabilityScore(
            overall_score=round(overall, 2),
            blocks_analyzed=len(blocks),
            high_citability_blocks=high_citability,
            recommendations=recommendations,
            block_scores=block_scores,
        )

    def _extract_content_blocks(self, html: str) -> List[ContentBlock]:
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = soup.find_all("p")
        
        blocks = []
        for i, p in enumerate(paragraphs):
            text = p.get_text(strip=True)
            if not text or len(text) < 20:
                continue
            
            word_count = len(text.split())
            has_question = bool(re.search(r"[¿?]", text))
            
            next_p = paragraphs[i + 1] if i + 1 < len(paragraphs) else None
            has_answer = False
            if next_p:
                next_text = next_p.get_text(strip=True)
                if next_text and len(next_text) > 20:
                    has_answer = True
            
            sentences = re.split(r"[.!?]+", text)
            sentences = [s.strip() for s in sentences if s.strip()]
            is_self_contained = len(sentences) >= 2
            
            numbers = re.findall(r"\d+", text)
            factual_density = min(1.0, len(numbers) / max(1, word_count / 10))
            
            blocks.append(ContentBlock(
                text=text,
                word_count=word_count,
                has_question=has_question,
                has_answer=has_answer,
                is_self_contained=is_self_contained,
                factual_density=round(factual_density, 2),
            ))
        
        return blocks

    def _score_block(self, block: ContentBlock) -> float:
        score = 50.0
        
        min_opt, max_opt = self.OPTIMAL_WORD_RANGE
        if min_opt <= block.word_count <= max_opt:
            score += 20
        elif 100 <= block.word_count <= 200:
            score += 10
        
        if block.is_self_contained:
            score += 15
        
        if block.has_question and block.has_answer:
            score += 10
        
        score += block.factual_density * 5
        
        return min(100.0, max(0.0, score))

    def _generate_recommendations(self, block_scores: List[Dict]) -> List[str]:
        recommendations = []
        
        short_blocks = [bs for bs in block_scores if bs["word_count"] < 100]
        if short_blocks:
            recommendations.append(
                f"Found {len(short_blocks)} blocks under 100 words. "
                "Expand content to improve citability (aim for 134-167 words per block)."
            )
        
        low_score_blocks = [bs for bs in block_scores if bs["score"] < 50]
        if low_score_blocks:
            recommendations.append(
                f"Found {len(low_score_blocks)} blocks with low citability score. "
                "Add more factual content and ensure self-contained paragraphs."
            )
        
        no_qa_blocks = [bs for bs in block_scores if not bs["has_question"] and not bs["has_answer"]]
        if len(no_qa_blocks) > len(block_scores) * 0.7:
            recommendations.append(
                "Consider adding FAQ-style Q&A content to improve engagement and citability."
            )
        
        if not recommendations:
            recommendations.append("Content structure is good. Maintain current paragraph lengths.")
        
        return recommendations
