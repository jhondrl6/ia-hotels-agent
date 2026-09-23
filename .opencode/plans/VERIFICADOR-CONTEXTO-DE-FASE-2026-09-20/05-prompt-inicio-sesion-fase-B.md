# FASE-B — Costura de proveedor de decisiones, neutra y extensible

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-B
**Objetivo**: escribir `scripts/decision_client.py`, la única puerta del repo a un proveedor de
decisiones estructuradas, con contract test de forma y con **la extensión a un segundo proveedor
probada**. Cubre AC6–AC9.
**Dependencias**: FASE-A ✅ (reutiliza sus tres estados y su convención de `coverage_basis`).
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración (R3).
**Skill**: `phased_project_executor`.

## Contexto

**Ningún proveedor de pago se activa en este plan.** El acceso existe y está habilitado desde
2026-09-20; el operador decidió posponerlo. Eso no vuelve innecesaria esta fase: la vuelve más barata
y más segura. Lo que se construye aquí es la **costura**, y lo que se certifica es que añadir el
proveedor pospuesto cuesta **un archivo** (AC9). Su activación real es la deuda **D7**, y el primer
consumidor natural es la deuda **D6**, el lint de contradicciones semánticas.

La razón de aislar el proveedor no es estética: el SDK del proveedor rompió compatibilidad dos veces en
sus primeros nueve días público (redefinió los criterios de una primitiva; migró de serializador). Si
el repo se acopla al nombre del proveedor, cada subida rompe fases.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| FASE-A | ✅ — reutilizar `status` de tres estados y `coverage_basis`; no reinventarlos |

### Base técnica disponible

- La costura resuelve el proveedor por variable de entorno. Los dos candidatos que pueden quedar
  detrás, cuando se active D7, son el SDK oficial del proveedor y el **adapter** que el propio
  proveedor publica como reemplazo respaldado por APIs de LLM — el adapter existe precisamente para
  comparar proveedor contra proveedor en costo, velocidad e inteligencia.
- Forma esperada de una respuesta: elección con probabilidades y confianza; nivel ordenado con
  leyenda; binario con probabilidad de sí. La confianza es lo que permite separar «actué» de «no estoy
  seguro», y es el eje que FASE-C usa en AC12.
- Límites que condicionan el diseño y que hay que dejar escritos en el módulo: solo acepta texto; su
  techo de contexto por solicitud es **menor** que la suma de los documentos de gobierno de este repo
  (de ahí que FASE-C chunkee, y que el lint de conteos de FASE-A sea determinista y no pase por aquí);
  y sus modos de fallo documentados son lectura literal, conteo y comparación de fechas.
- Credencial: solo por variable de entorno. **Nunca** se imprime, se pega en el chat ni se escribe en
  evidencia — una clave que aparece en un transcript obliga a rotarla. La evidencia registra
  `provider_status`, jamás el valor. En esta fase no hay credencial en absoluto.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-V2.3 | Renumerar sin medir quién afirma el conteo deja contrato huérfano | Tarea 2 / **AC8**: el contract test afirma la **forma**, no los literales del proveedor ni de su versión |
| L-PF6 | Lector roto leído como ausencia | Tarea 1 / **AC7**: proveedor no configurado **no** puede producir una decisión por defecto |
| L-PF10 | Vacío ≠ ausente | Tarea 1 / **AC7**: `RESUELTO` / `NO-CONFIGURADO` / `ILEGIBLE`, tres estados, tres tests |
| L-D3 | Baseline absoluto hace que cumplir cuente como violación | **AC6**: el escaneo de imports se publica con su población, no como «0 coincidencias» a secas |
| L-R.3 | Un `[OK]` sin denominador no informa | **AC6/AC9**: todo conteo lleva la población que lo sostiene |
| L-R.4 | Regla sin verificador es publicable solo si lo declara | **AC9 y D7**: la comparación de proveedores se declara **fuera de alcance**, no se omite |
| L-VUP-5 | Una fase que no produce ni un rojo es un falso verde potencial | Criterios de completitud: el verde sin rojo previo se reporta sospechoso |

## Tareas

### Tarea 1: La costura y sus tres estados

**Objetivo**: `decision_client.py` con contrato propio (`evaluar(state, preguntas) → respuestas
tipadas`), resolución de proveedor por entorno, y fallo explícito cuando no hay proveedor o la
respuesta es ilegible.

**Archivos afectados**: `scripts/decision_client.py` (nuevo),
`tests/quality_gates/decision_client/` (nuevo).

**Criterios de aceptación**: **AC6** (ningún archivo fuera del script importa SDK o adapter alguno;
artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` con conteo **y** población escaneada) y **AC7** (clave
`provider_status`, tres tests nombrados por su causa; prohibido el `except` que devuelve un valor que
pueda leerse como decisión). Sin proveedor configurado, `evaluar()` **falla**; no devuelve una
heurística.

### Tarea 2: Contract test de forma

**Objetivo**: fijar la forma de la respuesta para que una subida de SDK rompa **este** test y no a una
fase de otro plan.

**Criterios de aceptación**: **AC8** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt` con el nombre del test
y su salida; versión de modelo pineada y declarada; se prueba que **alterar la forma del proveedor
falso lo pone rojo**. Prohibido pinear el número de checks ni literales del proveedor (L-V2.3).

### Tarea 3: Extensibilidad probada, no prometida

**Objetivo**: registrar un **segundo proveedor falso** a través de la costura y demostrar cuánto cuesta.
No se conecta ningún servicio real.

**Criterios de aceptación**: **AC9** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` con la clave
`files_changed_to_add_provider` (valor esperado `1`; si es mayor, se explica cuál y por qué) y
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt` con la salida del test que añade el segundo proveedor sin tocar
ningún otro módulo. **No hay comparación de proveedores en este plan**: con uno solo no hay elección
que medir, y exigirla produciría un `NO-EJERCITADO` que certifica humo. La comparación es deuda D7.

## Tests obligatorios

| Test | Criterio de éxito |
|------|-------------------|
| `test_decision_client_provider_no_configurado.py` | `NO-CONFIGURADO`, sin decisión por defecto |
| `test_decision_client_respuesta_ilegible.py` | `ILEGIBLE` con el motivo; nunca un favorable |
| `test_decision_client_contract_forma.py` | La forma fijada; alterarla rompe el test (**rojo**) |
| `test_decision_client_aislamiento_imports.py` | AC6 sobre el árbol real, con población |
| `test_decision_client_segundo_proveedor_un_archivo.py` | AC9; `files_changed_to_add_provider == 1` |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/decision_client -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-B ✅ con fecha y notas.
2. `README.md` — progreso y estado real de AC6–AC9.
3. `06-checklist-implementacion.md` — casillas correspondientes.
4. `09-documentacion-post-proyecto.md` — Secciones A, B, D, E.
5. `10-analisis-post-implementacion.md` — fila de la fase, lecciones nuevas con pertinencia, métricas
   reales, seguimientos y decisiones: **qué se pospuso (D7) y qué coste tiene posponerlo**.
6. `00-lecciones-capitalizadas.md` — «Qué cambia» con lo que realmente pasó; §4 al estado del cierre.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B \
  --desc "decision_client.py: costura neutra, contract test de forma y extensibilidad a un segundo proveedor probada (AC6-AC9)" \
  --archivos-mod "scripts/decision_client.py,tests/quality_gates/decision_client" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

## Criterios de completitud

- [ ] Los cinco tests pasan; ninguno cubre dos estados.
- [ ] `contract.txt` demuestra el rojo al alterar la forma y el verde con la forma actual (AC8).
- [ ] `costura.json` reporta `files_changed_to_add_provider`, con su valor o su explicación (AC9).
- [ ] Cero llamadas de red en toda la fase: verificable, no afirmado.
- [ ] Ninguna evidencia ni log contiene credencial alguna, ni parcial ni enmascarada.
- [ ] `--quick` verde sin haber tocado su composición (AC16).
- [ ] Post-ejecución completa, incluido el índice regenerado en el mismo commit.

## Restricciones

- **No se activa ningún proveedor real ni se hace una sola llamada de red.** Lo certificado aquí es la
  forma y el aislamiento.
- No importar el SDK ni el adapter en ningún otro archivo (es AC6, no estilo).
- No modificar `.agents/**`, `run_all_validations.py`, el hook, `build_lesson_index.py` ni
  `validate_governance_numbers.py` (es de FASE-A: consúmalo, no lo reescriba).
- No enviar a ningún proveedor contenido del plan `REFACTOR-WHATSAPP` ni material del cliente.
- No ejecutar la pipeline. No commitear ni empujar sin instrucción literal.
- Presupuesto con instrumento y corte declarados (R2.1); nunca estimado.

## Prompt de ejecución

```text
Ejecuta unicamente FASE-B del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-B.md, 01-plan-maestro.md §2 (las filas del proveedor y D7) y §4
(AC6-AC9, AC16, AC17), 04-contrato-ejecucion.md (permisos y la regla de cero red),
00-lecciones-capitalizadas.md §2, dependencias-fases.md y el workflow canónico.
Heredas de FASE-A los tres estados y la convencion coverage_basis: reutilizalos.
Escribe scripts/decision_client.py como unica puerta del repo a un proveedor de decisiones: contrato
propio, proveedor resuelto por variable de entorno, fallo explicito cuando no hay proveedor o la
respuesta es ilegible, y nunca una decision por defecto.
Cero llamadas de red: por decision del operador no entra Jev en este plan. AC6: ningun otro archivo
importa el SDK ni el adapter, con el conteo y su poblacion. AC8: contract test que se pone ROJO si
altera la forma del proveedor falso, sin pinear literales del proveedor. AC9: registra un segundo
proveedor falso a traves de la costura y publica files_changed_to_add_provider; si es mayor que 1, lo
explicas. La comparacion de proveedores NO es de este plan: es la deuda D7.
La credencial no se imprime, no se pega ni entra en evidencia: se registra provider_status.
No toques .agents/, run_all_validations.py, el hook, validate_governance_numbers.py ni ningun plan
vivo. Registra la fase con log_phase_completion.py y regenera el indice en el mismo commit. Deja
checkpoint si falta autorizacion.
```

---

## Nota de cierre de esta fase (2026-09-23) — no reconstruye las instrucciones de arriba

**Esta fase ya se ejecutó: FASE-B cerró VERIFICADO OFFLINE el 2026-09-21 y se commiteó el 2026-09-22
en `647f436`. Este prompt queda como histórico de esa sesión y no debe volver a ejecutarse.** Tres
rectificaciones que el texto de arriba no contenía cuando se escribió, y que la fase produjo al
commitearse:

- **S11 y S12** nacieron del propio commit de la fase y fueron corregidas **fuera de este plan** por el
  bloque A de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` (`fdd397f`); su **aceptación** por el plan
  propietario está en `dependencias-fases.md` §Conciliación. La guarda que esta fase publicó en el
  README sobre `validate_governance_numbers.py --report` sin destino **ya no aplica**.
- **AC9 se declaró con alcance local**: certifica añadir un proveedor **falso** del repo
  (`files_changed_to_add_provider = 1`, medido por sha256, sin red ni credenciales), **no** el coste de
  integrar un SDK real con sus dependencias y su autenticación. Su texto original («añadir el segundo
  cuesta un archivo») se leía como lo segundo.
- La instrucción de arriba sobre **`log_phase_completion.py` ya está cumplida y no se repite**: la fase
  tiene su entrada en `REGISTRY.md`. Volver a registrarla duplicaría la entrada, y ningún cierre de
  esta fase mueve `VERSION.yaml` (el bump pertenece a RELEASE).

Dónde quedó cerrado y qué quedó abierto (S10, D6, D7): `10-analisis-post-implementacion.md` y
`06-checklist-implementacion.md`.
