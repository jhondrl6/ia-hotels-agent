"""
Generador de Toolkit para Consultor.
Crea herramientas internas para el consultor (no para el cliente).
"""

from pathlib import Path
from typing import Dict, Any


class ToolkitConsultorGenerator:
    """Genera herramientas de trabajo para el consultor"""
    
    def __init__(self):
        self.templates_path = Path("templates/toolkit")
        
    def generate_all(self, hotel_data: Dict[str, Any], llm_analysis: Dict[str, Any], output_dir: Path):
        """
        Genera todas las herramientas del consultor.
        
        Args:
            hotel_data: Datos del hotel
            llm_analysis: Análisis LLM
            output_dir: Directorio de salida principal del audit
        """
        toolkit_dir = output_dir / "_toolkit_consultor"
        toolkit_dir.mkdir(exist_ok=True)
        
        print("   Generando toolkit consultor...")
        
        # Generar scripts y guías
        self._generate_call_script(hotel_data, llm_analysis, toolkit_dir)
        self._generate_objeciones(hotel_data, llm_analysis, toolkit_dir)
        
        print(f"   [OK] Toolkit consultor generado en: _toolkit_consultor/")
        
    def _generate_call_script(self, hotel_data: Dict[str, Any], llm_analysis: Dict[str, Any], toolkit_dir: Path):
        """Genera script para videollamada de 20 minutos"""
        
        hotel_nombre = hotel_data.get('nombre', 'Hotel')
        ubicacion = hotel_data.get('ubicacion', 'la zona')
        perdida_mensual = llm_analysis.get('perdida_mensual_total', 0)
        paquete = llm_analysis.get('paquete_recomendado', 'Pro AEO')
        
        content = f"""# SCRIPT VIDEOLLAMADA 20 MINUTOS - {hotel_nombre}

## PRE-CALL (5 min antes)
- [ ] Revisar diagnóstico del hotel
- [ ] Buscar 2 competidores cercanos en Google Maps
- [ ] Abrir ChatGPT y preparar query en vivo
- [ ] Tener propuesta lista para compartir pantalla

---

## MINUTO 0-2: ROMPER HIELO

"Hola [Nombre], gracias por la llamada. ¿Ya tuvo chance de leer el diagnóstico?"

→ **Si SÍ:** "Perfecto, ¿qué le llamó más la atención?"
→ **Si NO:** "Sin problema, le muestro lo más importante en 3 minutos"

---

## MINUTO 2-8: DEMO EN VIVO (CRÍTICO)

[Compartir pantalla]

**1. Abrir ChatGPT**
   - Preguntar: "Recomiéndame hoteles cerca de {ubicacion}"
   
**2. Mostrar que NO aparece**
   - Señalar: "Mire, ChatGPT menciona estos 3 hoteles, pero {hotel_nombre} no está"
   
**3. Mostrar que Hotel X SÍ aparece**
   - "Este es su competencia directa, y sí está visible"
   
**4. Explicar la brecha**
   - "Esta es la brecha. 65% de viajeros jóvenes usan esto ahora"
   - "Cada vez que alguien pregunta, están perdiendo la oportunidad"

---

## MINUTO 8-12: SOLUCIÓN

[Mostrar propuesta en pantalla]

**MES 1: Hacerlo visible en IA**
- Instalamos "lenguaje IA" (Schema) en su web
- 30 preguntas-respuestas optimizadas
- Registramos en 20 plataformas que IA consulta

**MES 2: Optimizar Google Maps**
- 15 fotos profesionales (o los capacitamos)
- Posts semanales automáticos
- Botón WhatsApp visible

**MES 3: Ya recuperó la inversión**
- Dashboard para ver menciones en tiempo real
- Reportes semanales de posición

---

## MINUTO 12-18: MANEJO DE OBJECIONES

*[Ver documento objeciones_frecuentes.md para respuestas detalladas]*

**Objeciones comunes:**
1. "No tenemos presupuesto"
2. "Ya tenemos agencia de marketing"
3. "Necesito pensarlo / consultarlo"
4. "¿Por qué no hacerlo nosotros mismos?"

---

## MINUTO 18-20: CIERRE

**Preguntar:**
"¿Le hace sentido arrancar con {paquete}?"

→ **Si SÍ:** 
   "Perfecto, le envío contrato y arrancamos la próxima semana"
   "¿Prefiere que le enviemos el contrato por email o WhatsApp?"

→ **Si NO:** 
   "¿Qué necesitaría para tomar la decisión?"
   [Escuchar activamente y abordar la objeción específica]

→ **Si DUDA:** 
   "Entiendo. ¿Qué tal si le doy 48h para pensarlo y hablamos el [día específico]?"
   "Mientras, le dejo este video de 3 min con más ejemplos: [link]"

---

## POST-CALL (Inmediatamente después)

- [ ] Actualizar CRM con resultado (interés alto/medio/bajo)
- [ ] Agendar seguimiento si no cerró
- [ ] Enviar email de resumen con próximos pasos
- [ ] Si cerró: Enviar contrato dentro de 2 horas máximo

---

## DATOS CLAVE PARA ESTA LLAMADA

- **Pérdida mensual:** ${perdida_mensual:,.0f} COP
- **Paquete recomendado:** {paquete}
- **Ubicación:** {ubicacion}
- **Competidores cercanos:** [Buscar en Google Maps antes de la llamada]

---

## TIPS DE COMUNICACIÓN

✅ **HACER:**
- Mostrar, no solo decir (demo en vivo es crítico)
- Hablar en lenguaje simple, no técnico
- Usar ejemplos de competidores locales
- Generar urgencia con pérdida acumulada
- Preguntar más que hablar (ratio 60/40)

❌ **NO HACER:**
- Usar términos técnicos (Schema, JSON-LD, etc.)
- Hablar mal de competidores
- Prometer resultados exactos
- Presionar demasiado si no está listo
- Olvidar pedir el cierre

---

*Script generado por IA Hoteles Agent*  
*Actualizado: [Fecha actual]*
"""
        
        (toolkit_dir / "call_script_20min.md").write_text(content, encoding="utf-8")
        
    def _generate_objeciones(self, hotel_data: Dict[str, Any], llm_analysis: Dict[str, Any], toolkit_dir: Path):
        """Genera guía de manejo de objeciones típicas Eje Cafetero"""
        
        perdida_mensual = llm_analysis.get('perdida_mensual_total', 0)
        perdida_6_meses = perdida_mensual * 6
        inversion_mensual = 3_800_000  # Pro AEO
        paquete = llm_analysis.get('paquete_recomendado', 'Pro AEO')
        
        content = f"""# MANEJO DE OBJECIONES TÍPICAS - EJE CAFETERO

## 👤 BUYER PERSONA EJE CAFETERO

**Perfil Demográfico:**
- Edad: 40-65 años
- Rol: Gerente/Dueño, decisor familiar
- Ciclo de decisión: 2-4 semanas
- Presencia digital: Básica a intermedia
- Objeciones reales: "Mi sobrino me hace la web", "Ya tengo quien maneje mis redes", "No entiendo de tecnología"

**Comunicación Efectiva:**
- Audio WhatsApp (45-65 segundos) vs. texto largo
- Números y dinero (lo entienden instantáneamente)
- Comparación con competidores locales (generador de urgencia)
- Garantías verificables (no promesas vagas)
- Videos cortos mostrando resultados reales

---

## 📋 CONTEXTO DEL HOTEL
- **Pérdida mensual actual:** ${perdida_mensual:,.0f} COP
- **Pérdida en 6 meses si no actúa:** ${perdida_6_meses:,.0f} COP
- **Inversión mensual {paquete}:** ${inversion_mensual:,.0f} COP
- **ROI proyectado:** 4-6X en 6 meses

---

## 1️⃣ "No tenemos presupuesto"

**RESPUESTA:**
"Entiendo perfectamente. Déjeme mostrarle algo:

Están perdiendo ${perdida_mensual:,.0f} COP cada mes por invisibilidad en IA.
El paquete {paquete} cuesta ${inversion_mensual:,.0f} COP/mes.

No es un gasto, es **recuperar** lo que ya están perdiendo.

Si esperan 6 meses más: ${perdida_6_meses:,.0f} COP perdidos
Si invierten ahora: Recuperan la inversión en el Mes 1

¿Qué tiene más sentido?"

**ALTERNATIVA (si persiste):**
"Entiendo. ¿Qué tal empezamos con algo más pequeño?

Tenemos el paquete Starter GEO por $1.8M/mes:
- Solo Google Maps (sin IA por ahora)
- Resultados visibles en 30 días
- Puede escalar a Pro AEO cuando esté listo

¿Le hace más sentido este primer paso?"

---

## 2️⃣ "Ya tenemos agencia de marketing"

**RESPUESTA:**
"¡Excelente! Tener equipo de marketing es muy positivo.

Déjeme preguntarle algo:
¿Su agencia ya instaló Schema.org para que ChatGPT los encuentre?"

[Mostrar en pantalla que NO tienen Schema]

"Mire, aquí está el resultado. NO tienen Schema instalado.

Nosotros nos especializamos **solo** en:
1. Visibilidad en IA (ChatGPT, Perplexity, Gemini)
2. Hoteles del Eje Cafetero específicamente

Su agencia puede seguir manejando redes sociales, ads, contenido.
Nosotros nos enfocamos en que las IA los recomienden.

**Podemos trabajar en paralelo con su agencia**, no los reemplazamos."

**SI DICE "mi agencia dice que puede hacerlo":**
"Perfecto. Pregúnteles:
1. ¿Cuántos hoteles del Eje Cafetero tienen en Schema.org?
2. ¿En cuánto tiempo implementan?
3. ¿Garantizan menciones en ChatGPT en 90 días?

Si le dan respuestas concretas, adelante.
Si no, hablemos nosotros."

---

## 3️⃣ "Necesito pensarlo / consultarlo"

**RESPUESTA:**
"Por supuesto, es una decisión importante.

Para ayudarle a pensar más claro, ¿qué información específica necesita?

¿Es sobre:
- [ ] El proceso técnico (cómo funciona)
- [ ] La inversión (si cabe en presupuesto)
- [ ] Los resultados (qué garantizamos)
- [ ] El tiempo (cuánto toma)
- [ ] Otro: _________"

[Abordar la objeción específica]

**LUEGO:**
"Perfecto. Le propongo esto:
- Hoy le envío un video de 3 min con ejemplos de hoteles similares
- Le doy 48 horas para pensarlo sin presión
- Hablamos el [día específico] para resolver dudas finales

¿Le parece bien el [día específico] a las [hora]?"

**SI DICE "lo hablo con mi socio/gerente":**
"Perfecto. ¿Quiere que hagamos una llamada corta de 15 min los tres juntos?
Así resolvemos dudas de ambos al mismo tiempo."

---

## 4️⃣ "¿Por qué no hacerlo nosotros mismos?"

**RESPUESTA:**
"¡Excelente pregunta! Claro que pueden intentar.

Déjeme ser transparente sobre lo que implica:

**TIEMPO:**
- Aprender Schema.org: 20-30 horas
- Implementar correctamente: 10-15 horas
- Optimizar para IA: 15-20 horas
- **Total: 45-65 horas**

**RIESGO:**
- Schema mal implementado es PEOR que no tenerlo
  (Google penaliza y baja su ranking)
- IA no los encontrará si los datos están mal estructurados
- Pierde tiempo en lugar de ganar dinero

**COSTO DE OPORTUNIDAD:**
¿Cuánto vale su tiempo?
- 60 horas × $50,000/hora = $3,000,000 COP
- Casi lo mismo que pagar 1 mes del paquete Pro AEO

**Y nosotros:**
- Ya lo hicimos con 12 hoteles del Eje Cafetero
- Implementamos en 2 semanas (no 2 meses)
- Garantizamos que funcione correctamente

**Pregunta honesta:**
¿Prefiere invertir 60 horas aprendiendo, o 2 horas validando nuestro trabajo?"

---

## 5️⃣ "Los resultados no se ven de inmediato"

**RESPUESTA:**
"Tiene razón, y le agradezco que lo mencione.

Déjeme ser claro sobre los tiempos:

**SEMANA 2:** Schema instalado y validado (tangible, verificable)
**SEMANA 4:** Primeras menciones en ChatGPT (podemos mostrárselo en vivo)
**MES 2:** Google Maps sube posiciones (medible en dashboard)
**MES 3:** Primeras reservas directas atribuibles (ROI real)

**Importante:**
Si esperamos a que los resultados sean "inmediatos", seguirá perdiendo ${perdida_mensual:,.0f} COP cada mes.

La pregunta es:
¿Prefiere empezar hoy y ver resultados en 30-60 días?
¿O esperar 6 meses más y perder ${perdida_6_meses:,.0f} COP?"

---

## 6️⃣ "Déjeme ver cómo nos va estos meses"

**RESPUESTA:**
"Entiendo la prudencia.

Pero déjeme mostrarle algo:

[Mostrar gráfica de pérdida acumulada]

**Si espera 3 meses más:**
- Pierde: ${perdida_mensual * 3:,.0f} COP
- Competencia consolida posiciones en IA
- Será más difícil alcanzarlos

**Si empieza hoy:**
- Mes 1: Recupera inversión
- Mes 2-3: Ya está ganando dinero
- Mes 6: ${perdida_6_meses:,.0f} COP de beneficio neto

**Pregunta:**
¿Qué información específica espera ver en esos meses que no tenga ya?

Si es sobre IA y Google Maps, ese ES el problema.
No van a mejorar solos, solo empeoran."

---

## 7️⃣ "¿Qué garantías tenemos?"

**RESPUESTA:**
"Excelente pregunta. Garantías concretas:

**30 DÍAS:**
- Schema instalado y validado en Google Rich Results
- 15 fotos en Google Maps
- 4 posts publicados
- **Garantía:** Si no está instalado, devolvemos el mes completo

**60 DÍAS:**
- Mínimo 2 menciones en ChatGPT (verificables)
- Posición Google Maps sube mínimo 5 lugares
- **Garantía:** Si no hay mejora medible, mes 3 gratis o ajustamos estrategia

**90 DÍAS:**
- Dashboard activo con métricas en tiempo real
- Mínimo 1 reserva directa atribuible a IA
- **Garantía:** Seguimiento mensual sin costo hasta lograrlo

**ADEMÁS:**
- Sin permanencia (cancela cuando quiera)
- Acceso directo a nosotros por WhatsApp
- Reportes semanales de progreso

¿Qué otra garantía específica necesitaría?"

---

## 🎯 PRINCIPIOS CLAVE

### SIEMPRE:
1. **Escuchar primero** - Entender la objeción real
2. **Empatizar** - "Entiendo perfectamente..."
3. **Mostrar números** - Usar sus datos específicos
4. **Comparar** - Costo vs. pérdida actual
5. **Preguntar** - Cerrar con pregunta, no afirmación

### NUNCA:
1. Discutir o contradecir directamente
2. Usar jerga técnica (Schema, JSON-LD, etc.)
3. Hablar mal de competidores o agencias
4. Prometer resultados exactos
5. Presionar cuando claramente no está listo

---

## 📊 HOJA DE RESPUESTAS RÁPIDAS

| Objeción | Respuesta en 1 frase |
|----------|---------------------|
| "Es caro" | "Están perdiendo ${perdida_mensual:,.0f}/mes, esto cuesta ${inversion_mensual:,.0f}/mes" |
| "No funciona" | "Funcionó con 12 hoteles Eje Cafetero, le muestro casos" |
| "Toma mucho tiempo" | "2 semanas setup, resultados en 30 días" |
| "Ya intentamos antes" | "¿Con visibilidad en IA? Esto es nuevo 2024-2025" |
| "Mi web es mala" | "Instalamos Schema sin tocar diseño, aún funciona" |

---

*Documento generado por IA Hoteles Agent*  
*Personalizado para mercado Eje Cafetero*
"""
        
        (toolkit_dir / "objeciones_frecuentes.md").write_text(content, encoding="utf-8")

