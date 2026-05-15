# RepoReadinessAgent

RepoReadinessAgent is a hackathon-focused autonomous repo readiness product for solo founders.

It helps answer a founder-level question:
- is this repository still a **Prototype**
- already an **MVP**
- or **Handoff-ready**

And it highlights the top risks and next fixes that matter most.

## What it does

A founder submits a GitHub repository.

Repo Readiness Agent then:
1. inspects the repository
2. judges its current readiness stage
3. highlights the biggest risks
4. recommends the top fixes that matter next
5. can compare progress again later through a follow-up loop

## One-line summary

An autonomous repo readiness agent that reviews a GitHub repository and gives a founder-facing judgment on whether it is still a Prototype, already an MVP, or ready for handoff.

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

## Core output

Every product-facing report aims to return:
- Stage
- Verdict
- Top risks
- Top 3 fixes
- Confidence

Optional founder-facing gates:
- Demo-safe?
- Launch-ready?
- Handoff-ready?

## Current status

This repo is being prepared as the publishable product repository for the hackathon submission.

The current implementation backbone lives in `tools/repo_quality_scorer/`, while the outward-facing product definition lives in `docs/`.

## Quick demo path

If you need the fastest walkthrough:
1. read `docs/hackathon_submission.md`
2. read `docs/demo_script.md`
3. inspect `examples/sample_outputs/qris_payment_bot_report.txt`
4. inspect `examples/sample_outputs/qris_payment_bot_report.json`
5. inspect the follow-up demo artifacts in `examples/sample_outputs/`

## Key docs

- `docs/repo_readiness_agent_identity.md`
- `docs/repo_readiness_product_contract.md`
- `docs/scoring_model.md`
- `docs/demo_script.md`
- `docs/pitch_pack.md`
- `docs/hackathon_submission.md`
- `docs/repo_quality_scorer_hackathon_positioning.md`
- `docs/architecture_boundaries.md`

## Product-layer implementation status

The product layer now has a working CLI adapter on top of the scorer engine.

Current product-layer modules:
- `src/repo_readiness_agent/contract.py` - product-facing report structures and canonical vocabulary
- `src/repo_readiness_agent/schema.json` - canonical JSON schema for product-layer report output
- `src/repo_readiness_agent/engine.py` - adapter from scorer output into founder-facing product output
- `src/repo_readiness_agent/formatter.py` - text rendering helpers
- `src/repo_readiness_agent/followup.py` - follow-up status and stop-condition concepts
- `src/repo_readiness_agent/cli.py` - product-layer CLI entrypoint

Example run:
- `PYTHONPATH=src python3 -m repo_readiness_agent.cli https://github.com/owner/repo`
- `PYTHONPATH=src python3 -m repo_readiness_agent.cli https://github.com/owner/repo --format json`

## Demo artifacts already in repo

- `examples/sample_outputs/qris_payment_bot_report.txt`
- `examples/sample_outputs/qris_payment_bot_report.json`
- `examples/sample_outputs/qris_payment_bot_followup_before.json`
- `examples/sample_outputs/qris_payment_bot_followup_after.json`
- `examples/sample_outputs/qris_payment_bot_followup_result.json`
