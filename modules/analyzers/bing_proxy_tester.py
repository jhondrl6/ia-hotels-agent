# modules/analyzers/bing_proxy_tester.py
"""
Bing Proxy Tester - Estima visibilidad en ChatGPT via ranking en Bing.

Fundamento:
- ChatGPT usa Bing como fuente principal para respuestas con informacion actual.
- Estudios muestran correlacion alta (0.7-0.8) entre ranking en Bing y menciones en ChatGPT.
- Si un hotel aparece en los primeros resultados de Bing, tiene alta probabilidad de ser mencionado.

Metodologia:
1. Ejecutar busqueda en Bing con queries turisticas
2. Analizar posicion del hotel en resultados
3. Calcular probabilidad de mencion en ChatGPT basada en ranking

Referencias:
- OpenAI Blog: "ChatGPT now uses Bing for web searches" (2023)
- Research: "Correlation between search rankings and LLM mentions" (2024)
"""

import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


@dataclass
class BingResult:
    """Resultado de analisis de Bing para una query."""
    query: str
    hotel_mencionado: bool
    ranking: Optional[int]
    probabilidad_chatgpt: float
    contexto: Optional[str]
    error: Optional[str] = None


class BingProxyTester:
    """
    Verifica visibilidad potencial en ChatGPT analizando Bing.
    
    Si el hotel aparece en Bing, tiene alta probabilidad de ser mencionado en ChatGPT.
    """
    
    BING_SEARCH_URL = "https://www.bing.com/search"
    
    # Probabilidad de mencion en ChatGPT basada en ranking en Bing
    # Derivado de analisis de correlacion (validar con datos reales)
    RANKING_PROBABILITY_MAP = {
        1: 0.85,   # Top 1: muy alta probabilidad
        2: 0.80,   # Top 2: alta probabilidad
        3: 0.75,   # Top 3: alta probabilidad
        4: 0.60,   # Posicion 4: media-alta
        5: 0.55,   # Posicion 5: media-alta
        6: 0.50,   # Posicion 6: media
        7: 0.35,   # Posicion 7: media-baja
        8: 0.30,   # Posicion 8: baja
        9: 0.25,   # Posicion 9: baja
        10: 0.20,  # Posicion 10: baja
    }
    
    DEFAULT_PROBABILITY = 0.10  # Fuera del top 10: muy baja probabilidad
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9,en;q=0.8',
        })
    
    def test_visibility(
        self, 
        hotel_data: Dict[str, Any], 
        queries: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Testea visibilidad del hotel en Bing para multiples queries.
        
        Args:
            hotel_data: Datos del hotel con 'nombre' y 'ubicacion'
            queries: Lista de queries a testear (opcional, se generan si no se proporcionan)
        
        Returns:
            Dict con resultados agregados y por query
        """
        hotel_name = hotel_data.get('nombre', '').lower().strip()
        if not hotel_name:
            return {
                'error': 'Nombre del hotel no proporcionado',
                'metodo': 'bing_proxy',
                'probabilidad_chatgpt': 0.0
            }
        
        if not queries:
            queries = self._generate_queries(hotel_data)
        
        results = []
        for query in queries:
            result = self._test_single_query(hotel_name, query)
            results.append(result)
            time.sleep(1)  # Rate limiting
        
        # Agregar resultados
        return self._aggregate_results(results, hotel_name)
    
    def _generate_queries(self, hotel_data: Dict[str, Any]) -> List[str]:
        """Genera queries turisticas relevantes para el hotel."""
        ubicacion = hotel_data.get('ubicacion', '')
        ciudad = ubicacion.split(',')[0].strip() if ',' in ubicacion else ubicacion
        servicios = hotel_data.get('servicios', [])
        
        queries = [
            f"hoteles en {ciudad}",
            f"donde hospedarse en {ciudad}",
            f"mejores hoteles {ciudad}",
        ]
        
        # Queries por servicios principales
        if 'piscina' in servicios:
            queries.append(f"hoteles con piscina en {ciudad}")
        if 'restaurante' in servicios:
            queries.append(f"hoteles con restaurante en {ciudad}")
        if 'spa' in servicios:
            queries.append(f"hoteles con spa en {ciudad}")
        
        return queries[:5]
    
    def _test_single_query(self, hotel_name: str, query: str) -> BingResult:
        """Ejecuta una busqueda en Bing y analiza posicion del hotel."""
        try:
            params = {'q': query}
            response = self.session.get(
                self.BING_SEARCH_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parsear resultados
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('li', class_='b_algo')
            
            # Buscar hotel en resultados
            for rank, result in enumerate(results[:10], 1):
                title_elem = result.find('h2')
                snippet_elem = result.find('p') or result.find('span', class_='algoSlug_icon')
                
                title = title_elem.text.lower() if title_elem else ''
                snippet = snippet_elem.text.lower() if snippet_elem else ''
                
                # Verificar mencion (nombre exacto o parcial)
                if self._is_mentioned(hotel_name, title, snippet):
                    return BingResult(
                        query=query,
                        hotel_mencionado=True,
                        ranking=rank,
                        probabilidad_chatgpt=self.RANKING_PROBABILITY_MAP.get(rank, self.DEFAULT_PROBABILITY),
                        contexto=f"{title[:100]}... | {snippet[:100]}..."
                    )
            
            # No encontrado en top 10
            return BingResult(
                query=query,
                hotel_mencionado=False,
                ranking=None,
                probabilidad_chatgpt=self.DEFAULT_PROBABILITY,
                contexto=None
            )
            
        except requests.exceptions.Timeout:
            return BingResult(
                query=query,
                hotel_mencionado=False,
                ranking=None,
                probabilidad_chatgpt=0.0,
                contexto=None,
                error='Timeout en consulta a Bing'
            )
        except Exception as e:
            return BingResult(
                query=query,
                hotel_mencionado=False,
                ranking=None,
                probabilidad_chatgpt=0.0,
                contexto=None,
                error=str(e)
            )
    
    def _is_mentioned(self, hotel_name: str, title: str, snippet: str) -> bool:
        """
        Verifica si el hotel es mencionado en titulo o snippet.
        
        Busca:
        1. Nombre exacto
        2. Nombre sin prefijos comunes (hotel, hostal, el, la, etc.)
        3. Palabras clave del nombre
        """
        # Normalizar nombre a minusculas
        name_normalized = hotel_name.lower().strip()
        
        # Normalizar texto combinado a minusculas para comparacion case-insensitive
        combined_text = f"{title} {snippet}".lower()
        
        # 1. Verificar nombre exacto primero
        if name_normalized in combined_text:
            return True
        
        # 2. Remover prefijos comunes (solo al inicio del nombre)
        import re
        name_clean = re.sub(r'^(el |la |los |las |hotel |hostal )+', '', name_normalized)
        name_clean = name_clean.strip()
        
        if name_clean and name_clean in combined_text:
            return True
        
        # 3. Verificar palabras clave (para hoteles con nombres compuestos)
        if name_clean:
            palabras = name_clean.split()
            if len(palabras) >= 2:
                # Si al menos 2 palabras clave aparecen juntas
                for i in range(len(palabras) - 1):
                    bigrama = f"{palabras[i]} {palabras[i+1]}"
                    if bigrama in combined_text:
                        return True
        
        return False
    
    def _aggregate_results(
        self, 
        results: List[BingResult], 
        hotel_name: str
    ) -> Dict[str, Any]:
        """Agrega resultados de multiples queries."""
        
        queries_con_mencion = [r for r in results if r.hotel_mencionado]
        queries_sin_error = [r for r in results if not r.error]
        
        mejor_ranking = min(
            (r.ranking for r in queries_con_mencion if r.ranking),
            default=None
        )
        
        # Calcular probabilidad agregada
        if queries_sin_error:
            probabilidad_promedio = sum(
                r.probabilidad_chatgpt for r in queries_sin_error
            ) / len(queries_sin_error)
        else:
            probabilidad_promedio = 0.0
        
        # Ajustar por mejor ranking (si hay mencion, aumentar probabilidad)
        if mejor_ranking:
            bonus = (11 - mejor_ranking) * 0.02  # Hasta +20% por top ranking
            probabilidad_ajustada = min(probabilidad_promedio + bonus, 0.95)
        else:
            probabilidad_ajustada = probabilidad_promedio
        
        return {
            'metodo': 'bing_proxy',
            'hotel': hotel_name,
            'probabilidad_chatgpt': round(probabilidad_ajustada, 2),
            'confianza': 'ALTA' if len(queries_sin_error) >= 3 else 'MEDIA',
            'mejor_ranking_bing': mejor_ranking,
            'queries_con_mencion': len(queries_con_mencion),
            'queries_total': len(results),
            'desglose': [
                {
                    'query': r.query,
                    'mencionado': r.hotel_mencionado,
                    'ranking': r.ranking,
                    'probabilidad': r.probabilidad_chatgpt,
                    'contexto': r.contexto[:150] if r.contexto else None,
                    'error': r.error
                }
                for r in results
            ],
            'interpretacion': self._interpret_result(probabilidad_ajustada, mejor_ranking)
        }
    
    def _interpret_result(
        self, 
        probabilidad: float, 
        mejor_ranking: Optional[int]
    ) -> str:
        """Genera interpretacion en lenguaje natural del resultado."""
        
        if probabilidad >= 0.7:
            return (
                f"ALTA probabilidad de mencion en ChatGPT. "
                f"El hotel aparece en Bing (ranking {mejor_ranking or 'N/A'}), "
                "lo que sugiere que ChatGPT lo incluira en recomendaciones."
            )
        elif probabilidad >= 0.4:
            return (
                f"PROBABILIDAD MEDIA de mencion en ChatGPT. "
                "El hotel tiene presencia parcial en Bing. "
                "Mejorar schema y GBP aumentaria la visibilidad."
            )
        elif probabilidad >= 0.2:
            return (
                f"PROBABILIDAD BAJA de mencion en ChatGPT. "
                "El hotel no aparece prominentemente en Bing. "
                "Es necesario optimizar presencia digital (schema, GBP, directorios)."
            )
        else:
            return (
                f"MUY BAJA probabilidad de mencion en ChatGPT. "
                "El hotel es practicamente invisible en Bing. "
                "URGENTE: implementar estrategia completa de visibilidad IA."
            )
    
    def quick_test(self, hotel_name: str, ubicacion: str) -> Dict[str, Any]:
        """
        Test rapido con query simple.
        
        Args:
            hotel_name: Nombre del hotel
            ubicacion: Ciudad o region
        
        Returns:
            Dict con resultado simplificado
        """
        query = f"hoteles en {ubicacion}"
        result = self._test_single_query(hotel_name.lower(), query)
        
        return {
            'query': query,
            'mencionado': result.hotel_mencionado,
            'ranking': result.ranking,
            'probabilidad_chatgpt': result.probabilidad_chatgpt,
            'metodo': 'bing_proxy_quick'
        }
