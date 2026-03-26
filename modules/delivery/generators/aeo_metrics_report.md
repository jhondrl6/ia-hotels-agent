# AEO Metrics Report

**Hotel**: {{HOTEL_NAME}}
**URL**: {{HOTEL_URL}}
**Generated**: {{TIMESTAMP}}
**Data Source**: {{DATA_SOURCE}}

---

## Executive Summary

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| AI Visibility Score | {{AI_VISIBILITY_SCORE}} | 70+ | {{STATUS_AI_VISIBILITY}} |
| Share of Voice | {{SOV_PERCENTAGE}} | 25%+ | {{STATUS_SOV}} |
| Citation Rate | {{CITATION_RATE}} | 60%+ | {{STATUS_CITATION}} |
| Voice Readiness Index | {{VOICE_READINESS}} | 80+ | {{STATUS_VOICE_READINESS}} |
| **Composite Score** | **{{COMPOSITE_SCORE}}** | **75+** | **{{STATUS_COMPOSITE}}** |

---

## AI Visibility Score

**Score**: {{AI_VISIBILITY_SCORE}}/100

{{#if AI_VISIBILITY_TREND}}
**Trend**: {{AI_VISIBILITY_TREND}}
{{/if}}

{{#if DATA_SOURCE}}
*Source: {{DATA_SOURCE}}*
{{/if}}

### Breakdown

```
AI Visibility Score
{{AI_VISIBILITY_BAR}}
{{AI_VISIBILITY_SCORE}}/100
```

### Insights

{{AI_VISIBILITY_INSIGHTS}}

---

## Share of Voice

**Your SOV**: {{SOV_PERCENTAGE}}%

### vs Competitors

| Competitor | SOV |
|------------|-----|
{{#each COMPETITORS}}
| {{domain}} | {{sov}}% |
{{/each}}

### Visualization

```
Share of Voice Distribution
{{SOV_VISUALIZATION}}
```

---

## Citation Rate

**Rate**: {{CITATION_RATE}}%

{{#if CITATION_DETAILS}}
### Details

- Total mentions analyzed: {{CITATION_DETAILS.total_mentions}}
- Citations with link: {{CITATION_DETAILS.citations_with_link}}
{{/if}}

---

## Voice Readiness Index

**Overall**: {{VOICE_READINESS}}/100

### Component Scores

| Component | Score | Weight |
|-----------|-------|--------|
| Schema Quality | {{SCHEMA_QUALITY}} | 25% |
| Speakable Coverage | {{SPEAKABLE_COVERAGE}} | 25% |
| FAQ TTS Compliance | {{FAQ_TTS_COMPLIANCE}} | 25% |
| Structured Data | {{STRUCTURED_DATA}} | 25% |

### Breakdown

```
Voice Readiness Index
{{VOICE_READINESS_BAR}}
{{VOICE_READINESS}}/100
```

---

## Recommendations

{{RECOMMENDATIONS}}

---

## Competitor Analysis

**Competitors Analyzed**: {{COMPETITORS_ANALYZED}}

**Average Competitor Visibility**: {{COMPETITOR_AVG_VISIBILITY}}

### Gap Analysis

{{GAP_ANALYSIS}}

---

## Next Steps

1. {{NEXT_STEP_1}}
2. {{NEXT_STEP_2}}
3. {{NEXT_STEP_3}}

---

## Technical Notes

{{#if IS_MOCK}}
> **NOTE**: This report contains mock data. Configure API keys for real metrics:
> - `PROFOUND_API_KEY` for AI Visibility, SOV, and Citation Rate
> - `SEMRUSH_API_KEY` for competitor analysis
{{/if}}

**Version**: {{VERSION}}
