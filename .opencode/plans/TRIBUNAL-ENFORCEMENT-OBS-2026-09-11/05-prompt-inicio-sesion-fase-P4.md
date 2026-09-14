# FASE-P4: Corrida de observación con datos reales

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P4
**Objetivo**: Ejecutar la corrida `v4complete` de observación (NO entrega a cliente) con el hotel y los datos fijados por Q4, sobre el pipeline ya corregido por P3-A/P3-B, y producir `evidence/FASE-P4/informe-observacion.md` con los 9 puntos del plan maestro §5. **Es la única fase con comando largo.**
**Dependencias**: FASE-P1 ✅ (Q3/Q4/Q5) + FASE-P3-A/P3-B ✅ (recomendado: el informe mide la fidelidad del acta ya corregida) + precondiciones **T3a** (datos con fuente) y **T3b/Q5** (techo de tier). **Fase opcional por contrato**: ver §Cierre de la fase sin corrida.
**Presupuesto**: 40 iteraciones (R2.1; la corrida consume tiempo de reloj, no iteraciones — ver §Cálculo del presupuesto del executor).
**Complejidad técnica**: MEDIA
**Modo de ejecución**: MIXTO (corrida delegada vía `delegate_task`; análisis en sesión principal)
**Skill**: `phased_project_executor.md` v2.24.0

---

## Contexto

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P1 | ⟨P1 fija: Q3 secuenciación, Q4 hotel+datos+consentimiento, Q5 techo de tier⟩ |
| FASE-P2 | ⟨P1 fija: ejecutada o no aplica⟩ |
| FASE-P3-A / P3-B | ⟨✅ + fecha de cada una⟩ |
| FASE-P4 | ← ESTA FASE |

### Lecciones capitalizadas aplicables a esta fase
(filtras de `00-lecciones-capitalizadas.md` §2)

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-VUP-9 | Los prompts delegados usan argumentos CLI reales, no suposiciones | Tarea 1: `--help` de `onboard` y `v4complete` verificado **antes** de redactar el brief delegado |
| L-VUP-13 | El estado de onboarding se confirma en el log, no en el código | Tarea 1: `ls output/clientes/` + log antes de la corrida; si cae a defaults, la condición de equivalencia se declara |
| L-VUP-12 | Protocolo evidencia-first | Tarea 2: corrida → **copia de evidencia antes de analizar** → script de comparación versionado en `evidence/FASE-P4/` → análisis |
| L-VUP-14 | El diff vs baseline es estructural, no visual | Tarea 2: parseo JSON por claves numeradas contra `evidence/FASE-E2E/`, probado **antes** de la corrida |
| L-B4 (hallazgo §3.b) | Dos planes pueden compartir carpeta de evidencia: `evidence/` es raíz global | Tarea 2: snapshot del baseline ajeno usado, copiado dentro de `evidence/FASE-P4/` con su procedencia |
| L-PF6 / L-PF10 | "Sin hallazgos" ≠ "no midió" | Punto 8 del informe: los tres estados de `reviewer_reports` distinguibles (NR8) |

---

## Tareas (R3: 3 tareas + 1 comando largo)

### Tarea 1: Preparación verificada (sin corrida)
- Confirmar decisión Q4 vigente: hotel, `rooms`/`occupancy_rate`/`direct_channel_percentage`/`ADR` con fuente declarada, URL propia, consentimiento registrado.
- `--help` de `onboard` y `v4complete`; `ls output/clientes/` + log de onboarding; techo de tier esperado según Q5 (A si (a) y T3b cumplido; `B_PLUS` si (b)).

### Tarea 2: Corrida delegada + evidencia (comando largo: `v4complete`)
- `delegate_task` con brief de argumentos verificados; exit 0.
- **Antes de analizar**: copiar toda la evidencia a `evidence/FASE-P4/` (incluido snapshot del baseline ajeno de `evidence/FASE-E2E/` que se use para el delta, con procedencia — L-B4).
- Script de comparación JSON versionado dentro de `evidence/FASE-P4/`; parseo probado contra el baseline antes de interpretar nada.

### Tarea 3: Informe de observación (AC-O2)
- `evidence/FASE-P4/informe-observacion.md` con los 9 puntos del §5 del maestro, incluyendo: punto 8 (estado real de `reviewer_reports` con los tres estados) y punto 9 (banderas efectivas y techo de tier — AC-O0).
- Provisionalidad de `APROBADO-PARA-ENTREGA` registrada si el enforcement no quedó cerrado (Q1≠sí o P2 pendiente).
- Delta vs corrida E2E del predecesor con diff estructural (R2.3).

**Criterios de aceptación**: los de `06-checklist-implementacion.md` §FASE-P4 (T3a recibida, techo de tier por Q5/AC-O0, L-VUP-9/13/12/14 cumplidos, informe de 9 puntos, provisionalidad, no-entrega-a-cliente).

---

## Cierre de la fase sin corrida (escenario declarado — sesión de ajuste 2026-09-14)

Si **T3a no se cierra** (no hay hotel con datos y fuente, ni aparece antes de la sesión): esta fase **no se fuerza ni queda "en espera"** — aplica §Cierre válido sin P4 de `dependencias-fases.md`:
1. Registrar el diferimiento con fecha y causa en `10-analisis-post-implementacion.md` §Decisiones (hereda lo que P1 decidió en Q4/Q5).
2. README pasa a 5 sesiones; la fila P4 del checklist se marca **Diferida**, no `—` vacío.
3. FASE-VERIFY pierde el criterio 2 → no activa; AC-V1 en RELEASE la sustituye.
4. P4 se transfiere al plan de analítica sucesor como fase propia, con el régimen Tier A declarado **no observado** por este plan.

El fallo de **T3b NO cierra este escenario**: con T3a cumplido la corrida se hace en `B_PLUS` con AC-O0.

---

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: P4 ✅ (o Diferida con referencia al escenario de arriba)
2. `README.md`: tabla de progreso
3. `09-documentacion-post-proyecto.md`: acumular (una corrida no genera módulos; registra hallazgos)
4. `10-analisis-post-implementacion.md`: fila + lecciones + métricas
5. `00-lecciones-capitalizadas.md` §2: realidad contra promesa
6. `evidence/FASE-P4/`: informe, evidencia copiada, script, snapshot del baseline
7. `log_phase_completion.py --fase FASE-P4 --desc "..." --check-manual-docs` (SIN `--release`)

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] Informe con los 9 puntos de §5 del maestro (AC-O2) + techo de tier (AC-O0)
- [ ] Evidencia copiada antes de analizar; script de comparación versionado; baseline ajeno snapshotado (L-B4)
- [ ] Iteraciones medidas y escritas (L-R.1 — un `—` no cierra)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] NO se usó como entrega a cliente
- [ ] Post-ejecución completada (7 puntos)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- NO re-decidir Q3/Q4/Q5 (L-VUP-6).
- La corrida es observación: prohibido entregar el ZIP a tercero como producto.
- NO modificar código de producción para "arreglar" lo que observe la corrida: hallazgo → seguimiento con dueño (L-V.4).
- Never-block del pipeline no se desactiva para la corrida.
