# Referencia: skill del fabricante `typesafe-ai` (FASE-B, 2026-10-03)

Registro de una referencia externa usada por el piloto, con su procedencia medida. No es codigo del
proyecto ni workflow de la casa: vive fuera del arbol versionado y aqui solo se la nombra con su
identidad, para que la siguiente sesion no vuelva a preguntarse de donde salio.

## Que es y de donde vino

| Dato | Valor medido |
|---|---|
| Archivo evaluado | `C:\Users\Jhond\Github\SKILL.md` |
| Identidad | sha256 `71ea90d7906c6554...`, 10.040 bytes, 149 lineas leidas |
| Naturaleza | skill de agente del fabricante (frontmatter `name: typesafe-ai`, `license: MIT`): direccion de disenio para construir con los modelos System One, no contrato ni codigo |
| Instalada en | `C:\Users\Jhond\.qoder\skills\typesafe-ai\SKILL.md` (sha256 `de8b4c35a3801f12...`, 10.040 bytes) |
| Como se instalo | entry point oficial `skill_manage` con `action=create`; despues aparecio en el listado de skills de la sesion, o sea quedo registrada y no es un archivo hueso |

## Procedencia: lo que si se pudo probar y lo que no

- **NO la trae el paquete**: buscado en `tmp_test/venv-jev-sdk/Lib/site-packages`, `typesafe-sdk==0.7.0`
  solo incluye LICENSEs de dependencias. La guia no es material empaquetado por el fabricante junto
  al SDK, asi que su autoria no se certifica desde el disco.
- **SU contenido cruza contra las docs vivas**: se descargo el indice real
  `https://docs.typesafe.ai/llms.txt` (guardado aqui como `docs_typesafe_llms.txt`, 118 lineas, 16.132
  bytes, sha256 `4151e8fd18e54945...`) y los 9 enlaces que la skill usa como tabla de entrada casan
  **1 de 1** cada uno: `concepts/system-one.md`, `concepts/state.md`, `primitives/noul.md`,
  `primitives/choice.md`, `primitives/score.md`, `api.md`, `sdk/python.md`, `confidence.md`,
  `cookbooks/rerank_typesafe.md`. Es decir: coherente con el fabricante, no inventada.
- **Identidad de la copia instalada, verificada por partes y no por un sha a ciegas**: cuerpo
  **identico byte a byte** (135 lineas); frontmatter **identico tras plegar blancos YAML** (el
  `description` usa el scalar plegado `>`). Los sha256 crudos difieren solo por los puntos de plegado
  de esas dos lineas, no por contenido. Tamano total coincidente (10.040 bytes) porque cada salto
  plegado cambia `\n`+espacios por espacio sin variar el conteo.
- **Dato de red que atane a P4**: `docs.typesafe.ai` y `api.typesafe.ai` **no resuelven por DNS local**
  (gaierror), pero el indice respondio `HTTP/1.1 200 OK` a traves del proxy de la maquina. El SDK
  (`httpx2`) honra las variables de proxy del entorno, y `openrouter.ai` si resuelve directo. El
  preflight del piloto tendra que registrar el transporte real por el que salio, no asumir DNS.

## Por que NO se versiona en el repo (decision tomada, con sus razones medidas)

1. **Procedencia**: archivo de autoria no certificable en disco; la casa no versiona material de
   terceros sin registro de origen, y aqui el origen util es la web viva, que ya se copio como crudo.
2. **Taxonomia**: el hogar validado de skills del repo es `.agents/workflows/` con registro en su
   README (`scripts/validate_agent_ecosystem.py:35` y `:91-96`). Un `SKILL.md` en la raiz es inerte;
   registrarlo en `.agents/workflows/` meteria prosa del fabricante en el corpus de workflows que la
   orden del 2026-08-24 podó a proposito (16 skills archivados).
3. **Caducidad silenciosa**: guia sin fecha que apunta a docs vivas y que ella misma declara que la
   fuente de verdad son las docs. En el arbol caducaria sin lector, que es la clase de texto que las
   ultimas podas de AGENTS.md retiraron.
4. **La prosa viaja**: documentacion suelta en el arbol puede proyectarse a los packs y disparar
   gates; ningun gate necesita ver este archivo.

## Utilidad real para este plan (por eso se instala y se cita)

- **Tarea 1 de FASE-B** («verificar docs actuales de Jev/DeepSeek: paquetes, modelos, payload, usage,
  errores, tarifas y limites»): su tabla de enlaces es el mapa de entrada al indice vivo, ya probado
  contra `docs_typesafe_llms.txt`. Incluye paginas que el plan no habia nombrado, como
  `introduction/coding-agents.md`.
- **Diseno de las preguntas de la corrida de recuperacion**: la semantica de **Noul** («probabilidad de
  si, *sin* confidence aparte; un valor cerca de 0.5 es probabilidad similar, no intensidad media») es
  el contrato que AC2 fija con `test_noul_probability_is_not_confidence`; y la advertencia de que la
  confidence de Choice/Score resume concentracion de la distribucion y **no** es permiso para actuar es
  lo que L-ENT.9 exige registrar. Tambien su regla de incluir una salida «no aplica» cuando nada puede
  casar, que es donde la rubrica del protocolo pone `insuficiente`.
- **La separacion que la pata (b) implementa**: «separar evidencia faltante, error del modelo, error de
  codigo y fallo del servicio» es la misma distincion que `error_kind_de` y `usage_normalized` codifican
  bajo DA-C3/AC9.

## Cruce con la decision de transporte

La skill empuja a leer las docs y el SDK instalados antes de escribir integracion, y prohibe inventar
detalles version-dependientes. Eso refuerza el rechazo a OpenRouter como transporte alterno del piloto
(registrado en `entorno.json` bajo `transporte_alterno_evaluado`): su garantia es el contrato del SDK
real, no una capa OpenAI-compatible.
