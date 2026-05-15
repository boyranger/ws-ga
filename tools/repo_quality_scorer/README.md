# repo_quality_scorer

A lightweight repository-level scorer for:
- code quality
- production readiness

It accepts a GitHub repository URL or local repository path, inspects the repository, optionally uses `code-quality-check` as a backbone analyzer, and produces a structured score report.

## Status

Early v1 implementation.

## Files

- `repo_quality_scorer.py` - CLI scorer
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

## Current behavior

The scorer currently:
- clones the repository if a GitHub URL is provided
- detects simple ecosystem signals
- inspects source/test/doc/deploy/config hints
- scans for a small set of security/secret/debug patterns
- computes 6 dimension scores
- computes:
  - Code Quality Score
  - Production Readiness Score
- renders text or JSON

## Current limitations

- heuristics are intentionally simple in v1
- language support is broad but shallow
- `code-quality-check` integration is best-effort
- production readiness is estimated from repository evidence, not runtime validation

## Source of truth

See:
- `docs/repo_quality_scorer_guideline.md`
- `tools/repo_quality_scorer/rubric.md`
