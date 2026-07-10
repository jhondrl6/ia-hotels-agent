<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>¿Cuánto pierde su hotel? — {{HOTEL_NOMBRE}}</title>
    <link rel="stylesheet" href="hook_styles.css">
</head>
<body>

<!-- ============================================================ -->
<!-- PÁGINA 1 — "¿Cuánto pierde su hotel?"                        -->
<!-- ============================================================ -->
<div id="page-1" class="page">

    <!-- Header -->
    <header id="header-hotel">
        <h1 id="hotel-nombre">{{HOTEL_NOMBRE}}</h1>
        <p id="hotel-meta">
            <span id="hotel-direccion">{{HOTEL_DIRECCION}}</span> ·
            <span id="hotel-region">{{HOTEL_REGION}}</span>
        </p>
        <p id="hotel-gbp">
            <span id="gbp-rating">{{GBP_RATING}}</span> ★ ·
            <span id="gbp-resenas">{{GBP_RESENAS}}</span> reseñas en Google
        </p>
    </header>

    <!-- Hook figure -->
    <section id="hook-section">
        <h2 id="hook-title">¿Cuánto pierde su hotel cada mes?</h2>
        <p id="hook-figure">{{FUGA_MENSUAL}} COP</p>
        <p id="hook-range">
            Rango estimado: {{FUGA_MINIMA}} – {{FUGA_MAXIMA}} COP/mes
        </p>
        <p id="hook-disclaimer">
            (Estimación basada en datos de la región y perfil de su hotel.)
        </p>
    </section>

    <!-- OTA commission -->
    <section id="ota-section">
        <h3>Comisión OTA anual</h3>
        <p id="comision-ota">{{COMISION_OTA_REAL}} COP/año</p>
    </section>

    <!-- Top 3 gaps -->
    <section id="gaps-section">
        <h3>Las 3 brechas que más le cuestan</h3>
        <table id="gaps-table">
            <thead>
                <tr>
                    <th>Brecha</th>
                    <th>Impacto estimado</th>
                    <th>Justificación</th>
                </tr>
            </thead>
            <tbody>
                <tr id="brecha-1">
                    <td class="brecha-nombre">{{BRECHA_1_NOMBRE}}</td>
                    <td class="brecha-cop">{{BRECHA_1_COP}} COP/mes</td>
                    <td class="brecha-justificacion">{{BRECHA_1_JUSTIFICACION}}</td>
                </tr>
                <tr id="brecha-2">
                    <td class="brecha-nombre">{{BRECHA_2_NOMBRE}}</td>
                    <td class="brecha-cop">{{BRECHA_2_COP}} COP/mes</td>
                    <td class="brecha-justificacion">{{BRECHA_2_JUSTIFICACION}}</td>
                </tr>
                <tr id="brecha-3">
                    <td class="brecha-nombre">{{BRECHA_3_NOMBRE}}</td>
                    <td class="brecha-cop">{{BRECHA_3_COP}} COP/mes</td>
                    <td class="brecha-justificacion">{{BRECHA_3_JUSTIFICACION}}</td>
                </tr>
            </tbody>
        </table>
    </section>

    <!-- 4 pillars table -->
    <section id="pillars-section">
        <h3>Visibilidad digital: Su hotel vs. promedio regional</h3>
        <table id="pillars-table">
            <thead>
                <tr>
                    <th>Pilar</th>
                    <th>Su hotel</th>
                    <th>Promedio regional</th>
                </tr>
            </thead>
            <tbody>
                <tr id="pillar-seo">
                    <td class="pillar-name">SEO</td>
                    <td class="pillar-score">{{SEO_SCORE}}</td>
                    <td class="pillar-regional">{{SEO_REGIONAL}}</td>
                </tr>
                <tr id="pillar-geo">
                    <td class="pillar-name">GEO</td>
                    <td class="pillar-score">{{GEO_SCORE}}</td>
                    <td class="pillar-regional">{{GEO_REGIONAL}}</td>
                </tr>
                <tr id="pillar-aeo">
                    <td class="pillar-name">AEO</td>
                    <td class="pillar-score">{{AEO_SCORE}}</td>
                    <td class="pillar-regional">{{AEO_REGIONAL}}</td>
                </tr>
                <tr id="pillar-iao">
                    <td class="pillar-name">IAO</td>
                    <td class="pillar-score">{{IAO_SCORE}}</td>
                    <td class="pillar-regional">{{IAO_REGIONAL}}</td>
                </tr>
            </tbody>
        </table>
    </section>

</div>

<!-- ============================================================ -->
<!-- PÁGINA 2 — "Cómo se resuelve"                                -->
<!-- ============================================================ -->
<div id="page-2" class="page">

    <!-- Explanation -->
    <section id="explanation-section">
        <h2>Cómo se resuelve</h2>
        <p>
            Su hotel pierde visibilidad frente a los buscadores tradicionales y los
            nuevos asistentes de inteligencia artificial. Esto significa que los
            viajeros que buscan hospedaje en <strong>{{HOTEL_REGION}}</strong> no lo
            encuentran — y reservan con la competencia o por OTA.
        </p>
        <p>
            Nuestro servicio corrige las brechas técnicas y de contenido que impiden
            que su hotel aparezca en Google, Google Maps, ChatGPT y otros asistentes.
        </p>
    </section>

    <!-- Projection -->
    <section id="projection-section">
        <h3>Proyección a 6 meses</h3>
        <table id="projection-table">
            <tbody>
                <tr id="proj-recuperacion">
                    <td class="proj-label">Recuperación estimada</td>
                    <td class="proj-value">{{RECUPERACION_6M}} COP</td>
                </tr>
                <tr id="proj-roi">
                    <td class="proj-label">ROI sobre inversión</td>
                    <td class="proj-value">{{ROI}}</td>
                </tr>
                <tr id="proj-fuga-acumulada">
                    <td class="proj-label">Fuga acumulada sin actuar</td>
                    <td class="proj-value">{{FUGA_6M}} COP</td>
                </tr>
            </tbody>
        </table>
    </section>

    <!-- CTA -->
    <section id="cta-section">
        <h3>Diagnóstico Express</h3>
        <p id="cta-precio">
            <strong>{{PRECIO_EXPRESS}} COP</strong> — pago único
        </p>
        <p id="cta-garantia">
            Si no encuentra valor en el diagnóstico, le devolvemos el 100%.
        </p>
        <p id="cta-contacto">
            Escríbanos para agendar su diagnóstico:
            <a href="{{HOTEL_URL}}">{{HOTEL_URL}}</a>
        </p>
    </section>

    <!-- Pricing reference -->
    <section id="pricing-reference">
        <p id="pricing-monthly">
            Plan mensual: <strong>{{PRECIO_MENSUAL}} COP/mes</strong>
        </p>
        <p id="pricing-setup">
            Setup inicial: <strong>{{SETUP_FEE}} COP</strong>
        </p>
    </section>

    <!-- Evidence tier disclaimer -->
    <footer id="evidence-disclaimer">
        <p>
            <small>Nivel de evidencia: {{EVIDENCE_TIER}}</small>
        </p>
    </footer>

</div>

</body>
</html>
