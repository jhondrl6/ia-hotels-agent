# Análisis Post-Implementación — CREDIBILIDAD-NUMERICA-2026-08-20

> **Estado**: 3/11 fases completadas (P0-A ✅, P0-B ✅, P0-C ✅) — 8 restantes
> **Plan**: CREDIBILIDAD-NUMERICA-2026-08-20
> **Versión objetivo**: v4.72.0
> **Creado DESDE LA CONCEPCIÓN** (phased_project_executor v2.15.0): cada fase agrega lecciones aquí al cerrar sesión.

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-P0-A | 2026-08-20 | ✅ | ~35 | No | 3 tests nuevos contrato F1; 0 regresiones; 22 fallos línea base intactos |
| FASE-P0-B | 2026-08-21 | ✅ | ~30 | No | 18 tests nuevos pricing_compliance; gate floor-aware D1; AGENTS.md 12→13 gates; 0 regresiones |
| FASE-P0-C | 2026-08-21 | ✅ | ~15 | No (DIRECTO) | 4 tests nuevos encoding; auditoría estática AST; fix en 3 writers (1 delivery_quality_report + 2 config_checker); 0 regresiones |
| FASE-P1-A | — | ⬜ | — | No | |
| FASE-P1-B | — | ⬜ | — | Sí (2 tracks) | |
| FASE-P1-C | — | ⬜ | — | No | |
| FASE-P1-D | — | ⬜ | — | No | Máxima complejidad |
| FASE-P2-A | — | ⬜ | — | No | |
| FASE-P2-B | — | ⬜ | — | No | |
| FASE-E2E-ZIONE | — | ⬜ | — | Sí (v4complete) | |
| FASE-RELEASE-4.72.0 | — | ⬜ | — | Opcional | |

## Matriz de Verificación de Fixes (llenar en FASE-E2E-ZIONE)

Matriz completa en `01-plan-maestro.md §4` (V1-V13). Resumen:

| # | Fix (fallo) | Expected | Real | Status |
|---|-------------|----------|------|--------|
| V1-V2 | F1 pricing único + gate | Un precio; gate PASSED (floor-aware D1) | | |
| V3 | F7 encoding | JSONs legibles utf-8 | | |
| V4-V5 | F2/F4/F3 benchmarks + fallback | Un ADR; fallback conservador | | |
| V6 | F5 comisión OTA | Rango + fuente | | |
| V7 | F6 cap rango hook | Ratio acotado | | |
| V8-V9 | F12/F13 verdad sitio vivo | Sin brechas falsas WhatsApp | | |
| V10 | F14 coherence vs gate | Ambos de acuerdo | | |
| V11 | F8 occupancy label | Etiqueta correcta | | |
| V12 | Regresión gates | Coherence ≥ 0.8; sin fallos NUEVOS vs línea base §6 | | |
| V13 | C9 corrida (caches cálidos) | Tiempo medido | | |

## Lecciones Aprendidas (mínimo 3 por fase completada)

Formato: **qué pasó / por qué / qué lo previene** + pertinencia (INCLUIR/EXCLUIR)

### Lecciones capitalizadas de planes anteriores (aplicadas al DISEÑO de este plan)

| Lección | Aplicación en este plan |
|---------|--------------------------|
| Nunca declarar bug sin leer el archivo completo (CONTEXT §1.3) | Los prompts ordenan INVESTIGAR antes de fijar; líneas citadas del contexto se marcan "verificar en ejecución" |
| Nunca declarar brecha HIGH sin verificación contra sitio vivo (CONTEXT §7.4) | FASE-E2E verifica V8/V9 contra https://zione.co/ |
| Post-implementación desde concepción (executor v2.15.0) | Este archivo creado en Preparación |
| Subagentes no comparten venv Windows (FASE-4 BUGS-ONBOARDING-ADR) | Advertencia venv en P1-B; v4complete delegado solo ejecuta terminal |
| Análisis de causa raíz de FASE-F (occupancy label) | F8 residual limitado a verificación de etiqueta, no re-fix del valor |

### Lecciones nuevas de este plan (llenar por fase)

#### FASE-P0-A

| # | Lección | Pertinencia |
|---|---------|-------------|
| L1 | `_load_pricing_config()` ya existía en `pricing_calculator.py` con caché module-level y fallback. Reutilizarla evita duplicar lógica de carga YAML y garantiza consistencia con el financial engine. | INCLUIR: futuros consumidores de pricing deben importar de pricing_calculator, no reimplementar |
| L2 | Al eliminar constantes de clase y reemplazarlas con método de instancia `_get_pricing_packages()`, los `getattr(self, '_current_*', self.CONSTANTE)` en 15 sitios del proposal generator requerían migración individual. Un grep global (`self.SETUP_FEE\|self.MONTHLY_PACKAGE_PRICE`) confirmó 0 residuales. | INCLUIR: tras refactor de constantes, SIEMPRE verificar con grep que no queden referencias |
| L3 | El test `test_pricing_constants` con valores hardcodeados ("120.000", "400.000") se rompió con el refactor. Reescribirlo para comparar contra `_load_pricing_config()` lo hace resiliente a cambios futuros en pricing.yaml. | INCLUIR: tests de contrato deben comparar contra fuente dinámica, no valores fijos |

#### FASE-P0-B

| # | Lección | Pertinencia |
|---|---------|-------------|
| L4 | El gate `pricing_compliance` necesita datos de pricing (pain_ratio, tier, monthly_price) en el assessment, pero `AssessmentBuilder` no los inyectaba. Agregar `with_pricing()` como método fluid y `pricing_data` como campo en `AssessmentPayload` resuelve el vacío sin tocar los 12 gates existentes. | INCLUIR: al agregar un gate nuevo, verificar SIEMPRE que el assessment builder propague los datos necesarios |
| L5 | La detección de `operational_floor` aplicado se implementa comparando `monthly_price <= operational_floor * 1.01` (tolerancia 1%). Sin tolerancia, precios exactos al floor fallan la detección por redondeo de punto flotante. | INCLUIR: comparaciones de precios con floor SIEMPRE deben incluir tolerancia (1% mínimo) |
| L6 | Los tests existentes (test_all_gates_pass, test_visperas_comprehensive_report) asumen un conteo FIJO de gates (12). Al agregar un gate nuevo, 4 tests se rompieron por assertions `len(results) == 12`. Actualizar a 13 fue trivial pero evitable con assertions dinámicas (`len(orchestrator.gates)`). | INCLUIR: assertions de conteo de gates deben usar `len(orchestrator.gates)` en vez de hardcoded — mejora resiliencia ante futuros gates |

#### FASE-P0-C

| # | Lección | Pertinencia |
|---|---------|-------------|
| L7 | La auditoría de writers sin encoding reveló que de ~60 writers en modules/, solo 3 carecían de encoding='utf-8'. El patrón dominante es que los writers YA estaban corregidos (probablemente por P0-A o convenciones previas). Un test estático con AST (ast.parse + walk) es más robusto que grep para detectar violaciones futuras porque entiende la estructura del código y no genera falsos positivos con comentarios o strings. | INCLUIR: para contratos de código transversales (encoding, imports prohibidos), usar AST en vez de regex/grep |
| L8 | `delivery_quality_report.py` era el writer crítico (F7 original: UnicodeDecodeError byte 0xf3). El fix fue trivial (1 línea) pero el impacto es alto: es el primer archivo que se lee al abrir el ZIP de entrega. Los writers de config_checker.py son archivos temporales de prueba de permisos — el fix es preventivo (evita fallo en sistemas con locale no-UTF-8). | INCLUIR: priorizar fixes de encoding por impacto en el usuario final, no por cantidad de writers |
| L9 | El test de contrato anti-regresión con caracteres Unicode (em-dash “–”, tildes “ó”, “é”) verifica el roundtrip save→load. Sin estos caracteres explícitos en el test, un futuro cambio podría reintroducir write_text sin encoding y el test pasaría porque ASCII no distingue cp1252 de utf-8. | INCLUIR: tests de encoding SIEMPRE deben incluir caracteres no-ASCII (tildes, ñ, em-dash) para ser efectivos |

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Ruta productora del pricing $500K no trazada a fondo (CONTEXT §4.2) | ✅ Cerrado | FASE-P0-A trazó la cadena: pricing.yaml → _load_pricing_config() → _calculate_dynamic_price() → pricing_result.monthly_price_cop |
| Comportamiento de scrapers con prospectos nuevos (CONTEXT §4.3) | Abierto | FASE-P2-B script pre-carga; medir en ejecución operativa |
| P3: deployer real, Express 5 páginas, monitoreo | Fuera de alcance | Solo tras primer Express pagado |

## Métricas de Ejecución (llenar al cierre)

| Métrica | Valor |
|---------|-------|
| Tests totales al cierre | (pendiente — se actualizará en RELEASE) |
| Coherence E2E Zi One | (pendiente) |
| Gates PASSED E2E | (pendiente) |
| Tiempo corrida con caches cálidos (C9) | (pendiente) |

## Decisiones Arquitectónicas (llenar cuando aplique)

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|--------------------------|------|
| D1 | Gate pricing_compliance floor-aware: BLOCKING solo si pain_ratio > pain_ratio_gate_max del tier (0.32 boutique); WARNING fuera de 0.03-0.06 con operational_floor aplicado | Con umbrales globales 0.03-0.06 como blocking, fuga < 6.67M/mes con floor 400K nunca cumple ratio ≤ 0.06 → V12 inalcanzable; precedente PATCH-A en coherence_validator (max_ratio 0.50) | Umbrales globales como blocking | FASE-P0-B |
| D2 | Comisión OTA: campo EXISTENTE `comision_ota` (0.18-0.22) + `source`; 5 sitios hardcodeados eliminados | Campo ya existente dentro de la narrativa 17-25%; consumidores activos (financial_factors.py, main.py L361) | Crear campo nuevo `ota_commission` | FASE-P1-B |
| D3 | Benchmark master: ¿YAML o JSON? (dimensiones: plano vs categoría; destino de plan_maestro_data.json) | Decidir en fase con el mapa T0 de 3 fuentes y 9+ consumidores | — | FASE-P1-A |
| D4 | Rango del hook cableado al benchmark master ANTES del cap | El cap sobre defaults hardcodeados acota un rango fabricado | Cap directo sin cableado | FASE-P1-C |
| D5 | AGENTS.md gate count 12→13 actualizado en P0-B y validado con validate_agents_md.py | `--quick` no valida gate count; drift invisible si se pospone a RELEASE | Posponer actualización a RELEASE | FASE-P0-B |
| D6 | pricing.yaml como fuente única de pricing: constantes `PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE` (hook_pdf) y `MONTHLY_PACKAGE_PRICE/SETUP_FEE` (proposal) eliminadas; ambos módulos consumen de `_load_pricing_config()["packages"]`; +express_price: 120000 agregado a pricing.yaml | Principio "una fuente de verdad por concepto": 3 fuentes Python no sincronizadas generaban riesgo de cifras contradictorias en output del cliente. La solución reutiliza infraestructura existente (pricing_calculator._load_pricing_config con caché) sin crear módulo nuevo | Crear pricing_service.py nuevo (más abstracción); mantener constantes con sync manual (más frágil) | FASE-P0-A ✅ |
| D7 | (pendiente) Cap de plausibilidad: percentil vs ratio fijo | Decidir en fase | | FASE-P1-C |
| D8 | (pendiente) Estado "verificado en producción" como primera clase | Cierra F13/F14 | | FASE-P1-D |

> D1-D6 están pre-resueltas en `01-plan-maestro.md §7`; D7/D8 se deciden en su fase.

## Checklist de Cierre (llenar en FASE-RELEASE-4.72.0)

- [ ] Todos los fixes F1-F14 verificados en matriz V1-V13
- [ ] Corrida única v4complete Zi One Luxury en `evidence/E2E-ZIONE/`
- [ ] Lecciones aprendidas ≥ 3 por fase
- [ ] CHANGELOG + GUIA_TECNICA + VERSION.yaml = 4.72.0
- [ ] run_all_validations.py --quick TOTAL PASS
