"""
Horarios Detector - Versión Playwright
======================================
Detector robusto de información de horarios en Google Maps.
Versión Playwright compatible con HorariosDetector (Selenium).

Mantiene 100% compatibilidad de interfaz para permitir fallback transparente.
"""

import re
import logging
from typing import Tuple, Optional, List

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


class HorariosDetectorPlaywright:
    """
    Detector robusto de información de horarios en Google Maps.
    Versión Playwright - Compatible con HorariosDetector (Selenium).
    """

    KEYWORDS_HORARIOS = [
        'horario', 'horarios', 'hora de entrada', 'hora de salida',
        'horario de entrada', 'horario de salida', 'entrada', 'salida',
        'entrada/salida', 'entrada - salida', 'entrada y salida',
        'check-in', 'check in', 'check-out', 'check out',
        'recepción', 'recepcion', 'atención', 'atencion',
        'abierto', 'cerrado', 'apertura', 'cierre',
        '24 horas', '24h', 'abierto toda',
        'opening hours', 'open', 'closed', 'hours',
        'reception', 'front desk',
    ]

    STRONG_KEYWORDS = [
        'hora de entrada', 'hora de salida', 'horario de entrada', 'horario de salida',
        'check-in', 'check in', 'check-out', 'check out',
        'entrada', 'salida', 'entrada/salida', 'entrada - salida', 'entrada y salida',
        'checkin', 'checkout', 'check in/out', 'check-in/out'
    ]

    TIME_PATTERNS = [
        r'\b([0-2]?[0-9]):([0-5][0-9])\s*(a\.?\s*m\.?|p\.?\s*m\.?|am|pm)?\b',
        r'\b(2[0-3]|[01]?[0-9]):([0-5][0-9])\b',
        r'\b([0-2]?[0-9])\s*(a\.?\s*m\.?|p\.?\s*m\.?)\b',
    ]

    CSS_SELECTORS = [
        "button[aria-label*='horario' i]",
        "div[aria-label*='horario' i]",
        "button[data-item-id='oh']",
        "div[data-item-id='oh']",
        "div[aria-label*='entrada' i]",
        "div[aria-label*='check-in' i]",
        "div[aria-label*='check in' i]",
        "span[aria-label*='hora de' i]",
        "table.WgFkxc",
        "div.OqCZI",
        "div[role='region']",
    ]

    def __init__(self, page: Page):
        self.page = page
        self.confidence_score = 0.0
        self.detection_evidence: List[str] = []

    def detect_horarios(self, timeout: int = 8) -> Tuple[bool, float, dict]:
        """
        Detecta información de horarios usando estrategia multinivel.

        Returns:
            Tuple[bool, float, dict]:
                - tiene_horarios: True si se detectaron horarios
                - confidence: Score 0.0-1.0 de confianza
                - metadata: Evidencia de detección
        """
        self.confidence_score = 0.0
        self.detection_evidence = []
        metadata = {
            'detection_method': None,
            'matched_keywords': [],
            'time_formats_found': [],
            'elements_analyzed': 0,
            'sample_text': None,
        }

        element_found, element_text = self._search_by_selectors(timeout)
        if element_found:
            metadata['detection_method'] = 'css_selector'
            metadata['sample_text'] = element_text[:200] if element_text else None

            css_confidence, css_keywords, css_time_formats = self._evaluate_text_confidence(element_text)
            if css_confidence >= 0.5:
                self.confidence_score = css_confidence
                metadata['matched_keywords'] = css_keywords
                metadata['time_formats_found'] = css_time_formats
                return True, self.confidence_score, metadata

        page_text = self._get_visible_text()
        metadata['elements_analyzed'] = len(page_text.split('\n'))

        keyword_score = self._analyze_keyword_presence(page_text)
        time_score = self._analyze_time_patterns(page_text)

        text_confidence, text_keywords, text_time_formats = self._evaluate_text_confidence(page_text)

        if keyword_score > 0 or time_score > 0 or text_confidence > 0:
            combined_confidence = min(0.85, (keyword_score * 0.4) + (time_score * 0.6))
            effective_confidence = max(combined_confidence, min(0.85, text_confidence))

            if time_score == 0 and combined_confidence < 0.5 and text_confidence >= 0.55:
                effective_confidence = min(0.8, text_confidence)

            if effective_confidence >= 0.5:
                self.confidence_score = effective_confidence
                metadata['detection_method'] = 'text_analysis'
                metadata['matched_keywords'] = text_keywords or self._extract_matched_keywords(page_text)
                metadata['time_formats_found'] = text_time_formats or self._extract_time_formats(page_text)
                metadata['sample_text'] = self._extract_relevant_snippet(page_text)
                return True, self.confidence_score, metadata

        always_open = self._detect_always_open(page_text)
        if always_open:
            self.confidence_score = 0.95
            metadata['detection_method'] = '24h_detection'
            metadata['sample_text'] = 'Detectado: servicio 24 horas'
            return True, self.confidence_score, metadata

        metadata['detection_method'] = 'not_found'
        return False, 0.0, metadata

    def _search_by_selectors(self, timeout: int) -> Tuple[bool, Optional[str]]:
        """Busca elementos usando selectores CSS ordenados por prioridad."""
        for selector in self.CSS_SELECTORS:
            try:
                element = self.page.wait_for_selector(selector, timeout=timeout * 1000)
                if element:
                    text_content = element.text_content() or ''
                    aria_label = element.get_attribute('aria-label') or ''
                    combined_text = f"{text_content} {aria_label}".strip()

                    if len(combined_text) > 3:
                        self.detection_evidence.append(f"Selector: {selector}")
                        return True, combined_text
            except PlaywrightTimeout:
                continue
            except Exception:
                continue

        return False, None

    def _get_visible_text(self) -> str:
        """Extrae texto visible de elementos relevantes."""
        try:
            main_panel = self.page.query_selector("div[role='main']")
            if main_panel:
                return main_panel.text_content() or ''
        except Exception:
            pass
        try:
            return self.page.content()
        except Exception:
            return ''

    def _analyze_keyword_presence(self, text: str) -> float:
        """Calcula score basado en presencia de palabras clave."""
        text_lower = text.lower()
        matches = [kw for kw in self.KEYWORDS_HORARIOS if kw in text_lower]

        if not matches:
            return 0.0

        score = min(1.0, len(matches) / 5.0)
        self.detection_evidence.extend(matches[:5])
        return score

    def _analyze_time_patterns(self, text: str) -> float:
        """Calcula score basado en formatos de tiempo detectados."""
        time_matches = []

        for pattern in self.TIME_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            time_matches.extend(matches)

        if not time_matches:
            return 0.0

        score = min(1.0, len(time_matches) / 4.0)
        return score

    def _detect_always_open(self, text: str) -> bool:
        """Detecta servicios 24 horas."""
        patterns_24h = [
            r'24\s*horas?',
            r'24\s*h\b',
            r'abierto\s+toda',
            r'siempre\s+abierto',
            r'24/7',
            r'24\s*hs?',
        ]

        text_lower = text.lower()
        for pattern in patterns_24h:
            if re.search(pattern, text_lower):
                self.detection_evidence.append(f"24h pattern: {pattern}")
                return True

        return False

    def _evaluate_text_confidence(self, text: str) -> Tuple[float, List[str], List[str]]:
        if not text or len(text.strip()) < 3:
            return 0.0, [], []

        text_lower = text.lower()
        matched_keywords = self._extract_matched_keywords(text)
        time_formats = self._extract_time_formats(text)

        if time_formats:
            base_confidence = 0.75 if len(time_formats) == 1 else 0.85
            if matched_keywords:
                base_confidence = min(0.95, base_confidence + min(len(matched_keywords), 3) * 0.05)
            return base_confidence, matched_keywords, time_formats

        strong_hits = [kw for kw in self.STRONG_KEYWORDS if kw in text_lower]
        keyword_hits: List[str] = []
        for kw in matched_keywords + strong_hits:
            if kw not in keyword_hits:
                keyword_hits.append(kw)

        if strong_hits:
            confidence = 0.65 if len(strong_hits) >= 2 else 0.55
            return confidence, keyword_hits[:5], []

        if len(matched_keywords) >= 3:
            return 0.55, matched_keywords[:5], []

        if len(matched_keywords) >= 2:
            return 0.5, matched_keywords[:5], []

        return 0.0, matched_keywords[:5], []

    def _extract_matched_keywords(self, text: str) -> List[str]:
        """Extrae keywords encontrados en el texto."""
        text_lower = text.lower()
        return [kw for kw in self.KEYWORDS_HORARIOS if kw in text_lower][:5]

    def _extract_time_formats(self, text: str) -> List[str]:
        """Extrae formatos de tiempo encontrados."""
        times = []
        for pattern in self.TIME_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            times.extend([''.join(m) if isinstance(m, tuple) else m for m in matches])
        return times[:5]

    def _extract_relevant_snippet(self, text: str, max_length: int = 150) -> Optional[str]:
        """Extrae fragmento relevante que contiene información de horarios."""
        text_lower = text.lower()
        for keyword in self.KEYWORDS_HORARIOS[:10]:
            idx = text_lower.find(keyword)
            if idx != -1:
                start = max(0, idx - 30)
                end = min(len(text), idx + max_length)
                snippet = text[start:end].strip()
                return f"...{snippet}..."

        return None
