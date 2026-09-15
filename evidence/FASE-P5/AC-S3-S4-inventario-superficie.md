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

2. Contención operativa (actualizada 2026-09-15)
   - Rotación de keys:
     * Key expuesta públicamente (AIzaSyBoYje…hB0, archives/gbp_profiles.json):
       ✅ ROTADA por el operador (declaración 2026-09-15). La key vigente
       (sufijo MnP_Y) verificada ausente en origin/master, HEAD, worktree,
       .env y logs locales. El material en el historial público es inerte.
     * Gemini (AIzaSyDqMau…JB8, SOLO en log local gitignored
       evidence/FASE-P4/corrida/corrida.log): nunca fue pública; estado de
       rotación NO CONFIRMADO por el operador (fila abierta, riesgo local).
     * OpenRouter / Perplexity: sin exposición pública medida en repo o
       remoto; la contención técnica AC-S1 impide fuga futura vía logs.
       Rotación preventiva = decisión opcional del operador.
   - Contención de datos: no se ha ejecutado
     * No se ha hecho escaneo en nube
     * No se ha hecho rotación automática
     * No se ha subido evidencia a terceros
   - Disposición de datos con cliente: pendiente
     * No se ha definido política de retención
     * No se ha definido política de notificación
     * Material de cliente versionado (59 blobs evidence/FASE-I/corrida/,
       fixture grandfathered): fuera del alcance de esta puerta de
       credenciales; sigue el owner=operador en config/client_material_policy.yaml

3. Estados explícitos
   - Técnico: ✅ DONE (fix implementado y testeado)
   - Operativo: 🟡 PARCIAL — exposición pública de credencial RESUELTA
     (key rotada 2026-09-15, verificado); filas abiertas: confirmación
     rotación Gemini-local y disposición de datos con cliente
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPENDENCIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- FASE-P6: NO depende de AC-S3/AC-S4 (puede ejecutarse en paralelo)
- FASE-RELEASE: ✅ DESBLOQUEADA (2026-09-15) — la exposición pública de
  credencial quedó resuelta por rotación verificable (§5, tercera vía).
  * Seguimientos heredados (no bloqueantes, dueño=operador):
    confirmación de rotación de la key Gemini-local (log gitignored) y
    disposición de datos con cliente (retención/notificación)
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
