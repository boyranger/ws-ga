# repo_quality_scorer - Guideline & Scope v1

> Hackathon scope note: for founder-facing hackathon positioning and scope guardrails, also see `docs/repo_quality_scorer_hackathon_positioning.md`.

## Purpose

`repo_quality_scorer` is a repository-level evaluation tool for scoring code quality and production readiness from a GitHub repository URL.

For the hackathon version, the preferred outward-facing framing is:
- **Repo Readiness Agent**
- primary user: **solo founder / indie hacker**
- core job: determine whether a repo is still a Prototype, already an MVP, or ready for handoff

It is designed to sit above low-level analyzers such as `code-quality-check`.

Positioning:

- `code-quality-check` -> rule engine / static signal provider
- `repo_quality_scorer` -> repository comprehension, scoring, and verdict layer

The goal is not only to detect code smells, but to assess the repository as an engineering artifact:

- source code quality
- architecture quality
- testing maturity
- documentation quality
- security posture
- operational / production readiness

## Primary Outputs

The tool must produce:

- **Code Quality Score**
- **Production Readiness Score**
- **Maturity Level**
- **Verdict**
- per-dimension breakdown
- evidence-backed reasoning
- key risks and improvement priorities

### Required dimensions

- Architecture
- Code quality
- Security
- Testing
- Documentation
- Production readiness

## Input

Minimum input:

- GitHub repository URL

Optional input:

- branch
- commit / ref
- subdirectory
- scoring strictness (`relaxed`, `balanced`, `strict`)
- language hint
- output format (`text`, `json`, or both)

## Output Contract

Human-readable output should include:

- repository URL
- code quality score
- production readiness score
- maturity level
- verdict
- confidence level
- per-dimension scores
- strengths
- risks
- red flags
- top improvement priorities

Example shape:

```text
Repo: https://github.com/example/project

Code Quality Score: 7.4 / 10
Production Readiness Score: 6.1 / 10
Confidence: Medium

Breakdown:
- Architecture: 8.0
- Code quality: 7.3
- Security: 6.4
- Testing: 3.2
- Documentation: 8.1
- Production readiness: 5.9

Strengths:
- ...

Risks:
- ...

Red flags:
- ...

Top improvements:
1. ...
2. ...
3. ...
```

Machine-readable output should expose the same fields in JSON, including the input parameters used for the scoring run.

## Non-Goals for v1

To keep v1 focused, the tool should **not** try to do all of the following yet:

- execute full application runtime flows for every repo
- measure true test coverage across all languages
- run enterprise-grade dependency CVE audits
- benchmark runtime performance
- generate automatic fixes
- post PR comments or act as a GitHub bot
- guarantee language-complete analysis for every ecosystem

## Scope v1

### Core workflow

1. accept a GitHub repository URL
2. clone or fetch the repository locally
3. detect ecosystem / language / framework signals
4. inspect important files and directory structure
5. run applicable analyzers
6. score each quality dimension
7. compute final scores
8. render a report in text and/or JSON

### Evidence sources

At minimum, the tool should inspect:

- repository root structure
- source tree
- test tree
- README
- package manifests (`package.json`, `pyproject.toml`, `go.mod`, etc.)
- CI config (`.github/workflows/*`)
- Docker / deploy files
- environment examples
- migration files
- application entrypoints
- test config files

### External analyzers

`repo_quality_scorer` should use `code-quality-check` as a backbone where applicable.

In v1:

- use `code-quality-check` for JS/TS/Go repositories when relevant
- keep analyzer integration optional and non-blocking when unsupported
- combine analyzer findings with repository-level inspection

## Dimension Rubric

### 1. Architecture

Measures:

- separation of concerns
- modularity
- layering
- coupling and cohesion
- complexity hotspots
- oversized files/functions
- dependency direction sanity

Signals may come from:

- repository structure
- source layout
- `code-quality-check` categories such as structural, god functions, deep nesting, CQS, LoD, and Sandi Metz rules

### 2. Code quality

Measures:

- naming clarity
- dead code
- debug artifacts
- import hygiene
- formatting consistency
- maintainability smells
- type-safety / static-analysis discipline

Signals may come from:

- `code-quality-check` semantic and hygiene findings
- formatter/typecheck results
- unused-code detection
- source inspection

### 3. Security

Measures:

- unsafe patterns
- secret handling
- auth and webhook safety
- insecure defaults
- exposure of internal errors
- dependency/security smells

Signals may come from:

- `code-quality-check` security findings
- config inspection
- API/webhook inspection
- deployment/config patterns

### 4. Testing

Measures:

- presence of tests
- breadth of test coverage by feature area
- unit vs integration vs e2e balance
- test meaningfulness
- CI execution of tests

Important note:

`code-quality-check` can help detect weak tests, but testing maturity must also be assessed structurally.

### 5. Documentation

Measures:

- README completeness
- setup instructions
- configuration docs
- API docs
- deployment docs
- troubleshooting notes

### 6. Production readiness

Measures:

- CI/CD presence
- environment/config discipline
- migration discipline
- deployment packaging
- health checks
- observability/logging
- resilience and retry/idempotency patterns
- operational clarity

This dimension must go beyond static style/linting.

## Score Model v1

### Code Quality Score

Recommended weights:

- Architecture: 25%
- Code quality: 30%
- Security: 15%
- Testing: 20%
- Documentation: 10%

Formula:

```text
Code Quality Score =
  (Architecture * 0.25) +
  (Code quality * 0.30) +
  (Security * 0.15) +
  (Testing * 0.20) +
  (Documentation * 0.10)
```

### Production Readiness Score

Recommended weights:

- Production readiness: 40%
- Security: 20%
- Testing: 20%
- Architecture: 10%
- Documentation: 10%

Formula:

```text
Production Readiness Score =
  (Production readiness * 0.40) +
  (Security * 0.20) +
  (Testing * 0.20) +
  (Architecture * 0.10) +
  (Documentation * 0.10)
```

## Scoring Principles

The scorer should not rely on vibes.

Base rules:

- use evidence from actual files when possible
- cap scores when critical gaps exist
- allow boosts only when evidence supports them
- be explicit when confidence is low
- separate repo-level facts from interpretation

### Suggested caps / guardrails

Examples:

- no tests -> Testing should usually cap at 2.5
- no CI -> Production readiness penalty
- no README -> Documentation should usually cap at 3
- critical security finding -> Security cap or severe penalty
- formatter/typecheck failures -> Code quality cap
- clear modular structure -> Architecture boost
- ad-hoc migrations/runtime schema hacks -> Production readiness penalty

## Confidence Levels

The tool should report confidence, for example:

- **High** -> key files present, analyzers ran, enough evidence collected
- **Medium** -> most important files found, some analyzers unavailable
- **Low** -> sparse repo, unsupported ecosystem, or limited evidence

## Suggested Tool Layout

Planned workspace location:

```text
tools/repo_quality_scorer/
├── README.md
├── repo_quality_scorer.py   # or .js depending on chosen runtime
├── rubric.md
├── templates/
└── analyzers/
```

Suggested responsibilities:

- `repo_quality_scorer.*` -> orchestration
- `rubric.md` -> scoring rubric snapshot used by the tool
- `analyzers/` -> adapters to `code-quality-check` and future ecosystem analyzers
- `templates/` -> text/json report rendering helpers

## v1 Implementation Notes

Recommended build order:

1. write and freeze rubric + output schema
2. implement repo fetch + file discovery
3. implement repo inspection for key files
4. integrate `code-quality-check`
5. implement per-dimension scoring
6. emit text + JSON reports
7. test on known repositories

## First Repositories for Calibration

Use a small set of known repos to calibrate scoring:

- a clean small repo
- a messy repo with obvious smells
- a repo with strong docs but weak tests
- a repo with good code but poor ops readiness
- Mahdy's sample repos used during development

## Design Constraint

The tool must prefer grounded scoring over inflated praise.

If a repository is weak in testing, security, or production discipline, the report should say so plainly.
