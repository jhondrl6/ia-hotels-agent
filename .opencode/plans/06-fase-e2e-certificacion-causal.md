# FASE-E2E-CAUSAL: Certificación E2E tras consolidación AEO/IAO

**ID**: FASE-E2E-CAUSAL
**Objetivo**: Ejecutar v4complete E2E con Hotel Víesperas (site real: https://www.hotelvisperas.com/es y confirmar que el diagnóstico NO genere scores fantasmas (--), referencias IAO o Voice Readiness.
**Dependencias**: FASE-CAUSAL-01, FASE-CAUSAL-02, FASE-CAUSAL-03, FASE-RELEASE-4.21.0 (TODAS completadas)
**Skill**: iah-cli-phased-execution

---

## Contexto

Tras la eliminación de scores redundantes (IAO, Voice Readiness, el diagnóstico generado por v4complete debe mostrar:
- Scorecard con 4 filas: GEO, GBP, AEO, SEO
- **NO** filas IAO ni Voice
- **NO** scores con "—" (em-dash) como valores hardcodeados
- **NO** referencias a "_calculate_iao_score" o "_calculate_voice_readiness"

**Hallazgo pre-ejecución** (diagnostico 2026-04-04 11:56:20):
- 0 referencias IAO: PASADO
- 0 referencias Voice: PASADO
- Scorecard tiene 4 filas correctas: PASADO
- AEO retorna "—/100" en lugar de número: PENDIENTE investigar

---

## Tareas

### Tarea 1: Ejecutar v4complete con site real

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python3 main.py v4complete --hotel-name "Hotel Visperas" --url "https://www.hotelvisperas.com/es"
```

Nota: Si `python3` no tiene `dotenv` instalado, usar el venv: `venv/Scripts/python.exe` o instalar con `pip3 install python-dotenv` (solo para esta sesión).

### Tarea 2: Validar diagnóstico generado

Verificar el archivo más reciente en `output/v4_complete/01_DIAGNOSTICO_*.md`:

#### Check 1: Scorecard correcto (4 filas)
- [ ] Fila GEO (Google Maps) presente
- [ ] Fila GBP (Perfil Google Business) presente
- [ ] Fila AEO (Infraestructura para IAs) presente con valor numérico XX/100 (NO "—")
- [ ] Fila SEO Local presente
- [ ] NO hay fila IAO
- [ ] NO hay fila Voice Readiness

#### Check 2: Sin referencias eliminadas
- [ ] NO contiene "iao" (case insensitive, excluyendo palabras como "visibilidad en IA")
- [ ] NO contiene "voice readiness"
- [ ] NO contiene "_calculate_iao_score"
- [ ] NO contiene "_calculate_voice_readiness"

#### Check 3: Sin placeholders hardcodeados
- [ ] NO contiene "—" (em-dash U+2014) como valor de score
- [ ] NO contiene "$$" en valores monetarios
- [ ] NO contiene "[[VAR]]" o "{{VAR}}" (placeholders sin reemplazar)

### Tarea 3: Si AEO retorna "—", diagnosticar raíz

**Investigar** el método `_calculate_aeo_score()` en `v4_diagnostic_generator.py` (linea ~1110-1129):

Causas probables:
1. `audit_result.performance.mobile_score` es `None` → el audit no obtuvo datos de PageSpeed
2. `audit_result` mismo es `None`
3. `has_real_data` queda en `False` porque no hay mobile_score >= 50

**Acción correctiva**:
- Si el problema es que el audit no obtiene PageSpeed data, verificar que el scraper/PageSpeed funcione con la URL real
- Si el problema es que `mobile_score` existe pero es < 50, la lógica debería retornar "0/100" en vez de "—"
- Patchear `_calculate_aeo_score()` para que retorne "0/100" en vez de "—" cuando tiene audit real pero no cumple el umbral

### Tarea 4: Ejecutar log_phase_completion.py

```bash
python3 scripts/log_phase_completion.py \
    --fase FASE-E2E-CAUSAL \
    --desc "E2E Certification post-consolidacion AEO/IAO" \
    --archivos-mod "" \
    --archivos-nuevos "" \
    --check-manual-docs
```

Solo si se requirió parchear código (Tarea 3), incluir `--archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py"`.

### Tarea 5: Git commit

```bash
git add -A && git commit -m "FASE-E2E-CAUSAL: Certificacion E2E v4complete post-consolidacion AEO/IAO"
```

---

## Criterios de Aceptación

- [ ] v4complete ejecutado exitosamente con https://www.hotelvisperas.com/es
- [ ] Diagnosticscorecard tiene exactamente 4 filas (GEO, GBP, AEO con valor numérico, NO "—", SEO)
- [ ] 0 referencias a IAO o Voice Readiness
- [ ] 0 placeholders hardcodeados (—, $$, [[VAR]])
- [ ] CHANGELOG.md actualizado si se parcheó código
- [ ] log_phase_completion.py ejecutado
- [ ] Commit realizado

---

## Restricciones

- NO re-introducir código IAO o Voice
- NO cambiar la lógica del scorecard (4 filas es definitivo)
- Si AEO no puede medirse, retornar "0/100" con nota "Pendiente de datos" en vez de "—"
- NO modificar ROADMAP.md
- Un fase por sesión
