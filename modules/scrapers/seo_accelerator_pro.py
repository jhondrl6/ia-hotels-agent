from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from modules.scrapers.schema_finder import SchemaFinder
from modules.providers.llm_provider import ProviderAdapter
from modules.utils.http_client import get_default_client

# --- Clases de Análisis Mejoradas ---

class PageAnalyzer:
    """Analiza el contenido HTML de una URL - Versión mejorada con fallback SSL."""
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.timeout = 15
        self.soup: Optional[BeautifulSoup] = None
        self.html_content: Optional[str] = None
        self.final_url: str = url
        self.error: Optional[str] = None
        self.ssl_fallback_info: Dict[str, Any] = {}
        
        # Cliente HTTP con fallback SSL
        self.http_client = get_default_client()
        self._fetch_page()

    def _fetch_page(self):
        try:
            # Usar HttpClient con fallback SSL
            response, fallback_info = self.http_client.get(
                self.url, 
                headers=self.headers, 
                allow_redirects=True
            )
            self.ssl_fallback_info = fallback_info
            
            if response is None:
                self.error = fallback_info.get('error', 'Request failed')
                return
                
            self.final_url = response.url
            self.html_content = response.text
            self.soup = BeautifulSoup(self.html_content, "html.parser")
        except requests.RequestException as e:
            self.error = str(e)

    def get_title(self) -> str:
        if not self.soup: return ""
        return self.soup.title.string.strip() if self.soup.title and self.soup.title.string else ""

    def get_meta_description(self) -> str:
        if not self.soup: return ""
        tag = self.soup.find("meta", attrs={"name": "description"})
        return tag["content"].strip() if tag and tag.get("content") else ""

    def get_headings(self) -> Dict[str, List[str]]:
        if not self.soup: return {}
        headings = {"h1": [], "h2": [], "h3": []}
        for h in ["h1", "h2", "h3"]:
            for tag in self.soup.find_all(h):
                headings[h].append(tag.get_text(strip=True))
        return headings

    def get_images(self) -> List[Dict[str, str]]:
        if not self.soup: return []
        images = []
        for img in self.soup.find_all("img"):
            images.append({
                "src": img.get("src", ""),
                "alt": img.get("alt", ""),
            })
        return images

    def get_links(self) -> List[Dict[str, str]]:
        if not self.soup: return []
        links = []
        parsed_url = urlparse(self.final_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        for a in self.soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)
            link_type = "external"
            if urlparse(full_url).netloc == parsed_url.netloc:
                link_type = "internal"
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                link_type = "other"
            
            links.append({
                "href": href,
                "text": a.get_text(strip=True),
                "type": link_type,
            })
        return links

@dataclass
class SEOIssue:
    """Representa un problema SEO con su impacto y solución."""
    icon: str
    title: str
    problem: str
    impact: str
    solution: str
    priority: str  # CRÍTICO, ALTO, MEDIO, BAJO
    category: str  # technical, content, conversion, local, reputation
    estimated_monthly_loss: int = 0
    estimated_improvement: str = ""
    fix_time: str = ""
    score_impact: int = 0


@dataclass
class SEOScoreBreakdown:
    """Score desglosado por categorías."""
    technical: int = 100
    content: int = 100
    conversion: int = 100
    local_seo: int = 100
    reputation: int = 100
    
    @property
    def total(self) -> int:
        """Calcula el score total ponderado."""
        weights = {
            'technical': 0.25,
            'content': 0.25,
            'conversion': 0.20,
            'local_seo': 0.20,
            'reputation': 0.10
        }
        return int(
            self.technical * weights['technical'] +
            self.content * weights['content'] +
            self.conversion * weights['conversion'] +
            self.local_seo * weights['local_seo'] +
            self.reputation * weights['reputation']
        )


@dataclass
class CompetitorData:
    """Datos de un competidor."""
    name: str
    url: str
    score_estimate: int = 0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


class SEOAcceleratorProEnhanced:
    """
    Analizador SEO avanzado para hoteles - VERSIÓN MEJORADA.
    
    Combina la robustez de SEOAcceleratorPro con mejoras específicas de ai_studio_code.
    """
    
    def __init__(
        self,
        url: str,
        business_name: Optional[str],
        location: Optional[str],
        provider_type: Optional[str] = None,
    ) -> None:
        self.url = url
        self.business_name = (business_name or "Hotel").strip() or "Hotel"
        self.location = (location or "Colombia").strip() or "Colombia"
        self.provider_type = provider_type or "deepseek"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.timeout = 15
        
        # Usar PageAnalyzer mejorado
        self.page_analyzer = PageAnalyzer(self.url)
        
        # Cache
        self._analysis_cache: Dict[str, Any] = {}
        
        # Resultados
        self.issues: List[SEOIssue] = []
        self.score: SEOScoreBreakdown = SEOScoreBreakdown()
        self.metadata: Dict[str, Any] = {}
        
    def analyze_complete(self, include_competitor_analysis: bool = False) -> Dict[str, Any]:
        """
        Análisis SEO completo en una sola ejecución - VERSIÓN MEJORADA.
        """
        # 1. Usar PageAnalyzer para análisis de contenido
        if self.page_analyzer.error:
            issue = SEOIssue(
                icon="💥",
                title="Sitio inaccesible",
                problem=f"No se pudo acceder al sitio: {self.page_analyzer.error}",
                impact="Sin acceso web = 0 reservas directas. Los huéspedes ven error y se van a OTAs.",
                solution="Contactar al proveedor de hosting inmediatamente. Verificar DNS y configuración del servidor.",
                priority="CRÍTICO",
                category="technical",
                estimated_monthly_loss=1_500_000,
                fix_time="Inmediato (revisar con hosting)",
                score_impact=40
            )
            self.issues.append(issue)
            # FIX: Cuando el sitio es inaccesible, TODOS los scores deben ser 0
            # No solo technical - evita falsos positivos con scores altos en sitios caídos
            self.score = SEOScoreBreakdown(
                technical=0,
                content=0,
                conversion=0,
                local_seo=0,
                reputation=0
            )
            return self._compile_results([issue], [], include_competitor_analysis)

        # 2. Análisis técnico mejorado
        technical_issues = self._analyze_technical_seo_enhanced()
        
        # 3. Análisis de contenido mejorado
        content_issues = self._analyze_content_quality_enhanced()
        
        # 4. Análisis de conversión
        conversion_issues = self._analyze_conversion_elements()
        
        # 5. Análisis de presencia local mejorado
        local_issues = self._analyze_local_presence_enhanced()
        
        # 6. Análisis de reputación
        reputation_issues = self._analyze_reputation_signals()
        
        # Combinar todos los issues
        all_issues = technical_issues + content_issues + conversion_issues + local_issues + reputation_issues
        self.issues = all_issues
        
        return self._compile_results(all_issues, [], include_competitor_analysis)
    
    def _analyze_technical_seo_enhanced(self) -> List[SEOIssue]:
        """Análisis técnico mejorado integrando criterios de ambos módulos + v2.6 improvements."""
        issues = []
        soup = self.page_analyzer.soup
        
        # HTTPS (de ambos módulos)
        if not self.page_analyzer.final_url.startswith("https://"):
            issues.append(SEOIssue(
                icon="🔒",
                title="Sin HTTPS",
                problem="El sitio no usa protocolo seguro",
                impact="Navegadores marcan como 'No seguro'. 67% de usuarios móviles abandonan sitios sin HTTPS.",
                solution="Activar certificado SSL gratuito (Let's Encrypt) en el hosting.",
                priority="CRÍTICO",
                category="technical",
                estimated_monthly_loss=800_000,
                estimated_improvement="8-12 reservas/mes",
                fix_time="30 minutos con hosting",
                score_impact=20
            ))
        
        # v2.6: Core Web Vitals (real data if API configured, fallback otherwise)
        cwv_data = self._fetch_core_web_vitals()
        self._analysis_cache["core_web_vitals"] = cwv_data
        
        if cwv_data.get("status") == "success":
            perf_score = cwv_data.get("performance_score", 0)
            lcp = cwv_data.get("lcp_seconds", 0)
            
            if perf_score < 50 or lcp > 4.0:
                issues.append(SEOIssue(
                    icon="🐌",
                    title="Core Web Vitals deficientes",
                    problem=f"Performance Score: {perf_score}/100, LCP: {lcp:.1f}s",
                    impact="Google penaliza sitios lentos. Más del 50% de usuarios abandonan si tarda >3s.",
                    solution="Optimizar imágenes, reducir JS bloqueante, habilitar caching.",
                    priority="CRÍTICO" if lcp > 4.0 else "ALTO",
                    category="technical",
                    estimated_monthly_loss=450_000 if lcp > 4.0 else 300_000,
                    estimated_improvement="5-8 reservas/mes",
                    fix_time="2-4 horas",
                    score_impact=20 if lcp > 4.0 else 15
                ))
            elif perf_score < 75:
                issues.append(SEOIssue(
                    icon="⚡",
                    title="Velocidad mejorable",
                    problem=f"Performance Score: {perf_score}/100 (objetivo: ≥75)",
                    impact="Velocidad aceptable pero con margen de mejora para ranking.",
                    solution="Optimizar imágenes, habilitar lazy loading.",
                    priority="MEDIO",
                    category="technical",
                    estimated_monthly_loss=150_000,
                    estimated_improvement="2-3 reservas/mes",
                    fix_time="1-2 horas",
                    score_impact=8
                ))
            # If score >= 75, no issue added (good performance)
        else:
            # Fallback: heurística original si API no está configurada
            issues.append(SEOIssue(
                icon="🐌",
                title="Velocidad de carga (sin verificar)",
                problem=f"API PageSpeed no configurada - se recomienda optimización ({cwv_data.get('reason', 'API key missing')})",
                impact="Más del 50% de los usuarios abandonan un sitio si tarda más de 3 segundos en cargar.",
                solution="Optimizar imágenes (WebP), reducir JavaScript bloqueante, habilitar caching. Configurar GOOGLE_PAGESPEED_API_KEY para métricas reales.",
                priority="ALTO",
                category="technical",
                estimated_monthly_loss=450_000,
                estimated_improvement="5-7 reservas/mes",
                fix_time="2-3 horas",
                score_impact=15
            ))
        
        # Optimización móvil (de ambos módulos)
        viewport = soup.find('meta', attrs={'name': 'viewport'}) if soup else None
        if not viewport:
            issues.append(SEOIssue(
                icon="📱",
                title="No optimizado para móvil",
                problem="Falta meta tag viewport o diseño no responsive",
                impact="Más del 60% del tráfico de hoteles proviene de dispositivos móviles. Una mala experiencia móvil frustra a los usuarios y pierdes reservas.",
                solution='Agregar <meta name="viewport" content="width=device-width, initial-scale=1"> y usar diseño responsive.',
                priority="CRÍTICO",
                category="technical",
                estimated_monthly_loss=600_000,
                estimated_improvement="6-9 reservas/mes",
                fix_time="1-2 horas",
                score_impact=15
            ))
        
        # v2.6: Canonical URL check
        canonical_issue = self._check_canonical_url()
        if canonical_issue:
            issues.append(canonical_issue)
        
        # v2.6: robots.txt and sitemap.xml checks
        issues.extend(self._check_robots_and_sitemap())
        
        return issues
    
    def _analyze_content_quality_enhanced(self) -> List[SEOIssue]:
        """Análisis de contenido mejorado integrando PageAnalyzer."""
        issues = []
        
        # Título (análisis mejorado)
        title = self.page_analyzer.get_title()
        if not title or len(title) < 30:
            issues.append(SEOIssue(
                icon="🏷️",
                title="Título de página genérico o demasiado corto",
                problem=f"Título actual: '{title}' ({len(title)} caracteres)" if title else "Sin título",
                impact="Un título débil no atrae clics en Google, reduciendo el CTR (Click-Through Rate) y afectando el posicionamiento.",
                solution="Crear un título descriptivo de entre 50-60 caracteres que incluya el nombre del hotel, su valor diferencial (ej. 'con aguas termales') y la ubicación.",
                priority="CRÍTICO",
                category="content",
                estimated_monthly_loss=700_000,
                estimated_improvement="10-15 reservas/mes",
                fix_time="15 minutos",
                score_impact=20
            ))
        
        # Meta Description (análisis mejorado)
        description = self.page_analyzer.get_meta_description()
        if not description or len(description) < 80:
            issues.append(SEOIssue(
                icon="📝",
                title="Meta description débil o ausente",
                problem=f"Description actual: {len(description)} caracteres" if description else "Sin meta description",
                impact="Los potenciales huéspedes no ven una propuesta de valor clara en los resultados de Google, por lo que es menos probable que hagan clic.",
                solution="Escribir una meta description atractiva de unos 150 caracteres que resuma la experiencia del hotel e invite a reservar.",
                priority="ALTO",
                category="content",
                estimated_monthly_loss=300_000,
                estimated_improvement="3-5 reservas/mes",
                fix_time="20 minutos",
                score_impact=10
            ))
        
        # Encabezados (usando PageAnalyzer)
        headings = self.page_analyzer.get_headings()
        if not headings.get("h1"):
            issues.append(SEOIssue(
                icon="🎯",
                title="Ausencia de un encabezado H1",
                problem="No hay etiqueta H1 en la página",
                impact="Los motores de búsqueda no pueden determinar el tema principal de la página, lo que debilita la relevancia para las búsquedas clave.",
                solution=f"Añadir un único encabezado H1 por página que describa claramente el contenido principal (ej. '{self.business_name} en {self.location}').",
                priority="ALTO",
                category="content",
                estimated_monthly_loss=250_000,
                estimated_improvement="3-4 reservas/mes",
                fix_time="10 minutos",
                score_impact=10
            ))
        elif len(headings.get("h1", [])) > 1:
            issues.append(SEOIssue(
                icon="⚡",
                title="Múltiples encabezados H1",
                problem=f"Hay {len(headings.get('h1'))} etiquetas H1 (debe ser 1)",
                impact="Confunde a los motores de búsqueda sobre cuál es el tema principal de la página, diluyendo la autoridad SEO.",
                solution="Asegurar que haya un único H1. Usar H2 y H3 para las subsecciones.",
                priority="MEDIO",
                category="content",
                estimated_monthly_loss=100_000,
                fix_time="20 minutos",
                score_impact=5
            ))
        
        # Optimización de Imágenes (usando PageAnalyzer)
        images = self.page_analyzer.get_images()
        images_without_alt = [img for img in images if not img.get("alt", "").strip()]
        
        if len(images_without_alt) > 2:
            issues.append(SEOIssue(
                icon="🖼️",
                title="Imágenes sin texto alternativo",
                problem=f"{len(images_without_alt)} de {len(images)} imágenes no tienen texto alternativo (alt tag)",
                impact="Se pierde la oportunidad de posicionar en Google Imágenes y se afecta la accesibilidad para usuarios con discapacidad visual.",
                solution="Añadir texto 'alt' descriptivo a todas las imágenes, explicando lo que muestran (ej. 'habitación doble con vista a las montañas').",
                priority="ALTO",
                category="content",
                estimated_monthly_loss=400_000,
                estimated_improvement="5-7 reservas/mes",
                fix_time="1-2 horas",
                score_impact=12
            ))
        
        # v2.6: Internal links analysis
        internal_link_issue = self._analyze_internal_links()
        if internal_link_issue:
            issues.append(internal_link_issue)
        
        return issues
    
    def _analyze_conversion_elements(self) -> List[SEOIssue]:
        """Análisis de elementos de conversión mejorado."""
        issues = []
        
        # CTA analysis usando PageAnalyzer
        links = self.page_analyzer.get_links()
        cta_found = any(
            "reserva" in link["href"] or "booking" in link["href"] or 
            "wa.me" in link["href"] or "whatsapp" in link["href"] 
            for link in links
        )
        
        if not cta_found:
            issues.append(SEOIssue(
                icon="☎️",
                title="Sin llamados a la acción (CTA) claro para reservar",
                problem="No hay botones visibles de reserva, WhatsApp o teléfono",
                impact="Los visitantes interesados en reservar no encuentran cómo hacerlo fácilmente, lo que lleva a una alta tasa de abandono y pérdida de reservas directas.",
                solution="Agregar botón flotante de WhatsApp y botón de 'Reservar Ahora' en header.",
                priority="CRÍTICO",
                category="conversion",
                estimated_monthly_loss=900_000,
                estimated_improvement="12-18 reservas/mes",
                fix_time="1 hora (con plugin)",
                score_impact=25
            ))
        
        return issues
    
    def _analyze_local_presence_enhanced(self) -> List[SEOIssue]:
        """Análisis de presencia local mejorado integrando SchemaFinder."""
        issues = []
        
        # Schema de Hotel (de ai_studio_code)
        schema_finder = SchemaFinder()
        schema_result = schema_finder.analyze(self.url)
        self._analysis_cache["schema_result"] = schema_result
        
        if not schema_result.get("tiene_hotel_schema"):
            issues.append(SEOIssue(
                icon="🏨",
                title="Schema de hotel ausente",
                problem="No hay markup de Schema.org tipo Hotel",
                impact="Google y otras IAs no pueden identificar claramente la web como un hotel, perdiendo oportunidades en resultados de búsqueda locales y enriquecidos.",
                solution="Implementar un script JSON-LD con el tipo `@type: Hotel` que incluya detalles como dirección, rango de precios y teléfono.",
                priority="ALTO",
                category="local_seo",
                estimated_monthly_loss=600_000,
                estimated_improvement="8-12 consultas/mes de búsqueda por voz",
                fix_time="45 minutos",
                score_impact=20
            ))
        
        # Otros Schemas (de ai_studio_code)
        if schema_result.get("schemas_faltantes"):
            missing = ", ".join(schema_result["schemas_faltantes"])
            issues.append(SEOIssue(
                icon="📄",
                title="Faltan schemas recomendados",
                problem=f"Faltan: {missing}",
                impact="Se pierden 'rich snippets' (estrellas de valoración, preguntas frecuentes) en los resultados de Google, disminuyendo el CTR.",
                solution=f"Añadir schemas como {missing} para enriquecer la apariencia en los resultados de búsqueda.",
                priority="MEDIO",
                category="local_seo",
                estimated_monthly_loss=250_000,
                estimated_improvement="CTR +15-25%",
                fix_time="1 hora",
                score_impact=15
            ))
        
        # Google Business Profile (concepto de ambos módulos)
        issues.append(SEOIssue(
            icon="🗺️",
            title="Perfil de Google Business Profile incompleto",
            problem="La ficha de Google Business existe pero carece de optimizaciones clave (posts recientes, botón de WhatsApp, galería robusta).",
            impact="Sin contenido actualizado y CTA visibles, pierdes relevancia en Google Maps y consultas 'cerca de mí'.",
            solution="Actualizar GBP con posts semanales, botón de reserva/WhatsApp y al menos 15 fotos profesionales.",
            priority="ALTO",
            category="local_seo",
            estimated_monthly_loss=400_000,
            estimated_improvement="5-8 reservas/mes",
            fix_time="2-3 horas",
            score_impact=12
        ))
        
        return issues
    
    def _analyze_reputation_signals(self) -> List[SEOIssue]:
        """Análisis de señales de reputación mejorado."""
        issues = []
        
        # Gestión de reseñas (de ai_studio_code)
        issues.append(SEOIssue(
            icon="⭐",
            title="Gestión de reseñas online limitada",
            problem="No se muestran testimonios ni respuestas recientes a reseñas en el sitio web.",
            impact="Las reseñas negativas sin respuesta pueden disuadir al 90% de los potenciales clientes. Una buena reputación es clave para la decisión de reserva.",
            solution="Mostrar testimonios destacados y responder reseñas en Google, TripAdvisor y perfiles sociales.",
            priority="ALTO",
            category="reputation",
            estimated_monthly_loss=450_000,
            estimated_improvement="6-8 reservas/mes",
            fix_time="2 horas",
            score_impact=15
        ))
        
        # Redes sociales usando PageAnalyzer
        links = self.page_analyzer.get_links()
        social_links = [l for l in links if any(platform in l['href'] for platform in 
                      ['facebook.com', 'instagram.com', 'twitter.com'])]
        
        if not social_links:
            issues.append(SEOIssue(
                icon="📱",
                title="No se encontraron enlaces a redes sociales",
                problem="No hay links a Facebook, Instagram o Twitter",
                impact="Se pierde una oportunidad para interactuar con la comunidad, mostrar la experiencia del hotel y generar confianza y branding.",
                solution="Añadir enlaces visibles a los perfiles de redes sociales activos (como Instagram o Facebook) en el pie de página o encabezado del sitio web.",
                priority="BAJO",
                category="reputation",
                estimated_monthly_loss=150_000,
                fix_time="30 minutos",
                score_impact=5
            ))
        
        # v2.6: Open Graph and Twitter Cards check
        issues.extend(self._check_social_meta_tags())
        
        return issues

    # =========================================================================
    # SEO v2.6 IMPROVEMENTS - New diagnostic methods
    # =========================================================================

    def _fetch_core_web_vitals(self) -> Dict[str, Any]:
        """Obtiene métricas reales de Core Web Vitals via PageSpeed Insights API."""
        import os
        api_key = os.getenv("GOOGLE_PAGESPEED_API_KEY")
        
        if not api_key:
            return {"status": "skipped", "reason": "GOOGLE_PAGESPEED_API_KEY not configured"}
        
        try:
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                "url": self.url,
                "key": api_key,
                "strategy": "mobile",
                "category": ["performance", "seo"]
            }
            response = requests.get(api_url, params=params, timeout=30)
            data = response.json()
            
            # Extract key metrics
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            audits = lighthouse.get("audits", {})
            
            return {
                "status": "success",
                "performance_score": int(categories.get("performance", {}).get("score", 0) * 100),
                "seo_score": int(categories.get("seo", {}).get("score", 0) * 100),
                "lcp_seconds": audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000,
                "fid_ms": audits.get("max-potential-fid", {}).get("numericValue", 0),
                "cls": audits.get("cumulative-layout-shift", {}).get("numericValue", 0),
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def _check_canonical_url(self) -> Optional[SEOIssue]:
        """Verifica la presencia y correcta configuración de URL canónica."""
        soup = self.page_analyzer.soup
        if not soup:
            return None
        
        canonical = soup.find("link", rel="canonical")
        
        if not canonical:
            return SEOIssue(
                icon="🔗",
                title="URL canónica ausente",
                problem="No se encontró <link rel='canonical'> en la página",
                impact="Google puede indexar versiones duplicadas (www vs no-www, http vs https).",
                solution="Agregar <link rel='canonical' href='https://[dominio]/'> en el <head>.",
                priority="ALTO",
                category="technical",
                estimated_monthly_loss=200_000,
                fix_time="10 minutos",
                score_impact=10
            )
        
        canonical_url = canonical.get("href", "")
        
        # Verify canonical points to HTTPS
        if canonical_url and not canonical_url.startswith("https://"):
            return SEOIssue(
                icon="🔗",
                title="URL canónica insegura",
                problem=f"Canonical apunta a HTTP: {canonical_url}",
                impact="La versión canónica debería ser HTTPS.",
                solution=f"Cambiar canonical a: https://{canonical_url.replace('http://', '')}",
                priority="MEDIO",
                category="technical",
                estimated_monthly_loss=100_000,
                fix_time="10 minutos",
                score_impact=5
            )
        
        return None

    def _check_robots_and_sitemap(self) -> List[SEOIssue]:
        """Verifica existencia de robots.txt y sitemap.xml."""
        issues = []
        parsed = urlparse(self.page_analyzer.final_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Check robots.txt
        try:
            robots_response = requests.get(f"{base_url}/robots.txt", timeout=10, headers=self.headers)
            if robots_response.status_code != 200:
                issues.append(SEOIssue(
                    icon="🤖",
                    title="robots.txt no encontrado",
                    problem=f"Código {robots_response.status_code} al acceder a /robots.txt",
                    impact="Googlebot puede no rastrear eficientemente el sitio.",
                    solution="Crear robots.txt con: User-agent: *\\nAllow: /\\nSitemap: [URL sitemap]",
                    priority="MEDIO",
                    category="technical",
                    estimated_monthly_loss=100_000,
                    fix_time="15 minutos",
                    score_impact=5
                ))
            else:
                # Check if it references sitemap
                if "sitemap" not in robots_response.text.lower():
                    issues.append(SEOIssue(
                        icon="🗺️",
                        title="robots.txt sin referencia a sitemap",
                        problem="El robots.txt no incluye directiva Sitemap",
                        impact="Google puede no descubrir todas las páginas.",
                        solution="Agregar línea: Sitemap: https://[dominio]/sitemap.xml",
                        priority="BAJO",
                        category="technical",
                        estimated_monthly_loss=50_000,
                        fix_time="5 minutos",
                        score_impact=3
                    ))
        except Exception:
            pass
        
        # Check sitemap.xml
        try:
            sitemap_response = requests.get(f"{base_url}/sitemap.xml", timeout=10, headers=self.headers)
            if sitemap_response.status_code != 200:
                issues.append(SEOIssue(
                    icon="🗺️",
                    title="sitemap.xml no encontrado",
                    problem=f"Código {sitemap_response.status_code} al acceder a /sitemap.xml",
                    impact="Google puede no indexar todas las páginas del sitio.",
                    solution="Generar sitemap.xml con plugin (Yoast SEO, Rank Math) o herramienta online.",
                    priority="MEDIO",
                    category="technical",
                    estimated_monthly_loss=150_000,
                    fix_time="20 minutos",
                    score_impact=8
                ))
        except Exception:
            pass
        
        return issues

    def _check_social_meta_tags(self) -> List[SEOIssue]:
        """Verifica Open Graph y Twitter Cards para compartir en redes sociales."""
        issues = []
        soup = self.page_analyzer.soup
        if not soup:
            return issues
        
        # Open Graph
        og_title = soup.find("meta", property="og:title")
        og_description = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")
        
        missing_og = []
        if not og_title:
            missing_og.append("og:title")
        if not og_description:
            missing_og.append("og:description")
        if not og_image:
            missing_og.append("og:image")
        
        if missing_og:
            issues.append(SEOIssue(
                icon="📱",
                title="Open Graph incompleto",
                problem=f"Faltan tags: {', '.join(missing_og)}",
                impact="Al compartir en Facebook/WhatsApp, no se muestra preview atractivo.",
                solution="Agregar meta tags OG en el <head> del sitio.",
                priority="BAJO" if len(missing_og) == 1 else "MEDIO",
                category="reputation",
                estimated_monthly_loss=100_000,
                fix_time="20 minutos",
                score_impact=5
            ))
        
        # Twitter Cards (optional)
        twitter_card = soup.find("meta", attrs={"name": "twitter:card"})
        if not twitter_card:
            issues.append(SEOIssue(
                icon="🐦",
                title="Twitter Card no configurada",
                problem="No se encontró meta tag twitter:card",
                impact="Al compartir en Twitter/X, no se muestra preview.",
                solution="Agregar: <meta name='twitter:card' content='summary_large_image'>",
                priority="BAJO",
                category="reputation",
                estimated_monthly_loss=50_000,
                fix_time="10 minutos",
                score_impact=3
            ))
        
        return issues

    def _analyze_internal_links(self) -> Optional[SEOIssue]:
        """Análisis básico de estructura de enlaces internos."""
        links = self.page_analyzer.get_links()
        internal_links = [l for l in links if l.get("type") == "internal"]
        
        if len(internal_links) < 5:
            return SEOIssue(
                icon="🔗",
                title="Pocos enlaces internos en homepage",
                problem=f"Solo {len(internal_links)} enlaces internos detectados",
                impact="Dificulta la distribución de autoridad SEO y navegación.",
                solution="Agregar enlaces a páginas clave (habitaciones, servicios, contacto, blog).",
                priority="MEDIO",
                category="content",
                estimated_monthly_loss=150_000,
                fix_time="30 minutos",
                score_impact=8
            )
        
        # Check if key pages are linked
        key_pages = ["habitacion", "servicio", "contacto", "reserv", "tarifa"]
        linked_key_pages = sum(1 for l in internal_links 
                              if any(kp in l.get("href", "").lower() for kp in key_pages))
        
        if linked_key_pages < 2:
            return SEOIssue(
                icon="🧭",
                title="Páginas clave no enlazadas desde home",
                problem="La homepage no enlaza directamente a habitaciones/servicios/reservas",
                impact="Usuarios y bots tardan más en encontrar contenido importante.",
                solution="Agregar enlaces visibles a 'Habitaciones', 'Servicios', 'Reservar'.",
                priority="MEDIO",
                category="content",
                estimated_monthly_loss=100_000,
                fix_time="20 minutos",
                score_impact=5
            )
        
        return None
    
    def _compile_results(self, issues: List[SEOIssue], competitors: List[Any], include_competitor_analysis: bool) -> Dict[str, Any]:
        """Compila todos los resultados del análisis en un formato serializable."""
        self.score = self._calculate_scores_enhanced(issues)
        
        # --- INICIO: Multiplicador de Penalización v2.5.2 ---
        critical_count = sum(1 for i in issues if i.priority == "CRÍTICO")
        high_count = sum(1 for i in issues if i.priority == "ALTO")
        
        penalty_multiplier = 1.0
        penalty_reason = None
        original_score = self.score.total
        
        if critical_count > 0:
            penalty_multiplier = 0.60
            penalty_reason = f"Penalización por {critical_count} falla(s) CRÍTICA(s)"
        elif high_count >= 3:
            penalty_multiplier = 0.80
            penalty_reason = f"Penalización por {high_count} fallas de prioridad ALTA"
        
        # Calcular score penalizado
        penalized_total = int(original_score * penalty_multiplier)
        
        # Almacenar metadata de penalización para trazabilidad
        penalty_metadata = {
            "original_score": original_score,
            "penalized_score": penalized_total,
            "penalty_multiplier": penalty_multiplier,
            "penalty_reason": penalty_reason,
            "critical_count": critical_count,
            "high_count": high_count,
        }
        # --- FIN: Multiplicador de Penalización ---
        
        # Aplicar penalización SSL si corresponde
        ssl_info = getattr(self.page_analyzer, 'ssl_fallback_info', {})
        if ssl_info.get('ssl_bypassed'):
            seo_penalty = ssl_info.get('seo_penalty', 30)
            self.score.technical = max(0, self.score.technical - seo_penalty)
            # Agregar issue de SSL
            ssl_issue = SEOIssue(
                icon="🔐",
                title="Certificado SSL expirado o inválido",
                problem="El certificado HTTPS del sitio está expirado o no es válido",
                impact="Los navegadores mostrarán advertencias de seguridad. Visitantes abandonan el sitio. Google penaliza en rankings.",
                solution="Renovar certificado SSL inmediatamente. Contactar al proveedor de hosting.",
                priority="CRÍTICO",
                category="technical",
                estimated_monthly_loss=1_200_000,
                fix_time="Inmediato (contactar hosting)",
                score_impact=seo_penalty
            )
            issues.insert(0, ssl_issue)
        
        content_plan = self._generate_content_plan_enhanced()
        competitor_analysis = self._analyze_competition_enhanced() if include_competitor_analysis else ""
        financial_impact = self._calculate_financial_impact(issues)
        roadmap = self._generate_implementation_roadmap_enhanced(issues)
        keywords = self._generate_local_keywords(max_keywords=8)

        self.metadata = {
            "business_name": self.business_name,
            "location": self.location,
            "final_url": self.page_analyzer.final_url,
            "generated_at": datetime.now().isoformat(),
            "title": self.page_analyzer.get_title(),
            "meta_description": self.page_analyzer.get_meta_description(),
        }

        page_data = {
            "headings": self.page_analyzer.get_headings(),
            "images_count": len(self.page_analyzer.get_images()),
            "links_count": len(self.page_analyzer.get_links()),
        }

        schema_result = self._analysis_cache.get("schema_result") or {}

        issues_serialized = [asdict(issue) for issue in issues]

        return {
            "score": {
                "technical": self.score.technical,
                "content": self.score.content,
                "conversion": self.score.conversion,
                "local_seo": self.score.local_seo,
                "reputation": self.score.reputation,
                "total": penalized_total,  # ← Score con penalización aplicada
                "penalty_metadata": penalty_metadata,  # ← Trazabilidad
            },
            "issues": issues_serialized,
            "metadata": self.metadata,
            "competitors": competitors,
            "content_plan": content_plan,
            "competitor_analysis": competitor_analysis,
            "financial_impact": financial_impact,
            "roadmap": roadmap,
            "page_analyzer_data": page_data,
            "schema_result": schema_result,
            "keywords": keywords,
            "ssl_fallback_info": ssl_info,  # Trazabilidad SSL
        }
    
    def _calculate_scores_enhanced(self, issues: List[SEOIssue]) -> SEOScoreBreakdown:
        """Calcula scores mejorado integrando método de ai_studio_code."""
        # Método mejorado que combina ambos enfoques
        penalties = {"CRÍTICO": 25, "ALTO": 15, "MEDIO": 10, "BAJO": 5}
        
        technical_penalty = sum(penalties.get(i.priority, 0) for i in issues if i.category == "technical")
        content_penalty = sum(penalties.get(i.priority, 0) for i in issues if i.category == "content")
        conversion_penalty = sum(penalties.get(i.priority, 0) for i in issues if i.category == "conversion")
        local_penalty = sum(penalties.get(i.priority, 0) for i in issues if i.category == "local_seo")
        reputation_penalty = sum(penalties.get(i.priority, 0) for i in issues if i.category == "reputation")
        
        return SEOScoreBreakdown(
            technical=max(0, 100 - technical_penalty),
            content=max(0, 100 - content_penalty),
            conversion=max(0, 100 - conversion_penalty),
            local_seo=max(0, 100 - local_penalty),
            reputation=max(0, 100 - reputation_penalty)
        )
    
    def _generate_content_plan_enhanced(self) -> Dict[str, Any]:
        """Genera plan de contenido usando ProviderAdapter de ai_studio_code."""
        prompt = (
            f"Genera un plan de contenido SEO con 3 ideas concretas para un hotel llamado '{self.business_name}' "
            f"en {self.location}. Las ideas deben atraer a potenciales huéspedes. "
            "Incluye formatos como blog posts, FAQs y guías locales."
        )
        
        try:
            adapter = ProviderAdapter(self.provider_type)
            response = adapter.unified_request(prompt, max_tokens=250, temperature=0.5)
            
            # Parsear respuesta en estructura consistente
            return self._parse_content_response(response)
        except Exception as e:
            return self._fallback_content_plan()
    
    def _parse_content_response(self, response: str) -> Dict[str, Any]:
        """Parsea la respuesta del LLM en estructura estructurada."""
        lines = [line.strip() for line in response.split('\n') if line.strip() and not line.startswith('**')]
        
        blog_posts = [line for line in lines if 'blog' in line.lower() or 'guía' in line.lower()][:3]
        faqs = [line for line in lines if 'faq' in line.lower() or 'pregunta' in line.lower()][:2]
        guides = [line for line in lines if 'guía' in line.lower() or 'actividad' in line.lower()][:2]
        
        return {
            'blog_posts': blog_posts if blog_posts else [
                f"Guía completa de hoteles en {self.location}",
                f"Beneficios de los hoteles con aguas termales en {self.location}",
                f"Consejos para elegir el mejor hotel en {self.location}"
            ],
            'faqs': faqs if faqs else [
                f"¿Qué servicios incluye {self.business_name}?",
                f"¿Cómo llegar a {self.business_name} desde el aeropuerto?"
            ],
            'local_guides': guides if guides else [
                f"Las 5 mejores actividades cerca de {self.business_name}",
                f"Restaurantes y comida típica en {self.location}"
            ]
        }
    
    def _fallback_content_plan(self) -> Dict[str, Any]:
        """Plan de contenido por defecto."""
        return {
            'blog_posts': [
                f"Guía completa de hoteles en {self.location}",
                f"Beneficios de los hoteles con aguas termales en {self.location}",
                f"Consejos para elegir el mejor hotel en {self.location}"
            ],
            'faqs': [
                f"¿Qué servicios incluye {self.business_name}?",
                f"¿Cómo llegar a {self.business_name} desde el aeropuerto?"
            ],
            'local_guides': [
                f"Las 5 mejores actividades cerca de {self.business_name}",
                f"Restaurantes y comida típica en {self.location}"
            ]
        }

    def _generate_local_keywords(self, max_keywords: int = 8) -> List[str]:
        location_label = (self.location or "Colombia").strip() or "Colombia"
        prompt = (
            "Genera una lista de 8 keywords de cola larga en español para impulsar reservas directas de "
            f"un hotel llamado '{self.business_name}' ubicado en {location_label}. Solo la keyword por línea, sin numeración."
        )
        try:
            adapter = ProviderAdapter(self.provider_type)
            response = adapter.unified_request(prompt, max_tokens=200, temperature=0.4)
            keywords = self._parse_keywords_block(response)
            if keywords:
                return keywords[:max_keywords]
        except Exception:
            pass
        return self._fallback_keywords(location_label, max_keywords)

    def _parse_keywords_block(self, raw_text: str) -> List[str]:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        keywords: List[str] = []
        for line in lines:
            keyword = re.sub(r"^[0-9]+[)\.-]\s*", "", line)
            if keyword:
                keywords.append(keyword.lower())
        unique: List[str] = []
        seen = set()
        for kw in keywords:
            if kw not in seen:
                unique.append(kw)
                seen.add(kw)
        return unique

    def _fallback_keywords(self, location_label: str, max_keywords: int) -> List[str]:
        base = location_label.lower()
        tokens = [token for token in re.split(r"[,;]\s*", base) if token]
        zone = tokens[0] if tokens else base
        suggestions = [
            f"hotel boutique en {zone}",
            f"alojamiento familiar en {zone}",
            f"hotel con termales en {zone}",
            f"mejor hotel para parejas en {zone}",
            f"hotel pet friendly en {zone}",
            f"hotel con jacuzzi privado en {zone}",
        ]
        return suggestions[:max_keywords]
    
    def _analyze_competition_enhanced(self) -> str:
        """Análisis competitivo mejorado."""
        # Este análisis podría expandirse con web_search en implementación real
        return (
            f"**Competidores clave en {self.location}:**\n"
            "- **Hotel Termales del Ruiz:** Fuerte presencia en Google Maps, muchas reseñas positivas, buen uso de Schema de Hotel.\n"
            "- **Finca Hotel El Rosario:** Muy activo en Instagram, buenas fotografías pero sitio web lento.\n\n"
            "**Oportunidades identificadas:**\n"
            "- Esquemas de rich snippets poco utilizados por la competencia\n"
            "- Contenido local específico sobre actividades en la zona\n"
            "- Optimización móvil inconsistente en competidores directos"
        )
    
    def _calculate_financial_impact(self, issues: List[SEOIssue]) -> Dict[str, Any]:
        """Calcula el impacto financiero mejorado."""
        total_loss = sum(issue.estimated_monthly_loss for issue in issues)
        recoverable_percentage = 0.7  # 70% recuperable
        
        return {
            'estimated_monthly_loss': total_loss,
            'potential_improvement_percentage': self._calculate_improvement_potential(issues),
            'projected_monthly_gain': int(total_loss * recoverable_percentage),
            'recoverable_percentage': int(recoverable_percentage * 100)
        }
    
    def _calculate_improvement_potential(self, issues: List[SEOIssue]) -> int:
        """Calcula el potencial de mejora basado en issues críticos/altos."""
        critical_high_count = sum(1 for issue in issues if issue.priority in ['CRÍTICO', 'ALTO'])
        
        if critical_high_count >= 5:
            return 85
        elif critical_high_count >= 3:
            return 65
        elif critical_high_count >= 1:
            return 45
        else:
            return 25
    
    def _generate_implementation_roadmap_enhanced(self, issues: List[SEOIssue]) -> Dict[str, List[Dict[str, Any]]]:
        """Genera roadmap de implementación priorizado mejorado."""
        critical = [i for i in issues if i.priority == "CRÍTICO"]
        high = [i for i in issues if i.priority == "ALTO"]
        medium = [i for i in issues if i.priority == "MEDIO"]
        low = [i for i in issues if i.priority == "BAJO"]
        
        roadmap = {
            'semana_1_2': [],
            'semana_3_4': [],
            'mes_2': []
        }
        
        # Semana 1-2: Críticos
        for issue in critical[:5]:
            roadmap['semana_1_2'].append({
                'tarea': issue.title,
                'descripcion': issue.problem,
                'tiempo': issue.fix_time,
                'impacto': f"Recuperación estimada: ${issue.estimated_monthly_loss:,} COP/mes",
                'categoria': issue.category
            })
        
        # Semana 3-4: Altos
        for issue in high[:5]:
            roadmap['semana_3_4'].append({
                'tarea': issue.title,
                'descripcion': issue.problem,
                'tiempo': issue.fix_time,
                'impacto': f"Recuperación estimada: ${issue.estimated_monthly_loss:,} COP/mes",
                'categoria': issue.category
            })
        
        # Mes 2: Medios y bajos
        for issue in (medium + low)[:8]:
            roadmap['mes_2'].append({
                'tarea': issue.title,
                'descripcion': issue.problem,
                'tiempo': issue.fix_time,
                'impacto': f"Mejora incremental",
                'categoria': issue.category
            })
        
        return roadmap

    def generate_markdown_report(self, analysis_result: Dict[str, Any]) -> str:
        """Genera el reporte final en formato Markdown mejorado."""
        return ReportGeneratorEnhanced(
            url=self.url,
            business_name=self.business_name,
            location=self.location,
            analysis_result=analysis_result
        ).generate()


class ReportGeneratorEnhanced:
    """Genera reportes Markdown mejorados integrando lo mejor de ambos módulos."""
    
    def __init__(self, url: str, business_name: str, location: str, analysis_result: Dict[str, Any]):
        self.url = url
        self.business_name = business_name
        self.location = location
        self.analysis_result = analysis_result
    
    def generate(self) -> str:
        """Genera el reporte Markdown completo."""
        sections = [
            self._generate_executive_summary(),
            self._generate_detailed_analysis(),
            self._generate_implementation_roadmap(),
            self._generate_content_plan(),
            self._generate_keywords_section(),
        ]

        if self.analysis_result.get('competitor_analysis'):
            sections.append(self._generate_competitor_analysis())

        sections.append(self._generate_final_recommendations())

        return "\n".join(section for section in sections if section)
    
    def _generate_executive_summary(self) -> str:
        """Genera resumen ejecutivo mejorado."""
        score = self.analysis_result['score']
        financial = self.analysis_result['financial_impact']
        site = urlparse(self.url).netloc.upper()

        section = [
            f"# 🎯 DIAGNÓSTICO SEO ESTRUCTURADO - {site}",
            f"**Hotel:** {self.business_name}",
            f"**Ubicación:** {self.location}",
            f"**URL:** {self.url}",
            f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 📊 RESUMEN EJECUTIVO",
            "",
            f"### Score SEO Global: **{score['total']}/100**",
            "```",
            f"  Técnico:    {score['technical']}/100  {'█' * (score['technical']//5)}",
            f"  Contenido:  {score['content']}/100  {'█' * (score['content']//5)}",
            f"  Conversión: {score['conversion']}/100  {'█' * (score['conversion']//5)}",
            f"  Local SEO:  {score['local_seo']}/100  {'█' * (score['local_seo']//5)}",
            f"  Reputación: {score['reputation']}/100  {'█' * (score['reputation']//5)}",
            "```",
            "",
            "### 💰 Impacto Financiero",
            f"- **Ingresos mensuales perdidos estimados:** ${financial['estimated_monthly_loss']:,} COP",
            f"- **Potencial de mejora:** {financial['potential_improvement_percentage']}%",
            f"- **Ganancia mensual proyectada tras fixes:** ${financial['projected_monthly_gain']:,} COP",
            "- **ROI esperado:** 300-500% en primeros 3 meses",
        ]

        return "\n".join(section)
    
    def _generate_detailed_analysis(self) -> str:
        """Genera análisis detallado con issues categorizados."""
        issues = self.analysis_result['issues']
        
        if not issues:
            return "## ✅ No se encontraron problemas críticos de SEO\n"
        
        by_priority: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for issue in issues:
            by_priority[issue.get('priority', 'MEDIO')].append(issue)
        
        section = ["## 🚨 ANÁLISIS DETALLADO", ""]
        
        priority_order = ['CRÍTICO', 'ALTO', 'MEDIO', 'BAJO']
        priority_icons = {'CRÍTICO': '🔴', 'ALTO': '🟠', 'MEDIO': '🟡', 'BAJO': '🟢'}
        
        for priority in priority_order:
            group = by_priority.get(priority)
            if not group:
                continue
            
            section.append(f"### {priority_icons[priority]} Problemas de Prioridad {priority} ({len(group)})")
            section.append("")
            
            for issue in group:
                section.append(f"#### {issue.get('icon', '•')} {issue.get('title', 'Issue')}")
                section.append(f"**Problema:** {issue.get('problem', 'No disponible')}")
                section.append(f"**Impacto:** {issue.get('impact', 'Sin datos de impacto')}")
                section.append(f"**Solución:** {issue.get('solution', 'Sin recomendación')}")
                loss = issue.get('estimated_monthly_loss')
                improvement = issue.get('estimated_improvement')
                if isinstance(loss, int) and loss > 0:
                    section.append(f"**Pérdida estimada:** ${loss:,} COP/mes")
                if improvement:
                    section.append(f"**Mejora esperada:** {improvement}")
                section.append(f"**Tiempo de implementación:** {issue.get('fix_time', 'N/D')}")
                category = issue.get('category', 'general').replace('_', ' ').title()
                section.append(f"**Categoría:** {category}")
                section.append("")
        
        return "\n".join(section)
    
    def _generate_implementation_roadmap(self) -> str:
        """Genera hoja de ruta de implementación."""
        roadmap = self.analysis_result['roadmap']
        
        section = [
            "## 🗺️ HOJA DE RUTA DE IMPLEMENTACIÓN",
            "",
            "### 📅 Semana 1-2: Correcciones Críticas (Impacto Inmediato)"
        ]
        
        for task in roadmap.get('semana_1_2', []):
            section.append(f"- [ ] **{task['tarea']}** - {task['tiempo']} → {task['impacto']}")
        
        section.extend([
            "",
            "### 📅 Semana 3-4: Optimizaciones Principales (Alto Impacto)"
        ])
        
        for task in roadmap.get('semana_3_4', []):
            section.append(f"- [ ] **{task['tarea']}** - {task['tiempo']} → {task['impacto']}")
        
        section.extend([
            "",
            "### 📅 Mes 2: Mejoras Continuas (Impacto Medio-Bajo)"
        ])
        
        for task in roadmap.get('mes_2', []):
            section.append(f"- [ ] **{task['tarea']}** - {task['tiempo']} → {task['impacto']}")
        
        section.append("")
        return "\n".join(section)
    
    def _generate_content_plan(self) -> str:
        """Genera sección de plan de contenido."""
        content_plan = self.analysis_result.get('content_plan', {})
        
        if not content_plan:
            return ""
        
        section = [
            "## ✍️ PLAN DE CONTENIDO SEO RECOMENDADO",
            ""
        ]
        
        if content_plan.get('blog_posts'):
            section.append("### 📝 Artículos de Blog Sugeridos")
            for i, post in enumerate(content_plan['blog_posts'][:3], 1):
                section.append(f"{i}. {post}")
            section.append("")
        
        if content_plan.get('faqs'):
            section.append("### ❓ Preguntas Frecuentes (FAQ)")
            for i, faq in enumerate(content_plan['faqs'][:2], 1):
                section.append(f"{i}. {faq}")
            section.append("")
        
        if content_plan.get('local_guides'):
            section.append("### 🗺️ Guías Locales")
            for i, guide in enumerate(content_plan['local_guides'][:2], 1):
                section.append(f"{i}. {guide}")
            section.append("")
        
        return "\n".join(section)

    def _generate_keywords_section(self) -> str:
        keywords = self.analysis_result.get('keywords', [])
        if not keywords:
            return ""
        lines = ["## 🔑 KEYWORDS LOCALES RECOMENDADAS", ""]
        for idx, keyword in enumerate(keywords, 1):
            lines.append(f"{idx}. `{keyword}`")
        return "\n".join(lines)
    
    def _generate_competitor_analysis(self) -> str:
        """Genera análisis competitivo."""
        competitor_analysis = self.analysis_result.get('competitor_analysis', '')
        
        if not competitor_analysis:
            return ""
        
        return f"## 🎯 ANÁLISIS COMPETITIVO\n\n{competitor_analysis}\n"
    
    def _generate_final_recommendations(self) -> str:
        """Genera recomendaciones finales."""
        return """
## 💡 RECOMENDACIONES FINALES

### Acciones Inmediatas (Hoy)
1. ✅ Activar certificado SSL si no tienes HTTPS
2. ✅ Actualizar título y meta description  
3. ✅ Agregar botón de WhatsApp flotante
4. ✅ Reclamar perfil en Google Business Profile

### Próximos 7 Días
1. 📸 Optimizar todas las imágenes (alt tags + compresión)
2. 🏨 Implementar Schema.org tipo Hotel
3. ⭐ Agregar sección de testimonios
4. 📱 Verificar responsive en móviles reales

### Estrategia a 30 Días
1. ✍️ Publicar primer artículo de blog optimizado
2. 🌐 Reclamar y optimizar perfiles en TripAdvisor
3. 📊 Configurar Google Analytics y Search Console
4. 🎯 Iniciar campaña de recolección de reseñas

---
*Diagnóstico generado por SEO Accelerator Pro Enhanced*  
*Próxima revisión recomendada: 30 días*
"""
def quick_analyze(
    url: str,
    provider_type: Optional[str] = None,
    business_name: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    """Ejecuta un diagnóstico rápido y devuelve el reporte en Markdown."""
    accelerator = SEOAcceleratorProEnhanced(
        url=url,
        business_name=business_name or "Hotel",
        location=location or "Colombia",
        provider_type=provider_type,
    )
    result = accelerator.analyze_complete(include_competitor_analysis=False)
    return accelerator.generate_markdown_report(result)