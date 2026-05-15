# RepoReadinessAgent

RepoReadinessAgent is a hackathon-focused autonomous repo readiness product for solo founders.

It helps answer a founder-level question:
- is this repository still a **Prototype**
- already an **MVP**
- or **Handoff-ready**

And it highlights the top risks and next fixes that matter most.

## Current repository structure

- `docs/` - product identity, contract, scoring model, demo script, positioning, and hackathon-facing docs
- `tools/repo_quality_scorer/` - the current scoring engine and schema
- `src/repo_readiness_agent/` - product-layer code and output contracts for Repo Readiness Agent
- `examples/` - sample outputs for demo and explanation
- `references/` - supporting notes and external references if needed

## Initial product loop

1. **Repo Intake**
2. **Signal Inspection**
3. **Readiness Judgment**
4. **Founder Guidance**

## Current status

This repo is being prepared as the publishable product repository for the hackathon submission.

The current implementation backbone lives in `tools/repo_quality_scorer/`, while the outward-facing product definition lives in `docs/`.

## Key docs

- `docs/repo_readiness_agent_identity.md`
- `docs/repo_readiness_product_contract.md`
- `docs/scoring_model.md`
- `docs/demo_script.md`
- `docs/hackathon_submission.md`
- `docs/repo_quality_scorer_hackathon_positioning.md`

## Initial source skeleton

- `src/repo_readiness_agent/contract.py` - product-facing report structures
- `src/repo_readiness_agent/formatter.py` - text rendering helpers
- `src/repo_readiness_agent/followup.py` - follow-up status and stop-condition concepts
- `src/repo_readiness_agent/cli.py` - future product-layer CLI entrypoint
