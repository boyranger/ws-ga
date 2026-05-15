# repo_quality_scorer

A lightweight repository-level scorer for:
- code quality
- production readiness

It accepts a GitHub repository URL or local repository path, inspects the repository, optionally uses `code-quality-check` as a backbone analyzer, and produces a structured score report.

## Status

Early v1 implementation, now with:
- versioned JSON output
- maturity classification
- verdict text
- configurable scoring inputs

## Files

- `repo_quality_scorer.py` - CLI scorer
- `schema.json` - JSON output contract
- `rubric.md` - scoring rubric snapshot
- `README.md` - usage notes

## Usage

### Score a GitHub repository

```bash
python3 tools/repo_quality_scorer/repo_quality_scorer.py https://github.com/mahdyarief/qris-payment-bot
```

### Score a local repository

```bash
python3 tools/repo_quality_scorer/repo_quality_scorer.py /path/to/repo
```

### Output JSON

```bash
python3 tools/repo_quality_scorer/repo_quality_scorer.py https://github.com/mahdyarief/qris-payment-bot --format json
```

### Output both text and JSON

```bash
python3 tools/repo_quality_scorer/repo_quality_scorer.py https://github.com/mahdyarief/qris-payment-bot --format both
```

### Use strict mode

```bash
python3 tools/repo_quality_scorer/repo_quality_scorer.py https://github.com/mahdyarief/qris-payment-bot --strictness strict
```

### Score a subdirectory

```bash
python3 tools/repo_quality_scorer/repo_quality_scorer.py /path/to/repo --subdir packages/api
```

### Override language hint

```bash
python3 tools/repo_quality_scorer/repo_quality_scorer.py /path/to/repo --language-hint TypeScript
```

## JSON contract

The JSON output now includes:
- `schema_version`
- `verdict`
- `maturity_level`
- stable top-level score fields
- `inputs` for run parameters
- `facts` for raw repository evidence

Schema reference:
- `tools/repo_quality_scorer/schema.json`

## Current behavior

The scorer currently:
- clones the repository if a GitHub URL is provided
- optionally scores a specific subdirectory
- supports `relaxed`, `balanced`, and `strict` scoring modes
- detects simple ecosystem signals
- inspects source/test/doc/deploy/config hints
- scans for a small set of security/secret/debug patterns
- computes 6 dimension scores
- computes:
  - Code Quality Score
  - Production Readiness Score
- classifies output into a maturity level and verdict
- renders text, JSON, or both
- exposes a versioned JSON contract via `schema.json`

## Current limitations

- heuristics are intentionally simple in v1
- language support is broad but shallow
- `code-quality-check` integration is best-effort
- production readiness is estimated from repository evidence, not runtime validation
- verdicts are calibrated heuristically, not yet benchmarked against a large corpus

## Source of truth

See:
- `docs/repo_quality_scorer_guideline.md`
- `tools/repo_quality_scorer/rubric.md`
- `tools/repo_quality_scorer/schema.json`
