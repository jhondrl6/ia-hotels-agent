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
   - Estado: PENDIENTE de decisión operativa
   - Restricción: presupuesto "FUERA DE SERVICIO" (R2.1/D-V2.1)
   - No se ha ejecutado rotación automática ni subida de evidencia

4. Comparación: retirada de HEAD vs saneamiento de historial
   - Retirada de HEAD: cambiar la key en el código y .env
     * Pros: simple, reversible, no altera historial
     * Contras: la key vieja sigue en historial (accesible con git checkout)
   - Saneamiento de historial: git filter-branch / BFG Repo Cleaner
     * Pros: elimina la key del historial completo
     * Contras: destructivo, reescribe commits, requiere force-push,
       afecta a todos los clones, puede romper referencias en issues/PRs
   - Decisión pendiente: el operador debe evaluar coste/beneficio
     * Si el repo es público y la key sigue activa → saneamiento recomendado
     * Si la key ya fue rotada o el repo es privado → retirada de HEAD suficiente

5. Evidencia no secreta
   - Archivo: evidence/FASE-P4/informe-observacion.md (línea 155)
   - Contenido: descripción del hallazgo sin la key completa
   - Referencia: "key=AIza…" (truncado en el informe original)
   - Nota: el archivo archives/gbp_profiles.json contiene una key real
     en HTML embebido (capturada durante scraping de GBP profiles)

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

2. Contención operativa (pendiente)
   - Rotación de keys: decisión del operador
     * Gemini: pendiente (presupuesto FUERA DE SERVICIO)
     * OpenRouter: pendiente (presupuesto FUERA DE SERVICIO)
     * Perplexity: pendiente (presupuesto FUERA DE SERVICIO)
   - Contención de datos: no se ha ejecutado
     * No se ha hecho escaneo en nube
     * No se ha hecho rotación automática
     * No se ha subido evidencia a terceros
   - Disposición de datos con cliente: pendiente
     * No se ha definido política de retención
     * No se ha definido política de notificación

3. Estados explícitos
   - Técnico: ✅ DONE (fix implementado y testeado)
   - Operativo: ⏳ PENDING (rotación/contención requieren decisión del operador)
   - Publicación: ⛔ BLOCKED (mientras rotación/contención sigan pendientes
     sin resolución verificable o aceptación explícita del riesgo)

4. Dueños
   - Controles técnicos: mantenimiento de validaciones/providers
   - Credenciales: operador
   - Autorización de publicación: operador (consentimiento explícito)

5. Criterios de cierre
   - Rotación verificable de las 3 keys (Gemini, OpenRouter, Perplexity)
   - O aceptación explícita del riesgo por el operador (documentada)
   - O contención verificable (ej: repo privado, key ya rotada, historial saneado)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPENDENCIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- FASE-P6: NO depende de AC-S3/AC-S4 (puede ejecutarse en paralelo)
- FASE-RELEASE: SÍ depende de AC-S4 resuelta
  * No se puede publicar mientras rotación/contención sigan pendientes
  * Sin resolución verificable o aceptación explícita del riesgo
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
