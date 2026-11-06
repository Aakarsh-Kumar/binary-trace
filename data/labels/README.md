# Gold Labels Directory (US-35)

This directory contains human-adjudicated gold standard labels and evaluation manifests for measuring system precision, recall, and false flag rate (FFR).

## Files

- `TEMPLATE.csv`: Blank CSV with the official 12-column header row.
- `sample_5.csv`: A 5-row schema and validation fixture derived from pilot submissions.
- `CORPUS_STATE.json`: Local audit manifest tracking the 60 evaluation corpus submissions (gitignored).

## Workflow

1. Read the full annotation protocol in [`docs/annotation_guideline.md`](../../docs/annotation_guideline.md).
2. Choose an annotation mode:
   - **Mode A**: Independent dual human annotation followed by adjudication on disagreement.
   - **Mode B**: Agent bootstrap pass (`compliance-review labels bootstrap`) followed by a 25% stratified human audit.
3. Validate and compute metrics against evaluation runs:
   ```bash
   compliance-review metrics --labels data/labels/gold_labels.csv --out data/labels/metrics_report.json
   ```
