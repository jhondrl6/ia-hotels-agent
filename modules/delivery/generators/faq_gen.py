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
            return ("\n".join(header_sections) + "\nPregunta,Respuesta,Categoria,Fecha_Generacion\nError generating FAQs", "")
            
        def asignar_categoria(pregunta, respuesta):
            texto = (pregunta + " " + respuesta).lower()
            if any(kw in texto for kw in ["check-in", "check-out", "hora de entrada", "hora de salida", "llegada", "salida"]):
                return "Hospedaje - Horarios"
            if any(kw in texto for kw in ["desayuno", "almuerzo", "cena", "buffet", "comida"]):
                return "Servicios - Alimentación"
            if any(kw in texto for kw in ["cancelación", "cancelar", "reembolso", "reserva"]):
                return "Reservas - Políticas"
            if any(kw in texto for kw in ["wifi", "wi-fi", "internet"]):
                return "Servicios - Conectividad"
            if any(kw in texto for kw in ["estacionamiento", "parqueadero", "parking"]):
                return "Servicios - Parqueadero"
            if any(kw in texto for kw in ["mascota", "perro", "gato", "pet"]):
                return "Servicios - Mascotas"
            if any(kw in texto for kw in ["piscina", "pool"]):
                return "Servicios - Piscina"
            if any(kw in texto for kw in ["traslado", "aeropuerto", "taxi", "transporte"]):
                return "Servicios - Transporte"
            if any(kw in texto for kw in ["spa", "masaje", "bienestar"]):
                return "Servicios - Spa"
            if any(kw in texto for kw in ["dieta", "vegano", "vegetariano", "sin gluten"]):
                return "Servicios - Dietas Especiales"
            if any(kw in texto for kw in ["habitación", "cuarto", "suite", "cama"]):
                return "Hospedaje - Habitaciones"
            if any(kw in texto for kw in ["precio", "costo", "tarifa"]):
                return "Reservas - Precios"
            return "Información General"
        
        BOGOTA_TZ = pytz.timezone('America/Bogota')
        ISO_TIMESTAMP = datetime.now(BOGOTA_TZ).isoformat(timespec='seconds')
        lines = ['"Pregunta","Respuesta","Categoria","Fecha_Generacion"']
        for item in faqs:
            q = item["pregunta"].replace('"', '""')
            a = item["respuesta"].replace('"', '""')
            c = asignar_categoria(item["pregunta"], item["respuesta"])
            lines.append(f'"{q}","{a}","{c}","{ISO_TIMESTAMP}"')
        
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
