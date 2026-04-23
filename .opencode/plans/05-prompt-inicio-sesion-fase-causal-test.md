# FASE-CAUSAL-TEST: Verificación End-to-End

**ID**: FASE-CAUSAL-TEST  
**Objetivo**: Verificar que la corrección funciona regenerando propuesta para Amaziliahotel  
**Dependencias**: FASE-CAUSAL-FIX (código corregido)  
**Duración estimada**: 1-2 horas  
**Skill**: `iah-cli-post-implementation-e2e-verification`

---

## Contexto

### Corrección Aplicada (de FASE-CAUSAL-FIX)
- `PROPOSAL_SERVICE_TO_ASSET` ahora tiene 7 entradas
- La plantilla o generador ahora incluye dinámicamente FAQ y Open Graph

### Qué verificar
1. La propuesta comercial lista 7 servicios (no 5)
2. "Página de FAQ" aparece explícitamente
3. "Meta Tags Sociales" aparece explícitamente
4. Los servicios corresponden a las brechas del diagnóstico

### Base Técnica
- hotel_id: `amaziliahotel`
- URL: `https://amaziliahotel.com/`
- Diagnóstico original: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260421_173618.md`
- Propuesta original: `output/v4_complete/02_PROPUESTA_COMERCIAL_20260421_173621.md`

---

## Tareas

### Tarea 1: Regenerar propuesta comercial
**Objetivo**: Generar nueva propuesta con los servicios correctos

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**Alternativa si no hay API key**:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --skip-iao
```

**Criterios de aceptación**:
- [ ] Nueva propuesta generada en `output/v4_complete/`
- [ ] Timestamp más reciente que el original

---

### Tarea 2: Verificar servicios en AMBAS tablas de la propuesta
**Objetivo**: Confirmar que ahora hay 7 servicios en la tabla principal Y en asset_quality_table

**Archivo**: Buscar el nuevo archivo de propuesta en `output/v4_complete/`

**Verificar tabla principal "Esto es lo que hacemos por usted"** (template markdown):
```
|| Servicio | Qué obtiene ||
||----------|-------------||
|| ✅ Google Maps Optimizado (GEO) | ... ||  ← debe existir
|| ✅ SEO Local (SEO) | ... ||                ← debe existir
|| ✅ Botón de WhatsApp | ... ||              ← debe existir
|| ✅ Datos Estructurados | ... ||            ← debe existir
|| ✅ Informe Mensual | ... ||                ← debe existir
|| ✅ Página de FAQ | ... ||                  ← NUEVO
|| ✅ Meta Tags Sociales (Open Graph) | ... || ← NUEVO
```

**Verificar tabla "Estado de los Entregables"** (`${asset_quality_table}`):
- Debe tener 7 filas
- FAQ y OG deben aparecer con su nivel de preparación

**Criterios de aceptación**:
- [ ] Tabla principal tiene 7 filas (5 originales + FAQ + OG)
- [ ] Tabla de entregables tiene 7 filas
- [ ] "Página de FAQ" visible en ambas
- [ ] "Meta Tags Sociales (Open Graph)" visible en ambas
- [ ] Ambas tablas son consistentes entre sí

---

### Tarea 3: Ejecutar validaciones
**Objetivo**: Verificar que no hay regresiones

**Comandos**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Validaciones rápidas
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Verificación de doctor
./venv/Scripts/python.exe scripts/doctor.py --status
```

**Criterios de aceptación**:
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores críticos

---

### Tarea 4: Verificar coherencia del documento
**Objetivo**: Confirmar que la propuesta es internamente consistente

**Verificar**:
1. Los servicios listados en "Esto es lo que hacemos" corresponden a los entregables en "Estado de los Entregables"
2. La propuesta no contradice el diagnóstico
3. Los timestamps son consistentes

**Criterios de aceptación**:
- [ ] Sin contradicciones internas
- [ ] Documento completo y coherente

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_proposal_alignment.py` | `tests/asset_generation/` | Pasa con 7 servicios |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar:

1. **`dependencias-fases.md`**
   - Marcar FASE-CAUSAL-TEST como ✅ Completada
   - Agregar fecha de ejecución
   - Resultados de verificación

2. **`06-checklist-implementacion.md`**
   - Marcar todas las tareas de TEST como completadas
   - Actualizar estado

3. **Guardar evidencia**:
   - Captura de la nueva propuesta con 7 servicios
   - Output de validaciones

4. **Si todo pasa**: Proceder a FASE-RELEASE-4.34.0
5. **Si falla algo**: Volver a FASE-CAUSAL-FIX con los errores documentados

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] Nueva propuesta generada (timestamp reciente)
- [ ] Tabla principal de servicios tiene 7 filas
- [ ] Tabla de entregables (`asset_quality_table`) tiene 7 filas
- [ ] "Página de FAQ" visible en ambas tablas
- [ ] "Meta Tags Sociales (Open Graph)" visible en ambas tablas
- [ ] Tests de proposal_alignment pasan
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores críticos
- [ ] Documento coherente internamente
- [ ] `dependencias-fases.md` actualizado

---

## Restricciones

- [ No modificar código en esta fase ]
- [ Solo verificar y documentar ]
- [ Si falla algo, documentar y reportar ]

---

## Prompt de Ejecución

```
Actúa como QA engineer. Tu objetivo es verificar que la corrección funciona end-to-end.

CONTEXTO:
- Amaziliahotel fue el caso de prueba original
- La corrección agregó FAQ y Open Graph al mapeo
- Necesitas verificar que aparecen en la propuesta

TAREAS:
1. Regenerar propuesta para Amaziliahotel (v4complete)
2. Abrir la nueva propuesta y contar servicios en tabla
3. Verificar que "Página de FAQ" y "Meta Tags Sociales" están
4. Ejecutar run_all_validations.py --quick
5. Ejecutar doctor.py --status
6. Verificar coherencia del documento

CRITERIOS:
- 7 servicios en la propuesta (no 5)
- FAQ y OG visibles
- Validaciones pasan
- Documento coherente

Si algo falla, documenta exactamente qué y por qué.
```
