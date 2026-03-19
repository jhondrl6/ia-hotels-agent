from typing import List, Dict, Any, Tuple
from modules.providers.llm_provider import ProviderAdapter

class FAQGenerator:
    """Generates optimized FAQs using the configured LLM provider."""
    
    def __init__(self, provider_type: str = "auto"):
        self.llm_provider = ProviderAdapter(provider_type)

    def generate(self, hotel_data: Dict[str, Any], count: int = 50, reason: str = None) -> Tuple[str, str]:
        """
        Generates a list of FAQs optimized for AI discovery in CSV format.
        
        Args:
            hotel_data: Datos del hotel
            count: Número de FAQs a generar
            reason: Justificación de por qué se genera este archivo
            
        Returns:
            Tuple de (csv_content, implementation_guide)
        """
        header_sections = []
        
        if reason:
            header_sections.append(f"> **🎯 Por qué este archivo:** {reason}")
            header_sections.append("")
        
        hotel_name = hotel_data.get('nombre', 'Hotel')
        header_sections.append(f"# FAQs Optimizadas - {hotel_name}")
        header_sections.append("")
        header_sections.append("Preguntas frecuentes optimizadas para búsqueda por voz y asistentes de IA.")
        header_sections.append("")
        
        faqs = self.generate_list(hotel_data, count)
        if not faqs:
            return ("\n".join(header_sections) + "\nPregunta,Respuesta\nError generating FAQs", "")
            
        lines = ["Pregunta,Respuesta"]
        for item in faqs:
            q = item["pregunta"].replace('"', '""')
            a = item["respuesta"].replace('"', '""')
            lines.append(f'"{q}","{a}"')
        
        csv_content = "\n".join(header_sections) + "\n".join(lines)
        
        implementation_guide = f"""# Guía de Implementación - FAQs
## {hotel_name}

Este archivo contiene FAQs optimizadas para SEO y búsqueda por voz.

## Instrucciones
1. Copia las preguntas y respuestas a tu sitio web
2. Agrega cada pregunta en una sección FAQ o página dedicada
3. Usa schema FAQPage para maximizar visibilidad en buscadores
"""
        
        return (csv_content, implementation_guide)

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
        4. Incluye preguntas sobre: ubicación, mascotas, check-in/out, desayuno, wifi, parking, parejas, familia, turismo cercano.
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
