# FASE-1A: Implementar Correccion Estado Entregables - Codigo

**ID**: FASE-1A  
**Objetivo**: Cerrar la cadena de llamadas site_presence_report en v4_proposal_generator.py + integrar SitePresenceChecker en main.py + fix tests  
**Dependencias**: Ninguna (primera fase)  
**Duracion estimada**: ~45 min  
**Skill**: iah-cli-phased-execution, iah-cli-entregables-estado-fix  

---

## Contexto

El bloque "Estado de los Entregables" en la propuesta comercial muestra informacion incorrecta:
- WhatsApp: muestra "Incluido en su kit" cuando YA EXISTE en produccion
- Datos Estructurados: muestra "Completo" cuando NO hay schema validado
- FAQ: muestra "Completo" cuando NO hay FAQ schema

**Causa raiz**: SitePresenceChecker se invoca DENTRO del gate de publicacion, PERO su resultado nunca se retroalimenta al V4ProposalGenerator. Hay un "half-done patch" donde los parametros existen en las firmas pero nunca se conectan.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| (ninguna) | - |

### Base Tecnica Disponible

- `modules/commercial_documents/v4_proposal_generator.py` (1418 lineas)
  - `generate()` L169: tiene `site_presence_report: Optional[Any] = None` en firma
  - `_prepare_template_data()` L459: tiene `site_presence_report: Optional[Any] = None` en firma PERO NUNCA lo usa en el cuerpo
  - `_generate_asset_quality_table()`: necesita recibir presence_lookup
  - `_confidence_to_nivel_significado()` L798: tiene `present_in_production` y `presence_verified` en firma
- `main.py` (3137 lineas)
  - L2476: `proposal_gen.generate()` — no pasa site_presence_report
- `tests/asset_generation/test_proposal_alignment.py` (173 lineas)
  - L43: usa `"Boton de WhatsApp"` SIN tilde — KeyError en runtime
  - `proposal_asset_alignment.py` L23: clave real es `"Boton de WhatsApp"` CON tilde
- Tests base: 2248 tests, 0 regresiones
- Evidencia previa: `evidence/fase-1-amazilia-correccion/`

---

## Tareas

### Tarea 1: Cerrar call chain en v4_proposal_generator.py

**Objetivo**: Conectar el parametro `site_presence_report` desde `generate()` hasta `_confidence_to_nivel_significado()`

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`

**Pasos especificos**:

1. **generate() → _prepare_template_data()** (~L212):  
   Actualizar la llamada existente para pasar `site_presence_report=site_presence_report`

2. **_prepare_template_data()**:  
   Actualizar la llamada a `_generate_asset_quality_table()` para pasar `site_presence_report=site_presence_report`

3. **_generate_asset_quality_table()**:  
   Agregar parametro `site_presence_report: Optional[Any] = None`.  
   Construir `presence_lookup` desde `site_presence_report`:
   ```python
   presence_lookup = {}
   if site_presence_report and hasattr(site_presence_report, 'results'):
       for asset_type, result in site_presence_report.results.items():
           presence_lookup[asset_type] = {
               'present_in_production': result.status.value == "exists",
               'presence_verified': True,
           }
   ```
   Pasar `presence_lookup` a las llamadas de `_confidence_to_nivel_significado()`.

4. **_confidence_to_nivel_significado()**:  
   Ya tiene los parametros `present_in_production` y `presence_verified`. Verificar que la logica L815 funcione:
   - Si `presence_verified and present_in_production` → "Verificado en sitio"
   - Si confidence >= 0.85 sin presencia → "Completo" (ahora "Listo para implementar" para assets no verificados)
   - Si confidence < 0.85 → segun nivel existente

**Criterios de aceptacion**:
- [ ] `generate()` pasa `site_presence_report` a `_prepare_template_data()`
- [ ] `_prepare_template_data()` pasa `site_presence_report` a `_generate_asset_quality_table()`
- [ ] `_generate_asset_quality_table()` construye `presence_lookup` y lo pasa a `_confidence_to_nivel_significado()`
- [ ] `_confidence_to_nivel_significado()` retorna "Verificado en sitio" cuando presence_verified=True y present_in_production=True
- [ ] No hay parametros aceptados-pero-no-usados (half-done patch eliminado)

### Tarea 2: Integrar SitePresenceChecker en main.py

**Objetivo**: Invocar SitePresenceChecker antes de generar la propuesta y pasar el reporte al generador

**Archivos afectados**:
- `main.py`

**Pasos especificos**:

1. Localizar la seccion de generacion de propuesta (~L2449-2488)
2. Antes de `proposal_gen.generate()` (L2476), agregar:
   ```python
   from modules.asset_generation.site_presence_checker import SitePresenceChecker
   from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET

   # Solo verificar assets que fueron generados
   generated_types = {a.asset_type for a in asset_result.generated_assets} if asset_result else set()
   asset_types_to_check = [at for at in PROPOSAL_SERVICE_TO_ASSET.values() if at in generated_types]

   site_presence_report = None
   if asset_types_to_check:
       checker = SitePresenceChecker()
       site_presence_report = checker.check_site(args.url, asset_types=asset_types_to_check)
   ```
3. Agregar `site_presence_report=site_presence_report` a la llamada `proposal_gen.generate()`

**Criterios de aceptacion**:
- [ ] SitePresenceChecker se invoca solo cuando hay assets generados
- [ ] Solo se verifican assets que estan en PROPOSAL_SERVICE_TO_ASSET y fueron generados
- [ ] El reporte se pasa a `proposal_gen.generate()`
- [ ] Si no hay assets que verificar, site_presence_report=None (backward compatible)

### Tarea 3: Fix test_proposal_alignment.py + nuevos tests

**Objetivo**: Corregir bug de tilde y agregar cobertura para la nueva funcionalidad

**Archivos afectados**:
- `tests/asset_generation/test_proposal_alignment.py`

**Pasos especificos**:

1. **Fix tilde** (L43): Cambiar `"Boton de WhatsApp"` → `"Botón de WhatsApp"` (con tilde)
2. Revisar L163 para el mismo bug
3. **Test nuevo**: `_confidence_to_nivel_significado` con `present_in_production=True` → verifica retorno "Verificado en sitio"
4. **Test nuevo**: `_confidence_to_nivel_significado` con confidence 0.85 sin presencia → verifica retorno apropiado (no "Completo" para assets no verificados)

**Criterios de aceptacion**:
- [ ] Linea 43 usa `"Botón de WhatsApp"` con tilde
- [ ] Test 1: presencia verificada → "Verificado en sitio"
- [ ] Test 2: sin presencia + confidence alta → no afirma "Completo" falsamente
- [ ] Todos los tests existentes siguen pasando (0 regresiones)

### Tarea 4: Verificacion

**Objetivo**: Confirmar que todo funciona sin regresiones

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

**Criterios de aceptacion**:
- [ ] test_proposal_alignment.py: todos los tests pasan
- [ ] tests/commercial_documents/: 0 regresiones
- [ ] run_all_validations.py: 4/4 checks

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-1A como ✅ Completada con fecha
2. **`README.md`**: Actualizar tabla de progreso
3. **`09-documentacion-post-proyecto.md`**: Seccion D (metricas) actualizada
4. **`evidence/fase-1a/`**: Guardar diff de cambios si aplica

---

## Criterios de Completitud (CHECKLIST)

- [ ] call chain cerrado: generate() → _prepare_template_data() → _generate_asset_quality_table() → _confidence_to_nivel_significado()
- [ ] main.py invoca SitePresenceChecker antes de generar propuesta
- [ ] Fix tilde en test_proposal_alignment.py
- [ ] 2 tests nuevos pasando
- [ ] 2248+ tests existentes sin regresiones
- [ ] run_all_validations.py --quick: 4/4
- [ ] dependencias-fases.md actualizado

---

## Restricciones

- **Maximo 60 iteraciones** del agente
- **NO ejecutar v4complete** en esta fase (es FASE-1B)
- **NO modificar archivos de documentacion** (CHANGELOG, GUIA_TECNICA) — eso es FASE-1C
- **NO modificar proposal_asset_alignment.py** ni site_presence_checker.py — solo leer de ellos
- Mantener backward compatibility: si site_presence_report=None, comportamiento = igual que antes
