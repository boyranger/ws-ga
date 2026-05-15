# Repo Readiness Agent - Architectural Boundaries

This note locks the current architectural boundaries for the hackathon v1 product layer.

## Purpose

Keep the app layer coherent while implementation grows.

The main rule is simple:
- do not let transport, product formatting, follow-up logic, and scorer integration collapse into one file

## Current source-of-truth ownership

### `tools/repo_quality_scorer/`
Canonical owner of:
- repo inspection
- heuristic scoring
- raw evidence gathering
- lower-level technical judgment inputs

### `src/repo_readiness_agent/contract.py`
Canonical owner of:
- product-facing report structures
- founder-facing report shape

### `src/repo_readiness_agent/engine.py`
Canonical owner of:
- calling the scorer engine
- translating scorer output into product-layer report inputs
- founder-gate derivation from scorer results

### `src/repo_readiness_agent/followup.py`
Canonical owner of:
- follow-up vocabulary
- follow-up comparison rules
- monitoring stop-condition logic

### `src/repo_readiness_agent/formatter.py`
Canonical owner of:
- rendering founder-facing output text

### `src/repo_readiness_agent/cli.py`
Canonical owner of:
- CLI argument handling
- orchestration of product-layer execution flow

## Boundary rules

- `cli.py` should orchestrate, not own business rules
- `formatter.py` should render, not inspect repositories
- `followup.py` should own monitoring comparison rules
- `engine.py` should adapt scorer results, not become a dumping ground for every product concern
- `contract.py` should remain the single source of truth for product report structures

## Why this matters

This keeps:
- feature ownership clearer
- source of truth cleaner
- product logic easier to evolve
- follow-up behavior reusable from future entrypoints

## Hackathon constraint

Do not over-abstract.
This repo is still intentionally single-agent and compact.
The goal is not theoretical purity; the goal is to avoid needless mixing while keeping the implementation demoable.
