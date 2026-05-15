---
name: repo-architecture-guardrails
description: Use when designing, reviewing, or refactoring RepoReadinessAgent code so feature ownership, source of truth, dependency direction, and follow-up/product boundaries stay coherent without overengineering.
---

# Repo Architecture Guardrails

Use this skill when working on RepoReadinessAgent application structure, product-layer wiring, scorer integration boundaries, or follow-up/report ownership.

## What this skill is for

This skill keeps RepoReadinessAgent code standard and coherent by enforcing:
- clear feature ownership
- single source of truth for rules and contracts
- thin entrypoints
- product-layer separation from lower-level scorer logic
- proportional refactors only

## Default workflow

1. Identify the touched scope.
2. Ask which file should be the canonical owner of the rule, contract, or behavior.
3. Check whether transport/orchestration/rendering/business logic are getting mixed.
4. Extract the smallest stable seam needed to restore coherence.
5. Preserve behavior; avoid broad rewrites.
6. Verify the product CLI or affected path still works.

## RepoReadinessAgent boundary defaults

Use these defaults unless there is a strong reason to change them:

- `tools/repo_quality_scorer/` owns repo inspection and heuristic scoring.
- `src/repo_readiness_agent/contract.py` owns product-facing report structures.
- `src/repo_readiness_agent/engine.py` owns scorer invocation and translation into product-facing inputs.
- `src/repo_readiness_agent/followup.py` owns monitoring vocabulary and comparison logic.
- `src/repo_readiness_agent/formatter.py` owns rendering.
- `src/repo_readiness_agent/cli.py` owns CLI orchestration only.

## Escalation guide

### Critical
Escalate when a boundary violation risks correctness, safety, or inconsistent founder-facing decisions across entrypoints.

### Warning
Escalate when a change introduces source-of-truth splits, duplicated rules, feature leakage, or a new dumping-ground module.

### Note
Use notes for small boundary improvements that are worth fixing soon but do not currently create major product risk.

## RepoReadinessAgent-specific checks

Before finalizing a change, check:
- Is one file clearly the owner of the changed rule or contract?
- Did CLI stay thin?
- Did formatter avoid business rules?
- Did follow-up logic stay out of rendering and transport code?
- Did scorer-specific heuristics stay in the scorer layer unless they are truly product translation concerns?
- Did the change avoid introducing a vague `utils` dumping ground?

## References

Read `references/architectural-boundaries.md` when you need the deeper review lens, example findings, or principle-by-principle guidance.
