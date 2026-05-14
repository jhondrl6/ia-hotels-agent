     1|# Contexto — Incidente: Bloqueo del Sistema por Memory Leak en Python
     2|
     3|> **Fecha:** 2026-05-13 22:12–22:16
     4|> **Repo:** `/mnt/c/Users/Jhond/Github/iah-cli`
     5|> **Origen:** Análisis forense de registros de Windows (Event Viewer) + logs de Hermes
     6|> **Propósito:** contexto completo para que una sesión nueva pueda diagnosticar, prevenir y corregir la causa raíz sin redescubrir nada.
     7|
     8|---
     9|
    10|## 1. Diagnóstico raíz
    11|
    12|### 1.1 Resumen del incidente
    13|
    14|A las 22:16 del 13/05/2026 el sistema Windows quedó completamente congelado (sin respuesta a comandos ni aplicaciones). El usuario forzó el apagado manual (Kernel-Power ID 41). No fue un BSOD.
    15|
    16|### 1.2 Causa directa
    17|
    18|**python.exe (PID 32376) consumió 42.5 GB de memoria virtual**, detectado por Resource-Exhaustion-Detector (ID 2004) a las 22:12:24.
    19|
    20|El Desktop Window Manager (dwm.exe) no pudo asignar buffers de video y crasheó 4 veces consecutivas (22:12:44, 22:13:27, 22:14:24, 22:15:03), dejando el sistema sin interfaz gráfica.
    21|
    22|### 1.3 Script culpable
    23|
    24|**`scripts/validate_document_integration.py`** (464 líneas) — validador de integración documental del proyecto iah-cli.
    25|
    26|Ejecutado por Hermes (sesión `20260513_215353_d7058e`) a través de comandos `terminal` que lanzaban Python 3.13 de Windows (`C:\Users\Jhond\AppData\Local\Programs\Python\Python313\`).
    27|
    28|---
    29|
    30|## 2. Cronología de eventos
    31|
    32|| Hora | Evento | Detalle |
    33||------|--------|---------|
    34|| 22:02:24 | 1er fallo script | `UnicodeEncodeError`: carácter `↔` no codificable en cp1252 |
    35|| 22:03:12 | 2ª ejecución | DOCUMENT INTEGRATION VALIDATOR — error de salida |
    36|| 22:03:41 | 3er fallo | `Exception in thread Thread-3 (_readerthread)` |
    37|| 22:03:48 | 4ª ejecución | Reporta "DOMAIN_PRIMER vs VERSION.yaml: mismatch" |
    38|| 22:05:25 | 5º fallo | Otra vez `_readerthread` exception |
    39|| 22:12:24 | **ALARMA** | **Resource-Exhaustion: python.exe = 42.5 GB virtual** |
    40|| 22:12:44 | DWM crash #1 | dwmcore.dll excepción 0xc00001ad |
    41|| 22:13:27 | DWM crash #2 | Reinicio automático fallido |
    42|| 22:14:24 | DWM crash #3 | GPU: AMD Radeon (TM) Graphics |
    43|| 22:14:36 | DWM crash #4 | (registrado en Application log como ID 1000) |
    44|| 22:15:03 | DWM no recupera | Sistema inusable — ventanas existen pero no se dibujan |
    45|| 22:16:41 | **Apagado forzado** | Usuario fuerza power off (Kernel-Power ID 41) |
    46|
    47|### 2.1 Uso de memoria en el momento del colapso
    48|
    49|| Proceso | PID | Memoria virtual |
    50||---------|-----|-----------------|
    51|| python.exe | 32376 | **42.5 GB** |
    52|| ollama.exe | 23232 | 1.5 GB |
    53|| vmmemWSL | 12120 | 1.5 GB |
    54|| **Total** | | **~45.5 GB** |
    55|
    56|RAM física del equipo: **15.4 GB** → swapping masivo (thrashing).
    57|
    58|---
    59|
    60|## 3. Causa técnica detallada
    61|
    62|### 3.1 Mecanismo del memory leak
    63|
    64|Tres factores que se combinaron:
    65|
    66|1. **Encoding cp1252 vs UTF-8**: Python en Windows usa cp1252 por defecto en stdout. El script imprime caracteres Unicode (↔, tildes, em-dash —). Cada `UnicodeEncodeError` genera excepciones que quedan atrapadas en buffers de pipe entre Hermes y el proceso Python.
    67|
    68|2. **Ejecuciones repetidas sin limpieza**: Hermes ejecutó el script al menos 5 veces en ~3 minutos. Los procesos que fallaban con `_readerthread` (pipe roto) no se cerraban limpiamente, acumulando instancias zombie con buffers crecientes.
    69|
    70|3. **Ciclo de excepciones**: cuando Python no puede imprimir en cp1252 y el pipe está roto, la excepción de encoding + la excepción de pipe roto generan un ciclo que infla los buffers internos sin liberar memoria.
    71|
    72|### 3.2 El script validate_document_integration.py
    73|
    74|- **Ubicación**: `/mnt/c/Users/Jhond/Github/iah-cli/scripts/validate_document_integration.py`
    75|- **Función**: valida consistencia cross-document (cross-references, CHANGELOG, versiones, DOMAIN_PRIMER, etc.)
    76|- **Problema**: no fuerza UTF-8 en stdout. Usa `print()` con caracteres Unicode directamente.
    77|- **Historial**: ya falló antes (sesión 20260508) con el mismo `UnicodeEncodeError` en el carácter `↔`. Se parchó parcialmente pero el problema persiste.
    78|
    79|### 3.3 Por qué DWM crasheó
    80|
    81|DWM necesita memoria de video (la GPU AMD Radeon integrada comparte RAM del sistema). Con 45.5 GB de memoria comprometida y solo 15.4 GB físicos, el sistema estaba en thrashing extremo. DWM no pudo asignar buffers → `0xc00001ad` → crash. Sin DWM no se dibuja la interfaz gráfica.
    82|
    83|---
    84|
    85|## 4. Evidencia en logs
    86|
    87|| Fuente | Evento ID | Hora | Descripción |
    88||--------|-----------|------|-------------|
    89|| System | 2004 | 22:12:24 | Resource-Exhaustion: python.exe 42.5 GB |
    90|| System | 41 | 22:16:41 | Kernel-Power: reinicio inesperado |
    91|| System | 6008 | 22:16:47 | EventLog: cierre anterior inesperado |
    92|| System | 1801/1795/1040 | 22:16-22:21 | TPM-WMI errores (consecuencia) |
    93|| Application | 1000 | 22:12:44 | dwm.exe crash #1 |
    94|| Application | 1000 | 22:14:36 | dwm.exe crash #4 |
    95|| Application | Dwminit | 22:13-22:15 | DWM cerró 4 veces (AMD Radeon) |
    96|| Hermes log | session 20260513_215353 | 22:02-22:05 | 5 ejecuciones fallidas del script |
    97|| Hermes log | session 20260513_215353 | 22:14:53 | Último "Turn ended" antes del bloqueo |
    98|
    99|---
   100|
   101|## 5. Recomendaciones
   102|
   103|### 5.1 Corrección inmediata (script)
   104|
   105|Parchear `scripts/validate_document_integration.py` para forzar UTF-8 en stdout:
   106|
   107|```python
   108|import sys, io
   109|sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
   110|sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
   111|```
   112|
   113|### 5.2 Corrección sistémica
   114|
   115|1. **Usar Python de WSL** (`python3` en vez de `python.exe` de Windows) para scripts del proyecto — evita problemas de encoding cross-OS.
   116|2. **No re-ejecutar** scripts que fallan con errores de encoding sin verificar que el proceso anterior se cerró.
   117|3. **Agregar guardas** en Hermes para detectar fallos repetidos con el mismo comando y mismo error (ya existe `repeated_exact_failure_warning` pero no detiene la ejecución).
   118|4. **Considerar límite de memoria** por proceso en Windows (Windows Job Objects o `SetProcessWorkingSetSize`).
   119|
   120|### 5.3 Monitoreo
   121|
   122|- Agregar un health check simple de memoria disponible antes de ejecutar scripts pesados.
   123|- Configurar alertas si python.exe supera 2 GB de memoria virtual.
   124|
   125|---
   126|
   127|## 6. Plan de acción sugerido para nueva sesión
   128|
   129|### Fase A: Parche inmediato
   130|1. Cargar `scripts/validate_document_integration.py`
   131|2. Agregar las 3 líneas de UTF-8 al inicio del bloque `if __name__ == "__main__"`
   132|3. Verificar que el script corre sin errores de encoding en Windows
   133|
   134|### Fase B: Corrección de encoding en otros scripts
   135|1. Auditar todos los scripts Python del proyecto que usen `print()` con caracteres Unicode
   136|2. Aplicar la misma fix donde aplique
   137|
   138|### Fase C: Prevención en Hermes
   139|1. Verificar si hay configuración de Hermes para evitar re-ejecución de comandos fallidos
   140|2. Revisar los `repeated_exact_failure_warning` thresholds
   141|
   142|### Fase D: Documentación
   143|1. Agregar a `CONTRIBUTING.md` una nota sobre encoding UTF-8 en scripts
   144|2. Actualizar `documentation_rules.md` si es necesario
   145|
   146|---
   147|
   148|## 7. Notas adicionales
   149|
   150|- **ollama** también estaba corriendo (v0.23.3 con modelo qwen3.5) pero no fue el causante. Consumía 1.5 GB normal.
   151|- **WSL** (vmmemWSL) consumía 1.5 GB normal.
   152|- No hubo errores de disco, RAM defectuosa, ni driver de video fallando — todo fue consecuencia del agotamiento de memoria virtual.
   153|- El equipo tiene **GPU AMD Radeon integrada** (comparte RAM) y **12 núcleos de CPU** (~2 GHz base, boost hasta ~2.5 GHz).
   154|- El script `validate_document_integration.py` fue creado/herramienta durante la sesión del 2026-05-08 (ver `session_20260508_143427_742941.json` en `~/.hermes/sessions/`).
   155|
   156|---
   157|
   158|*Este documento debe cargarse al inicio de la sesión para establecer el contexto antes de planificar.*
   159|

---

## 8. Post-Análisis — Verificación contra código vivo (2026-05-14)

> **Sesión:** Validación del plan FIX-ENCODING-SISTEMICO-2026-05 contra el codebase real.
> **Resultado:** El plan original tenia ~60% de precision. Multiples claims factuales eran incorrectas.

### 8.1 Scripts que YA tenian fix de encoding (el plan no lo sabia)

| Script | Fix presente | Tipo de fix | Lineas |
|--------|-------------|------------|--------|
| `main.py` | `sys.stdout.reconfigure(encoding="utf-8")` | reconfigure (Python >=3.7) | L32-35 |
| `derive_version_from_changelog.py` | `reconfigure()` + fallback `TextIOWrapper` | Dual | L12-17 |
| `version_consistency_checker.py` | `reconfigure()` + fallback `TextIOWrapper` | Dual | L28-35 |
| `log_phase_completion.py` | `reconfigure()` + fallback `TextIOWrapper` | Dual | L39-46 |
| `validate_document_integration.py` | `TextIOWrapper` en `if __name__ == "__main__"` | Simple | L461-462 |

**Conclusion:** 5 de los scripts mas Unicode-intensivos ya estan protegidos. El plan sobreestimaba el trabajo restante.

### 8.2 Scripts que REALMENTE necesitan parche (sin fix, con Unicode en prints)

| Script | Unicode detectado | Riesgo |
|--------|------------------|--------|
| `verify_ga4.py` | `ñ`, `í`, `ó` en `print()` | **ALTO** — imprime a stdout en Windows |
| `validate_structure.py` | `ó`, `é` en `print()` de status | **ALTO** — multiples prints con tildes |
| `update_benchmarks.py` | `→` (U+2192) en `print()` | **MEDIO** — un solo print con simbolo |

Scripts con Unicode SOLO en comentarios (riesgo bajo, no requieren accion inmediata): `sync_versions.py`, `fill_upgrade_proposal.py`, `config_checker.py`, `validate_context_integrity.py`, `run_all_validations.py`, `generate_system_status.py`.

### 8.3 Falsas alarmas del plan original

| Plan decia | Realidad |
|-----------|----------|
| `doctor.py` necesita revision de Unicode | **CERO** caracteres no-ASCII. Falsa alarma. |
| `derive_version_from_changelog.py` necesita parche | **YA TIENE fix** (reconfigure + TextIOWrapper). Verificar, no parchear. |
| `main.py` necesita parche | **YA TIENE fix** (reconfigure L32-35). Verificar, no parchear. |
| 4 scripts con Unicode identificados | En realidad son **14 scripts** con algun Unicode, pero solo **3 necesitan parche** (el resto ya tiene fix o es solo comentarios). |

### 8.4 Gap sutil detectado en FASE-A

`validate_document_integration.py` tiene `sys.stderr.write()` en las lineas 52 y 55, dentro de la funcion `read_file()`, que se ejecuta a nivel de modulo — **FUERA del bloque `if __name__ == "__main__"`** donde esta el `TextIOWrapper` (L461). Si ocurre un error de archivo al importar (antes de ejecutar main), `stderr.write()` con Unicode puede fallar antes de que el fix se active.

**Riesgo:** Bajo (solo si hay error de archivo al inicio). **Accion:** Documentado; no requiere parche inmediato.

### 8.5 Patrones de fix inconsistentes en el codebase

El codigo vivo usa 2 patrones distintos sin estandarizacion:

| Patron | Usado por | Recomendacion |
|--------|----------|---------------|
| `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` | main.py, log_phase_completion.py, version_consistency_checker.py | **PREFERIDO** — mas limpio, moderno |
| `io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')` | validate_document_integration.py, derive_version_from_changelog.py (fallback) | Usar solo como **fallback** para Python <3.7 |

**Decision para el plan:** Estandarizar en `reconfigure()` como patron primario, `TextIOWrapper` como fallback. No reescribir scripts ya parcheados (ambos patrones funcionan).

### 8.6 Mecanismo exacto del memory leak (refinamiento)

El incidente no fue solo `UnicodeEncodeError` -> memory leak. Fue una cascada de 3 capas:

1. **Python imprime `↔` en stdout cp1252** -> `UnicodeEncodeError`
2. **La excepcion rompe la pipe** entre Hermes y el proceso Python -> `_readerthread` exception (el thread de lectura de Hermes no puede leer la pipe rota)
3. **Hermes re-ejecuta el comando** sin verificar que el proceso anterior termino -> el proceso zombie con pipe rota mantiene buffers en memoria
4. **Repeticion 5x en 3 minutos** -> 42.5 GB acumulados

La prevencion requiere LAS 3 CAPAS: (a) fix encoding en scripts, (b) asegurar que Hermes limpia procesos tras pipe rota, (c) no re-ejecutar comandos que fallan con el mismo error.

### 8.7 Estructura de scripts en el proyecto (inventario completo)

Total: **21 scripts Python** en `scripts/`. El plan original solo mencionaba 6.

**Con fix de encoding:** `derive_version_from_changelog.py`, `log_phase_completion.py`, `validate_document_integration.py`, `version_consistency_checker.py` (+ `main.py` en raiz).

**Sin fix, necesitan parche:** `verify_ga4.py`, `validate_structure.py`, `update_benchmarks.py`.

**Sin fix, solo Unicode en comentarios (baja prioridad):** `sync_versions.py`, `fill_upgrade_proposal.py`, `config_checker.py`, `validate_context_integrity.py`, `run_all_validations.py`.

**Sin Unicode detectado:** `doctor.py`, `cleanup_sessions.py`, `cleanup_workdirs.py`, `normalize_cache_filenames.py`, `prune_outputs.py`, `structure_guard.py`, `validate.py`, `validate_agent_ecosystem.py`.

---

*Ultima actualizacion: 2026-05-14 — validacion post-analisis contra codigo vivo.*
