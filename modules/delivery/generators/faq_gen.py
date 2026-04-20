import json
from typing import List, Dict, Any, Tuple
from modules.providers.llm_provider import ProviderAdapter
from datetime import datetime
import pytz

class FAQGenerator:
    """Generates optimized FAQs using the configured LLM provider."""
    
    def __init__(self, provider_type: str = "auto"):
        self.llm_provider = ProviderAdapter(provider_type)

    def generate(self, hotel_data: Dict[str, Any], count: int = 50, reason: str = None) -> Tuple[str, str]:
        """
        Generates a list of FAQs optimized for AI discovery in JSON-LD format.
        
        Args:
            hotel_data: Datos del hotel
            count: Número de FAQs a generar
            reason: Justificación de por qué se genera este archivo
            
        Returns:
            Tuple de (jsonld_content, implementation_guide)
        """
        hotel_name = hotel_data.get('nombre', 'Hotel')
        url = hotel_data.get('website', hotel_data.get('url', ''))
        
        faqs = self.generate_list(hotel_data, count)
        if not faqs:
            empty_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": []
            }
            return (json.dumps(empty_schema, indent=2, ensure_ascii=False), "")
        
        # Build JSON-LD FAQPage schema
        main_entities = []
        for item in faqs:
            entity = {
                "@type": "Question",
                "name": item["pregunta"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["respuesta"]
                }
            }
            main_entities.append(entity)
        
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entities
        }
        
        jsonld_content = json.dumps(faq_schema, indent=2, ensure_ascii=False)
        
        implementation_guide = f"""# Guía de Implementación - FAQs
## {hotel_name}

Este archivo contiene FAQs en formato JSON-LD (schema.org FAQPage).
Optimizado para SEO y búsqueda por voz.

## Instrucciones
1. Inserta el JSON-LD en un <script type="application/ld+json"> en tu página de FAQs
2. Cada pregunta/respuesta está estructurada como schema.org Question/Answer
3. Google y otros buscadores reconocerán automáticamente el formato FAQPage
"""
        
        return (jsonld_content, implementation_guide)

    def generate_list(self, hotel_data: Dict[str, Any], count: int = 50) -> List[Dict[str, str]]:
        """
        Generates a list of FAQs as dictionaries.
        
        Returns:
            List of Dicts with 'pregunta' and 'respuesta'.
        """
        prompt = f"""
        Actúa como un experto en SEO para búsqueda por voz y optimización para asistentes de IA (AEO).
        Genera una lista de {count} Preguntas Frecuentes (FAQs) estratégicas para el hotel: "{hotel_data.get('nombre')}" ubicado en "{hotel_data.get('ubicacion')}".
        
        El objetivo es que estas preguntas cubran la intención de búsqueda transaccional e informacional para capturar tráfico de ChatGPT, Gemini y Perplexity.
        
        Contexto del hotel:
        - Servicios: {', '.join(hotel_data.get('servicios', []))}
        - Precio promedio: {hotel_data.get('precio_promedio', 'N/D')}
        
        Reglas de formato:
        1. Salida estricta en formato CSV: Pregunta,Respuesta
        2. Sin encabezados, sin numeración, sin texto introductorio.
        3. Las respuestas deben ser naturales, conversacionales y mencionar el nombre del hotel y la ubicación.
        4. Las RESPUESTAS deben tener entre 40 y 60 palabras para optimización TTS (Text-to-Speech).
        5. Incluye preguntas sobre: ubicación, mascotas, check-in/out, desayuno, wifi, parking, parejas, familia, turismo cercano.
        """
        
        try:
            response = self.llm_provider.unified_request(prompt)
            faqs = []
            for line in response.split('\n'):
                if ',' in line:
                    # Basic CSV parsing (splitting by first comma if not quoted, but LLM usually gives simple comma)
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        faqs.append({
                            "pregunta": parts[0].strip().strip('"'),
                            "respuesta": parts[1].strip().strip('"')
                        })
            return faqs
        except Exception as e:
            print(f"Error in FAQGenerator: {e}")
            return []
