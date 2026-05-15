# Repo Readiness Agent - Scoring Model

## Purpose

This document explains the scoring model behind Repo Readiness Agent in product-facing language.

It exists so the scoring logic is understandable not only to builders, but also to judges, founders, and collaborators.

---

## Why a scoring model exists

Repo Readiness Agent does not make readiness judgments from a single signal.

Instead, it inspects multiple engineering dimensions and combines them into a clearer founder-facing conclusion:
- is this repo still a **Prototype**
- already an **MVP**
- or **Handoff-ready**

The scoring model helps the product stay:
- structured
- explainable
- consistent
- demoable

Important: the scoring model exists to support the readiness judgment, not to replace it.

---

## Core scoring dimensions

The current model uses 6 dimensions:

### 1. Architecture
This looks at whether the repository shows healthy structure.

Examples of signals:
- clear project layout
- sensible separation of concerns
- not excessively chaotic or oversized structure
- supporting files that suggest maintainability

### 2. Code quality
This looks at whether the codebase appears reasonably clean and maintainable.

Examples of signals:
- code hygiene patterns
- maintainability hints
- absence of obvious problematic patterns
- supporting analyzer findings where applicable

### 3. Security
This looks for warning signs that reduce trust in the repository.

Examples of signals:
- suspicious secret exposure patterns
- insecure defaults
- code/config patterns that deserve manual review

### 4. Testing
This looks at whether the repository shows evidence of meaningful verification.

Examples of signals:
- presence of tests
- structure for automated validation
- signs that core flows can be checked reliably

### 5. Documentation
This looks at whether the project is understandable to someone other than the original builder.

Examples of signals:
- README presence and usefulness
- setup guidance
- environment or usage explanation
- clarity that helps handoff

### 6. Production readiness
This looks at whether the repository shows signs of delivery maturity.

Examples of signals:
- CI/CD hints
- Docker/deployment support
- environment examples
- migrations / health / operational signals
- repo evidence that suggests more than a fragile prototype

---

## Final output scores

The current engine computes 2 higher-level scores.

### Code Quality Score
This score emphasizes engineering quality in the implementation itself.

Current weighting:
- Architecture: 25%
- Code quality: 30%
- Security: 15%
- Testing: 20%
- Documentation: 10%

### Production Readiness Score
This score emphasizes whether the repository looks ready for stronger delivery confidence.

Current weighting:
- Production readiness: 40%
- Security: 20%
- Testing: 20%
- Architecture: 10%
- Documentation: 10%

---

## How scoring connects to stage judgment

Scores do not exist for their own sake.

They support the founder-facing readiness judgment.

A strong product explanation is:
- dimensions provide evidence
- scores summarize patterns
- the stage converts that evidence into a founder-usable decision

### Prototype
Typical meaning:
- promising early build
- still fragile
- meaningful gaps remain in tests, docs, delivery structure, or reliability

### MVP
Typical meaning:
- usable and demoable foundation
- meaningful progress exists
- still not fully strong for confident handoff or production trust

### Handoff-ready
Typical meaning:
- enough structure and evidence exist for another engineer to take over with reasonable confidence
- fewer critical blockers remain
- docs/tests/ops signals are materially stronger

The exact stage judgment should combine score patterns, evidence, and practical interpretation.

This is why Repo Readiness Agent should not be framed as only a score engine. It is a judgment product built on top of scoring.

---

## Important product principle

Repo Readiness Agent should not feel like “just a score calculator”.

The real product value is:
1. inspect repository evidence
2. evaluate multiple dimensions
3. make a clear readiness judgment
4. explain the top risks
5. recommend the top next fixes

The scoring model supports that judgment. It is not the product by itself.

---

## Supporting technical layer

The current implementation backbone lives in:
- `tools/repo_quality_scorer/repo_quality_scorer.py`
- `tools/repo_quality_scorer/rubric.md`
- `tools/repo_quality_scorer/schema.json`

Where useful, lower-level analyzers such as `code-quality-check` may also contribute code-quality-related signals.

---

## Current limitation

This model is intentionally lightweight for hackathon v1.

It is designed to be:
- understandable
- practical
- easy to demo
- good enough for founder decision support

It is not yet a substitute for deep language-specific static analysis, full security review, or human engineering due diligence.
