# repo_quality_scorer rubric v1

This file mirrors the scoring intent used by `repo_quality_scorer.py`.

## Dimensions

- Architecture
- Code quality
- Security
- Testing
- Documentation
- Production readiness

## Final scores

### Code Quality Score

- Architecture: 25%
- Code quality: 30%
- Security: 15%
- Testing: 20%
- Documentation: 10%

### Production Readiness Score

- Production readiness: 40%
- Security: 20%
- Testing: 20%
- Architecture: 10%
- Documentation: 10%

## Heuristic notes in v1

The current implementation is intentionally heuristic and lightweight.

Examples:
- missing tests strongly lowers Testing
- no CI lowers Production readiness
- no README caps Documentation low
- suspicious security/secret hits lower Security
- very large files lower Architecture and Code quality confidence
- Docker, env examples, migrations, and health hints help Production readiness

## Important limitation

v1 is not a substitute for deep language-specific static analysis or human review.

It is a structured repository scorer, not an absolute truth engine.
