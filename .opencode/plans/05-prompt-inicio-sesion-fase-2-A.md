# Prompt de Inicio de Sesion: FASE-2-A

> **Fase**: 2-A — Deteccion y Enriquecimiento  
> **Plan maestro**: `PLAN-REFACTOR-TERMALES-20260508.md`  
> **Iteraciones max**: 60  
> **Contexto previo**: FASE-PRE + FASE-1-A + FASE-1-B completadas  
> **Fixes**: FIX-5, FIX-6, FIX-7  

---

## Tareas de la Fase

TAREAS DE LA FASE:
  [ ] Investigacion de codigo existente (publication_gates.py, site_presence_checker.py, indirect_traffic_generator.py, faq_generator.py)
  [ ] Implementar FIX-5: SitePresenceChecker hardening
  [ ] Implementar FIX-6: indirect_traffic lee audit_context
  [ ] Implementar FIX-7: FAQ extrae datos del sitio
  [ ] Verificar con tests unitarios
  [ ] Documentacion post-fase

CONTADOR:
  - Total tareas: 5
  - Comandos largos: 0
  - Estado: dentro del limite R3 (max 4 tareas sin comandos largos; 5 es marginal pero aceptable si investigacion es rapida)
  > **NOTA**: Si la investigacion consume >5 iteraciones, priorizar FIX-5 y FIX-6; dejar FIX-7 para sesion de recuperacion.

---

## Contexto de Fases Anteriores

- FASE-PRE: Saneamiento completado
- FASE-1-A: Template engine + Coherence validator corregidos
- FASE-1-B: Content Scrubber Rule 6 + monthly_report data-driven corregidos

---

## Instrucciones Detalladas

### FIX-5: SitePresenceChecker Hardening

**Archivos**:
- `modules/quality_gates/publication_gates.py` (~L816-821)
- `modules/asset_generation/site_presence_checker.py`

**Problema**: `except Exception` traga errores del `SitePresenceChecker` y el gate asume "no existe".  
**Solucion**: Hardening en publication_gates.py + investigacion/correccion en site_presence_checker.py.

**Implementacion en publication_gates.py**:
```python
# Reemplazar:
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"SitePresenceChecker error: {e}")
    site_presence_report = None

# Por:
except Exception as e:
    import logging, traceback
    logger = logging.getLogger(__name__)
    logger.error(f"SitePresenceChecker error: {e}\n{traceback.format_exc()}")
    site_presence_report = {
        'presence_status': 'unknown',
        'error': str(e),
        'assets_checked': {}
    }
```

**Luego, en el gate**: Si `presence_status == 'unknown'`, el gate NO debe marcar el asset como "missing". Debe marcarlo como "indeterminate" o saltarse la verificacion.

**Investigacion en site_presence_checker.py**:
- Revisar por que falla en Termales (posibles causas: bloqueo de WordPress, timeout, selectors CSS desactualizados, SSL).
- Agregar retry con backoff, manejo de timeouts, y logging detallado.

**Validacion**:
- Test: Simular excepcion en SitePresenceChecker → gate retorna `presence_status: 'unknown'`, no marca como missing.
- Test: SitePresenceChecker con sitio que tiene WhatsApp → detecta correctamente.

### FIX-6: indirect_traffic lee audit_context

**Archivo**: `modules/asset_generation/indirect_traffic_generator.py`  
**Problema**: Recomienda acciones genericas sin consultar datos reales del hotel.  
**Solucion**: Leer `audit_report.json` antes de generar recomendaciones.

**Implementacion sugerida**:
```python
def generate(self, hotel_data, audit_report_path=None):
    """Genera recomendaciones basadas en datos reales del audit."""
    audit_data = {}
    if audit_report_path and os.path.exists(audit_report_path):
        with open(audit_report_path, 'r', encoding='utf-8') as f:
            audit_data = json.load(f)
    
    gbp_reviews = audit_data.get('google_business_profile', {}).get('review_count', 0)
    
    recommendations = []
    if gbp_reviews > 1000:
        recommendations.append("✅ Perfil GBP ya establecido. Enfocarse en respuesta a resenas.")
    else:
        recommendations.append("🔄 Reclama y optimiza tu perfil GBP.")
    
    # ... resto de logica
    return recommendations
```

**Validacion**:
- Test: `audit_report` con GBP >1000 reseñas → NO sugiere "reclama tu GBP"
- Test: `audit_report` con GBP <50 reseñas → SI sugiere "reclama tu GBP"

### FIX-7: FAQ extrae datos del sitio

**Archivo**: `modules/asset_generation/faq_generator.py`  
**Problema**: FAQ generica, sin referencia a termas, spa, cascadas.  
**Solucion**: Scraping previo del sitio para extraer servicios reales.

**Implementacion sugerida**:
```python
def _extract_services_from_site(self, url):
    """Hace scraping ligero del sitio para extraer servicios mencionados."""
    import requests
    from bs4 import BeautifulSoup
    
    try:
        resp = requests.get(url, timeout=15, headers={'User-Agent': 'iah-cli-bot/1.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extraer texto de secciones de servicios
        text = soup.get_text(separator=' ', strip=True).lower()
        
        keywords = ['termas', 'spa', 'cascadas', 'masaje', 'avistamiento', 'aves', 'senderismo', 'restaurante']
        found = [kw for kw in keywords if kw in text]
        return found
    except Exception as e:
        return []  # Fallback: FAQ generica

def generate(self, hotel_data, site_url=None):
    services = self._extract_services_from_site(site_url) if site_url else []
    
    faqs = []
    if 'termas' in services or 'spa' in services:
        faqs.append({
            'question': f'¿Cuales son los horarios de las termas en {hotel_data.get("name", "el hotel")}?',
            'answer': 'Consulte disponibilidad...'
        })
    # ... mas FAQs basadas en servicios detectados
    
    return faqs
```

**Validacion**:
- Test: URL de Termales → FAQ incluye preguntas sobre termas, spa, cascadas
- Test: URL generica sin servicios → FAQ generica (fallback)

---

## Post-Ejecucion (al finalizar la sesion)

1. **Marcar checklist** en `.opencode/plans/06-checklist-implementacion.md`:
   - FASE-2-A: estado y tareas completadas

2. **Ejecutar log_phase_completion.py**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2-A \
    --desc "FIX-5 SitePresenceChecker hardening + FIX-6 indirect_traffic audit_context + FIX-7 FAQ site scraping" \
    --archivos-nuevos "tests/asset_generation/test_site_presence_hardening.py,tests/asset_generation/test_indirect_traffic_context.py,tests/asset_generation/test_faq_site_extraction.py" \
    --archivos-mod "modules/quality_gates/publication_gates.py,modules/asset_generation/site_presence_checker.py,modules/asset_generation/indirect_traffic_generator.py,modules/asset_generation/faq_generator.py" \
    --tests "N" \
    --check-manual-docs
```

3. **Actualizar 09-documentacion-post-proyecto.md**:

```markdown
## Seccion B: Funcionalidades Nuevas
| Feature | Modulo | Descripcion | Fase |
|---------|--------|-------------|------|
| SitePresence hardening | publication_gates | Log completo + status unknown en vez de None | FASE-2-A |
| Audit-aware traffic | indirect_traffic_generator | Lee audit_report.json para recomendaciones contextualizadas | FASE-2-A |
| Site-aware FAQ | faq_generator | Scraping previo del sitio para FAQs especificas | FASE-2-A |
```

4. **Guardar evidencia**:
```bash
cp modules/quality_gates/publication_gates.py evidence/fase-2-A/
cp modules/asset_generation/site_presence_checker.py evidence/fase-2-A/
cp modules/asset_generation/indirect_traffic_generator.py evidence/fase-2-A/
cp modules/asset_generation/faq_generator.py evidence/fase-2-A/
```

---

## Criterios de Completitud

- [x] FIX-5 implementado: `except` loguea traceback, retorna `presence_status: 'unknown'`
- [x] FIX-5 testeado: gate no marca como missing cuando presence es unknown
- [x] FIX-6 implementado: `indirect_traffic_optimization_gen` lee `audit_report.json`
- [x] FIX-6 testeado: recomendaciones cambian segun datos del audit
- [x] FIX-7 implementado: `faq_gen` hace scraping previo
- [x] FIX-7 testeado: FAQ incluye servicios reales del sitio
- [x] `run_all_validations.py --quick` pasa (5/5)
- [x] `log_phase_completion.py` ejecutado
- [x] Checklist maestro actualizado

> **Estado**: 🟢 COMPLETADA — 2026-05-08 20:11
> **Iteraciones usadas**: ~35
> **Nota**: Paths reales difieren del plan original: indirect_traffic_generator.py → indirect_traffic_optimization_gen.py, faq_generator.py → faq_gen.py. Ambos en modules/delivery/generators/, no en modules/asset_generation/. Los fixes se adaptaron a los archivos reales.

---

## Restricciones

- **NO ejecutar v4complete** — reservado para FASE-2-B.
- **Max 60 iteraciones**.
- **NO modificar proposal_asset_alignment gate** — reservado para FASE-3.
- Si se agota iteraciones, priorizar FIX-5 (critico para deteccion) y dejar FIX-6/FIX-7 para recuperacion.

---

*Prompt generado por orquestador siguiendo phased_project_executor.md v2.10.0*
