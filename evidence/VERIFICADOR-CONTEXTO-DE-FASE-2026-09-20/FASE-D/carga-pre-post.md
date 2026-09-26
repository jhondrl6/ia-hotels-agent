# PAR PRE/POST de carga de lectura (AC20) — FASE-D

- comando de los dos lados: `stat -c %s <ruta>` (las rutas estan en `carga.json` -> `rutas_stat`; sin deduplicar: cada fase abre su copia del workflow)
- comando que produce el pack: `./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
- tokens: estimados por divisor 4 declarado, no recuento de tokenizer

| lado | stat -c %s | total en carga.json | coste de generar |
|---|---|---|---|
| before | 1648109 | 1648109 | 0 |
| after | 1430580 | 1431388 | 808 |

**Resta entre cargas totales: 1648109 - 1431388 = 216721 bytes (~54180 tokens estimados).**

Comprobaciones:
- [x] stat_pre == total_before: OK
- [x] stat_post + coste == total_after: OK
- [x] suma por fase == total (before): OK
- [x] suma por fase == total (after): OK
- [x] identidad del delta por fase: OK

Lectura obligatoria (contrato §Carga total y frescura del pack): la resta **no** es «fuentes contra pack». Cada lado publica sus tres sumandos y el unico ahorro atribuible al pack es lo que no entro porque no se declaro (`omitido_declarado_bytes`), neteado por el andamiaje del propio pack (`andamiaje_del_pack_bytes`) y por el coste de generarlo. El workflow canonico sigue en los dos lados: este plan no lo rebanó (deuda D3), y por eso el delta no puede presentarse como un tercio de la carga.
