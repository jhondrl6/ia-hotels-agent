# modules/analyzers/ia_tester.py
"""
IA Visibility Tester - Evalua visibilidad del hotel en asistentes de IA.

Metodos disponibles:
1. Perplexity API (si PERPLEXITY_API_KEY configurada)
2. OpenAI/ChatGPT API (si OPENAI_API_KEY configurada)
3. Bing Proxy (alternativa cuando OpenAI no disponible)
4. LLM Simulation con DeepSeek (siempre disponible como fallback)
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Import provider adapter
try:
    from modules.providers.llm_provider import ProviderAdapter
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from providers.llm_provider import ProviderAdapter

# Import Bing Proxy Tester as alternative
try:
    from modules.analyzers.bing_proxy_tester import BingProxyTester
except ImportError:
    BingProxyTester = None


class IATester:
    """Evalua visibilidad del hotel en multiples asistentes de IA."""
    
    def __init__(self):
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.cache_path = Path("data/cache/ia_visibility.json")
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._history = self._load_history()
        
        # Inicializar Bing Proxy como alternativa
        self.bing_proxy = BingProxyTester() if BingProxyTester else None
    
    def test_hotel(self, hotel_data):
        """Evaluate hotel visibility across multiple LLM assistants."""
        queries = self._generate_queries(hotel_data)
        
        key = self._build_history_key(hotel_data)
        previous_snapshot = self._latest_snapshot(key)

        results = {
            'perplexity': {'menciones': 0, 'posicion': None, 'detalles': []},
            'chatgpt': {'menciones': 0, 'posicion': None, 'detalles': []},
            'bing_proxy': {'menciones': 0, 'probabilidad_chatgpt': 0.0, 'detalles': []},
            'llm_simulation': {'mencionado': False, 'proveedor': None},
            'queries_testeadas': queries,
            'total_queries': len(queries),
            'metodos_disponibles': []
        }
        
        # Test with Perplexity (if API key configured)
        if self.perplexity_key:
            results['perplexity'] = self._test_perplexity(hotel_data, queries, self.perplexity_key)
            results['metodos_disponibles'].append('perplexity')
        else:
            results['perplexity']['error'] = 'PERPLEXITY_API_KEY no configurada'
        
        # Test with ChatGPT (if API key configured)
        if self.openai_key:
            chatgpt_result = self._test_openai(hotel_data, queries, self.openai_key)
            results['chatgpt'] = chatgpt_result
            results['metodos_disponibles'].append('chatgpt')
            
            # Si ChatGPT falla, usar Bing Proxy como alternativa
            if chatgpt_result.get('error') and self.bing_proxy:
                results['bing_proxy'] = self._test_bing_proxy(hotel_data, queries)
                results['metodos_disponibles'].append('bing_proxy')
                results['chatgpt']['alternativa_usada'] = 'bing_proxy'
        else:
            results['chatgpt']['error'] = 'OPENAI_API_KEY no configurada'
            # Usar Bing Proxy como alternativa cuando no hay OpenAI
            if self.bing_proxy:
                results['bing_proxy'] = self._test_bing_proxy(hotel_data, queries)
                results['metodos_disponibles'].append('bing_proxy')
                results['chatgpt']['alternativa_usada'] = 'bing_proxy'
        
        # LLM Simulation with configured provider (Anthropic or DeepSeek)
        if self.anthropic_key or self.deepseek_key:
            results['llm_simulation'] = self._test_llm_simulation(hotel_data, queries)
            results['metodos_disponibles'].append('llm_simulation')

        results.setdefault('meta', {})
        if previous_snapshot:
            results['meta'].update({
                'prev_timestamp': previous_snapshot.get('timestamp'),
                'prev_mentions': {
                    'perplexity': previous_snapshot.get('perplexity_menciones'),
                    'chatgpt': previous_snapshot.get('chatgpt_menciones'),
                    'gemini': previous_snapshot.get('gemini_menciones'),
                }
            })

        self._persist_results(key, hotel_data, results)
        return results
    
    def _load_history(self):
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open('r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception:
            return {}

    def _build_history_key(self, hotel_data):
        nombre = (hotel_data.get('nombre') or '').strip().lower()
        ubicacion = (hotel_data.get('ubicacion') or '').strip().lower()
        compuesto = f"{nombre}::{ubicacion}".strip(':')
        return compuesto if compuesto else "__unknown__"

    def _latest_snapshot(self, key):
        record = self._history.get(key, {})
        history = record.get('history') or []
        return history[-1] if history else None

    def _persist_results(self, key, hotel_data, results):
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'perplexity_menciones': results.get('perplexity', {}).get('menciones'),
            'chatgpt_menciones': results.get('chatgpt', {}).get('menciones'),
            'gemini_menciones': results.get('gemini', {}).get('menciones'),
            'bing_proxy_probabilidad': results.get('bing_proxy', {}).get('probabilidad_chatgpt'),
            'bing_proxy_ranking': results.get('bing_proxy', {}).get('mejor_ranking'),
            'llm_simulado': results.get('llm_simulation', {}).get('mencionado') if isinstance(results.get('llm_simulation'), dict) else None,
            'queries': results.get('queries_testeadas', []),
            'metodos_usados': results.get('metodos_disponibles', []),
        }

        record = self._history.setdefault(key, {
            'hotel': {
                'nombre': hotel_data.get('nombre'),
                'ubicacion': hotel_data.get('ubicacion'),
            },
            'history': []
        })

        record['hotel'].update({
            'servicios': hotel_data.get('servicios', []),
            'confidence': hotel_data.get('confidence'),
        })
        record['history'].append(snapshot)
        record['history'] = record['history'][-20:]

        try:
            with self.cache_path.open('w', encoding='utf-8') as fh:
                json.dump(self._history, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _test_llm_simulation(self, hotel_data, queries):
        """Simulate how an LLM would respond to tourist queries."""
        try:
            adapter = ProviderAdapter()
            query_sample = queries[0]
            
            content = adapter.unified_request(
                prompt=f"Recomiendame 3 hoteles para esta busqueda: {query_sample}",
                max_tokens=500
            )
            
            nombre = hotel_data['nombre'].lower()
            mencionado = nombre in content.lower()
            
            return {
                'mencionado': mencionado,
                'query_testeada': query_sample,
                'respuesta': content[:500],
                'interpretacion': (
                    'El hotel NO es mencionado porque no tiene datos estructurados para IA'
                    if not mencionado else
                    'El hotel ES mencionado'
                ),
                'proveedor_llm': adapter.get_current_provider()
            }
        
        except Exception as e:
            return {'error': str(e), 'mencionado': False}
    
    def _test_bing_proxy(self, hotel_data, queries):
        """
        Usa Bing como proxy para estimar visibilidad en ChatGPT.
        
        Alternativa cuando:
        - OPENAI_API_KEY no esta configurada
        - OpenAI API falla (error 429, timeout, etc.)
        
        Retorna probabilidad de mencion en ChatGPT basada en ranking en Bing.
        """
        if not self.bing_proxy:
            return {
                'error': 'BingProxyTester no disponible',
                'probabilidad_chatgpt': 0.0,
                'metodo': 'bing_proxy'
            }
        
        try:
            result = self.bing_proxy.test_visibility(hotel_data, queries)
            
            # Adaptar formato para compatibilidad con el resto del sistema
            return {
                'menciones': 1 if result.get('queries_con_mencion', 0) > 0 else 0,
                'probabilidad_chatgpt': result.get('probabilidad_chatgpt', 0.0),
                'mejor_ranking': result.get('mejor_ranking_bing'),
                'queries_con_mencion': result.get('queries_con_mencion', 0),
                'detalles': result.get('desglose', []),
                'interpretacion': result.get('interpretacion'),
                'metodo': 'bing_proxy',
                'confianza': result.get('confianza', 'MEDIA')
            }
        except Exception as e:
            return {
                'error': str(e),
                'menciones': 0,
                'probabilidad_chatgpt': 0.0,
                'metodo': 'bing_proxy'
            }
    
    def _generate_queries(self, hotel_data):
        """Generate contextual queries based on hotel data."""
        ubicacion = hotel_data.get('ubicacion', '')
        nombre = hotel_data.get('nombre', '')
        servicios = hotel_data.get('servicios', [])
        
        # Extract city name
        ciudad = ubicacion.split(',')[0].strip() if ',' in ubicacion else ubicacion
        
        queries = [
            f"hoteles en {ciudad}",
            f"donde hospedarse en {ciudad}",
            f"mejores hoteles {ciudad}",
            f"{nombre} opiniones",
        ]
        
        # Add queries based on key services
        if 'piscina' in servicios:
            queries.append(f"hoteles con piscina en {ciudad}")
        if 'restaurante' in servicios:
            queries.append(f"hoteles con restaurante en {ciudad}")
        
        return queries[:5]
    
    def _test_perplexity(self, hotel_data, queries, api_key):
        """Test hotel visibility using Perplexity API."""
        try:
            import requests
            
            menciones = 0
            detalles = []
            
            for query in queries:
                response = requests.post(
                    'https://api.perplexity.ai/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'llama-3.1-sonar-large-128k-online',
                        'messages': [
                            {'role': 'user', 'content': query}
                        ]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Count hotel mentions
                    nombre = hotel_data['nombre'].lower()
                    if nombre in content.lower():
                        menciones += 1
                        detalles.append({
                            'query': query,
                            'mencionado': True,
                            'contexto': content[:200]
                        })
                    else:
                        detalles.append({
                            'query': query,
                            'mencionado': False
                        })
                
                time.sleep(1)  # Rate limiting
            total_queries = len(queries) or 1
            
            return {
                'menciones': menciones,
                'posicion': None,
                'detalles': detalles,
                'tasa_mencion': f"{(menciones/total_queries*100):.1f}%"
            }
        
        except Exception as e:
            return {
                'menciones': 0,
                'error': str(e),
                'detalles': []
            }
    
    def _test_openai(self, hotel_data, queries, api_key):
        """Test hotel visibility using OpenAI ChatGPT."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            menciones = 0
            detalles = []
            
            for query in queries:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "user", "content": query}
                    ],
                    max_tokens=500
                )
                
                content = response.choices[0].message.content
                
                nombre = hotel_data['nombre'].lower()
                if nombre in content.lower():
                    menciones += 1
                    detalles.append({
                        'query': query,
                        'mencionado': True,
                        'contexto': content[:200]
                    })
                else:
                    detalles.append({
                        'query': query,
                        'mencionado': False
                    })
                
                time.sleep(1)
            total_queries = len(queries) or 1
            
            return {
                'menciones': menciones,
                'posicion': None,
                'detalles': detalles,
                'tasa_mencion': f"{(menciones/total_queries*100):.1f}%"
            }
        
        except Exception as e:
            error_str = str(e)
            # Identificar tipo de error para mejor manejo
            if '429' in error_str or 'quota' in error_str.lower():
                error_type = 'CUOTA_EXCEDIDA'
                error_msg = 'OpenAI API: Cuota excedida. Se usara Bing Proxy como alternativa.'
            elif 'timeout' in error_str.lower():
                error_type = 'TIMEOUT'
                error_msg = 'OpenAI API: Timeout. Se usara Bing Proxy como alternativa.'
            elif 'unauthorized' in error_str.lower() or 'invalid' in error_str.lower():
                error_type = 'API_KEY_INVALIDA'
                error_msg = 'OpenAI API: Clave invalida. Se usara Bing Proxy como alternativa.'
            else:
                error_type = 'ERROR_DESCONOCIDO'
                error_msg = f'OpenAI API: {error_str}'
            
            return {
                'menciones': 0,
                'posicion': None,
                'detalles': [],
                'error': error_msg,
                'error_tipo': error_type,
                'alternativa_recomendada': 'bing_proxy'
            }

    def _test_claude_simulation(self, hotel_data, queries):
        """Compatibility alias retained for legacy imports."""
        return self._test_llm_simulation(hotel_data, queries)
