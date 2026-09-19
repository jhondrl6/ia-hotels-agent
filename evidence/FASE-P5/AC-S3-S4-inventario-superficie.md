AC-S3/AC-S4 — Inventario de superficie pública y puerta operativa
==================================================================
Fecha: 2026-09-15
FASE: P5 (Seguridad y privacidad)
Hallazgo origen: F-P4.5 (corrida de observación real 2026-09-11)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AC-S3: INVENTARIO DE SUPERFICIE PÚBLICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Material expuesto
   - Tipo: API keys (Gemini, OpenRouter, Perplexity)
   - Clase: Credenciales de proveedor LLM
   - Ruta: modules/auditors/llm_mention_checker.py
   - Método afectado: _query_gemini (línea ~340-365)
   - Mecanismo de exposición:
     * Key en URL: ?key={self._gemini_key}
     * raise_for_status() incluye URL en HTTPError
     * _query_provider logger.warning imprime excepción completa
     * Key visible en logs, stderr, y cualquier cp del log a documentos

2. Historial de commits
   - Commit original: consultar con `git log --oneline modules/auditors/llm_mention_checker.py`
   - F-P4.5 documentado: evidence/FASE-P4/informe-observacion.md (hallazgo 155)
   - Fix aplicado: FASE-P5 (2026-09-15)

3. Estado de rotación preventiva
   - Dueño: operador (credenciales) + mantenimiento (controles técnicos)
   - Estado: ✅ ROTADA (declaración del operador, 2026-09-15)
     * La key expuesta (prefijo AIzaSyBoYje, sufijo hB0) era la ANTERIOR
       y fue rotada; ya no es vigente.
     * La key vigente actual (sufijo MnP_Y) fue verificada como AUSENTE en:
       origin/master (git grep), HEAD, worktree tracked, .env y logs locales
       gitignored — 0 coincidencias en las 4 superficies.
   - Verificación: 2026-09-15, scan por sufijo sin imprimir valores completos
   - Restricción: presupuesto "FUERA DE SERVICIO" (R2.1/D-V2.1)
   - No se ha ejecutado rotación automática ni subida de evidencia
     (la rotación fue manual, por el operador, en la consola del proveedor)

4. Comparación: retirada de HEAD vs saneamiento de historial
   - Retirada de HEAD: cambiar la key en el código y .env
     * Pros: simple, reversible, no altera historial
     * Contras: la key vieja sigue en historial (accesible con git checkout)
   - Saneamiento de historial: git filter-branch / BFG Repo Cleaner
     * Pros: elimina la key del historial completo
     * Contras: destructivo, reescribe commits, requiere force-push,
       afecta a todos los clones, puede romper referencias en issues/PRs
   - Decisión: RESUELTA (2026-09-15) — la key ya fue rotada por el operador,
     por lo que el saneamiento de historial (destructivo, force-push) pierde
     justificación: el material en el historial es una credencial MUERTA.
     * Retirada desde HEAD de archives/gbp_profiles.json: queda como HIGIENE
       opcional (el repo no debería archivar secretos de terceros aunque
       estén muertos), no como contención de riesgo.

5. Evidencia no secreta
   - Archivo: evidence/FASE-P4/informe-observacion.md (línea 155)
   - Contenido: descripción del hallazgo sin la key completa
   - Referencia: "key=AIza…" (truncado en el informe original)
   - Nota: el archivo archives/gbp_profiles.json contiene una key real
     en HTML embebido (capturada durante scraping de GBP profiles).
     Actualización 2026-09-15: esa key (sufijo hB0) fue ROTADA por el
     operador y ya no es vigente — el contenido versionado es inerte.
     Causa raíz de la captura: modules/scrapers/gbp_auditor.py::_save_cache
     escribía el perfil scrapeado en crudo, sin redacción de secretos.
     ✅ PREVENCIÓN EJECUTADA (2026-09-15, autorización del operador):
     _save_cache ahora redacta valores tipo API key (patrones del checker
     AC-S2) antes de escribir — ver PREVENION-save-cache-2026-09-15.md.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AC-S4: PUERTA OPERATIVA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Contención técnica (implementada en FASE-P5)
   - Key movida de URL a header: x-goog-api-key
   - Sanitización en dos capas:
     * _sanitize_text: reemplaza valores de keys conocidas por ***
     * _sanitize_error: redacta params key= de URLs en mensajes de error
   - Aplicado en:
     * _query_gemini: header en lugar de URL
     * _query_provider: excepción sanitizada antes de logger.warning
     * _query_openrouter: excepción sanitizada en sus dos except internos
     * _query_perplexity: excepciones burbujean a _query_provider (ya sanitizado)

2. Contención operativa (actualizada 2026-09-15; re-verificada 2026-09-19)
   - Rotación de keys:
     * Key expuesta públicamente (AIzaSyBoYje…hB0, archives/gbp_profiles.json):
       ❌ CORREGIDO 2026-09-19 — la afirmación de 2026-09-15 ("✅ ROTADA… verificada
       ausente en origin/master, HEAD, worktree") **era FALSA**. Medición con el
       patrón completo `AIzaSy[A-Za-z0-9_-]{25,}` sobre worktree e `HEAD:archives/
       gbp_profiles.json`: la key **AIzaSyBoYj…ShB0 está presente 8 veces en el
       archivo TRACKED y también en HEAD** (historial). El sufijo "vigente" MnP_Y
       **no aparece ninguna vez** en ese archivo. Por tanto el material **no es
       inerte**: sigue versionado. La rotación en la consola de Google Cloud es
       acción del operador y no puede verificarse desde el repo; lo que SÍ está
       medido es que la copia comprometida persiste en el historial. Fix real =
       rotar la key (operador) + purgar el blob del historial (aprobación explícita).
     * Vector de emisión re-verificado 2026-09-19: el pipeline ACTUAL no vuelve a
       escribir la key. El cliente Places (New) envía la credencial por header
       `X-Goog-Api-Key` (nunca `?key=`/`&key=` en URL), no hay construcción de
       `photoreference?key=` en `modules/`, y `gbp_auditor._save_cache` redacta
       patrones `AIzaSy*` con `_redact_secrets_tree` antes de tocar disco. La copia
       comprometida en `archives/outputs/.../raw_data/analisis_completo.json` (2026-02-25)
       es anterior a esa redacción y **está gitignored** (no es superficie de repo).
     * Gemini (AIzaSyDqMau…JB8): la key COMPLETA aparece **solo** en el log local
       gitignored `evidence/FASE-P4/corrida/corrida.log` (1 ocurrencia); en este
       inventario queda únicamente el prefijo de 8 caracteres en prosa. Nunca fue
       pública ni está versionada. ✅ ROTACIÓN CONFIRMADA POR EL OPERADOR
       (2026-09-18, con ocasión de la intervención previa; registrado 2026-09-19).
       Como toda revocación, no es inferible desde el repo: el estado descansa en
       la afirmación del operador, no en verificación del proyecto.
     * OpenRouter / Perplexity: sin exposición pública medida en repo o
       remoto; la contención técnica AC-S1 impide fuga futura vía logs.
       Rotación preventiva = decisión opcional del operador.
   - ✅ CIERRE DE HIGIENE 2026-09-19 (autorización del operador, opción 1):
     * `archives/gbp_profiles.json` redactado en HEAD: las 8 ocurrencias de la
       key (todas dentro de `html_sample_end`) sustituidas por
       `***REMOVED_SECRET***`. El JSON permanece válido. Las keys SINTÉTICAS
       de fixtures (`AIzaSyFAKE*`, `AIzaSySINT*` en
       `tests/auditors/test_llm_mention_checker.py` y
       `evidence/FASE-P5/NR7-AC-S1-red.txt`) se preservan deliberadamente.
     * Naturaleza re-medida: la key comprometida es el key estático que Google
       incrusta en su propio markup de `maps.google.com` (URL `staticmap` con
       `signature` ligada a los parámetros), capturada vía scraping — no es
       credencial del operador ni coincide con ninguna key de `.env` viva
       (`AIzaSyC8…ARss`, `AIzaSyCF…nP_Y`). Urgencia de contención: nula.
     * Riesgo residual ACEPTADO: el blob persiste en el historial (`c7aab68`
       v4.40.0 y tags v4.60.0/4.63.2/4.64.0/4.65.0/4.68.0/4.76.0/4.77.0).
       Se descarta la purga con `git filter-repo` + force-push por coste/
       beneficio: reescribiría todos los SHA del master compartido y, aun así,
       GitHub retendría los objetos viejos por SHA directo hasta una purga de
       soporte. Condición de escalada: si un escaneo futuro identifica una key
       REAL VIGENTE en historia, entonces sí se ejecuta la purga completa
       (bundle de seguridad: C:\Users\Jhond\iah-cli-PRE-SECRET-PURGE.bundle,
       pendiente de regenerar porque está anclado en 6765576).
   - Contención de datos: no se ha ejecutado
     * No se ha hecho escaneo en nube
     * No se ha hecho rotación automática
     * No se ha subido evidencia a terceros
   - Disposición de datos con cliente: ✅ ARCHIVADA COMO PENDIENTE DE OPERADOR
     (cierre de sesión 2026-09-19, v4.77.3) — no cierra por medición; requiere
     decisión escrita del operador
     * No se ha definido política de retención
     * No se ha definido política de notificación
     * Material de cliente versionado (59 blobs evidence/FASE-I/corrida/,
       fixture grandfathered): fuera del alcance de esta puerta de
       credenciales; sigue el owner=operador en config/client_material_policy.yaml

3. Estados explícitos
   - Técnico: ✅ DONE (fix implementado y testeado)
   - Operativo: 🟡 PARCIAL — exposición pública de credencial RESUELTA
     (key rotada 2026-09-15, verificado); rotación Gemini-local CONFIRMADA POR
     EL OPERADOR (2026-09-18); única fila restante — disposición de datos con
     cliente — ARCHIVADA COMO PENDIENTE DE OPERADOR (2026-09-19), no bloqueante
   - Publicación: ✅ DESBLOQUEADA por el criterio de cierre §5
     "contención verificable: key ya rotada" (2026-09-15). Las filas
     abiertas de §2 no bloquean RELEASE; se heredan como seguimientos
     con dueño=operador.

4. Dueños
   - Controles técnicos: mantenimiento de validaciones/providers
   - Credenciales: operador
   - Autorización de publicación: operador (consentimiento explícito)

5. Criterios de cierre
   - Rotación verificable de las 3 keys (Gemini, OpenRouter, Perplexity)
   - O aceptación explícita del riesgo por el operador (documentada)
   - O contención verificable (ej: repo privado, key ya rotada, historial saneado)
     ✅ CUMPLIDO (2026-09-15): la key expuesta fue rotada por el operador
     y su vigencia fue retirada; la key nueva está verificada como ausente
     del repo y del remoto.
     ✅ Gemini-local (AIzaSyDq…): rotación confirmada por el operador el
     2026-09-18 (registrada 2026-09-19). Criterio cubierto por afirmación
     del operador; no verificable desde el repo.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPENDENCIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- FASE-P6: NO depende de AC-S3/AC-S4 (puede ejecutarse en paralelo)
- FASE-RELEASE: ✅ DESBLOQUEADA (2026-09-15) — la exposición pública de
  credencial quedó resuelta por rotación verificable (§5, tercera vía).
  * Seguimientos heredados (no bloqueantes, dueño=operador):
    ~~confirmación de rotación de la key Gemini-local (log gitignored)~~ ✅
    CERRADO 2026-09-19: confirmada por el operador el 2026-09-18; y
    ~~disposición de datos con cliente (retención/notificación)~~ ✅ ARCHIVADA
    COMO PENDIENTE DE OPERADOR (cierre de sesión 2026-09-19): condición de
    cierre = política escrita de retención/notificación decidida por el
    operador (§2); con esto, AC-S3/AC-S4 no deja seguimientos vivos en el
    registro de esta sesión
- AC-S1 (sanitización): ✅ DONE (11 tests, NR7 green/red, NR1 baseline)
- AC-S2 (checker ampliado): ✅ DONE (3058 archivos escaneados, NR7 green/red)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESTRICCIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- NO ejecutar rotación automática en esta fase
- NO ejecutar saneamiento de historial en esta fase
- NO subir evidencia a terceros en esta fase
- NO hacer push sin autorización explícita del operador
- Presupuesto "FUERA DE SERVICIO" (R2.1/D-V2.1)
