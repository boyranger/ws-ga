# Repo Readiness Agent

Repo Readiness Agent is a hackathon-focused autonomous repo readiness product for **solo founders**.

It answers a practical founder question that most code tools do not answer clearly:

> Is this repository still a **Prototype**, already an **MVP**, or ready to be **handed off** with confidence?

Instead of stopping at raw code warnings, the agent inspects a GitHub repository, judges its engineering maturity, highlights the biggest risks, and recommends the top fixes that matter next.

---

## Why this matters

Solo founders can build software faster than ever, especially with AI coding tools.

But shipping quickly does not automatically mean a repository is ready to:
- demo safely
- launch with less risk
- hand off to an engineer or contractor

Existing tools often return lint findings, code smells, or fragmented technical diagnostics.
Repo Readiness Agent reframes that into a **founder decision artifact**.

---

## What the agent does

The founder provides a GitHub repository URL.

The agent then performs the rest of the loop autonomously:
1. **Repo Intake** - accept the repository input
2. **Signal Inspection** - inspect architecture, code quality, security, testing, documentation, and production-readiness signals
3. **Readiness Judgment** - classify the repository as `Prototype`, `MVP`, or `Handoff-ready`
4. **Founder Guidance** - return the verdict, top risks, top 3 fixes, confidence, and optional readiness gates

This is intentionally a **single-agent** product for the hackathon version.
That keeps the story, product behavior, and demo flow clear.

---

## Core output

Every founder-facing report is centered on:
- **Stage**
- **Verdict**
- **Top risks**
- **Top 3 fixes**
- **Confidence**

Optional founder-facing gates:
- **Demo-safe?**
- **Launch-ready?**
- **Handoff-ready?**

Example output shape:

```text
Stage: MVP
Verdict: This repository looks usable for demos or early users, but it still needs focused hardening before handoff.
Confidence: Medium

Top risks:
- No CI workflow was detected, so quality gates may rely on manual discipline.

Top 3 fixes:
- Add CI to run lint/typecheck/tests on every change.
```

---

## Why this is a good hackathon product

This repository is shaped to support the hackathon judging criteria:

### 1. Use Case Clarity & Impact
- narrow target user: **solo founders / indie hackers**
- clear problem: repo readiness uncertainty
- clear output: a founder decision, not only a score

### 2. Creativity & Originality
- reframes code/repo inspection into a **founder-facing readiness judgment**
- translates engineering evidence into stage, verdict, and next actions

### 3. Autonomy & Agent Behaviour
- user gives only the repo URL
- agent performs intake, inspection, judgment, and guidance without manual check selection
- optional follow-up mode compares progress over time and reports:
  - `Improved`
  - `Unchanged`
  - `Still blocked`

### 4. Technical Execution
- working CLI inspection flow
- product-layer adapter over scoring engine
- text and JSON report output
- sample outputs and calibration artifacts included

### 5. Real-World Deployability
- clear docs
- repeatable demo path
- sample outputs for low-risk presentation
- optional Telegram bot scaffold for public interaction experiments

---

## Current status

Repo Readiness Agent is **hackathon-ready** as a coherent single-agent product direction with:
- working repo inspection flow
- founder-facing report output
- follow-up comparison concept
- sample artifacts for demo and judging
- a pitch deck and demo brief in the repository

It should be described honestly as:
- **ready for hackathon demo/submission**
- **not yet a fully hardened production SaaS**

---

## Repository structure

```text
RepoReadinessAgent/
├── docs/                         # product identity, contracts, demo, pitch, runbooks
├── examples/                     # sample outputs and calibration artifacts
├── pitch_deck/                   # exported pitch deck assets, including NotebookLM PDF
├── references/                   # supporting notes and external references
├── src/repo_readiness_agent/     # product-layer code, CLI, formatter, follow-up, bot scaffold
├── tools/repo_quality_scorer/    # scoring engine, rubric, and schema
├── .env.example                  # example environment config for bot/local setup
└── requirements-bot.txt          # bot/runtime dependencies
```

---

## Installation

### Requirements

Recommended local environment:
- Python 3.11+
- `git`
- internet access for cloning and inspecting public GitHub repositories

### 1. Clone the repository

```bash
git clone https://github.com/boyranger/ws-ga.git
cd ws-ga/RepoReadinessAgent
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements-bot.txt
```

This installs the runtime dependencies for:
- CLI inspection
- Telegram bot surface
- PDF export

---

## Quick start

### 1. Inspect a repository

From `RepoReadinessAgent/`:

```bash
PYTHONPATH=src .venv/bin/python -m repo_readiness_agent.cli inspect https://github.com/pallets/flask --format text
```

### 2. Get JSON output

```bash
PYTHONPATH=src .venv/bin/python -m repo_readiness_agent.cli inspect https://github.com/pallets/flask --format json
```

### 3. Export hasil ke PDF bahasa Indonesia

```bash
PYTHONPATH=src .venv/bin/python -m repo_readiness_agent.cli inspect \
  https://github.com/pallets/flask \
  --format pdf \
  --output examples/sample_outputs/flask_product_report_id.pdf
```

### 4. Run follow-up comparison

```bash
PYTHONPATH=src .venv/bin/python -m repo_readiness_agent.cli followup \
  examples/sample_outputs/qris_payment_bot_followup_before.json \
  examples/sample_outputs/qris_payment_bot_followup_after.json \
  --format text
```

---

## Fastest demo path

If you need the quickest reliable demo flow:

1. read `docs/hackathon_submission.md`
2. read `docs/demo_script.md`
3. open `docs/demo_production_brief.md`
4. show `examples/sample_outputs/qris_payment_bot_report.txt`
5. optionally run one live `inspect` command
6. briefly show `examples/sample_outputs/qris_payment_bot_followup_result.json`
7. close with the founder decision framing

Suggested close line:

> Repo Readiness Agent turns repository evidence into a founder decision.

---

## Best artifacts to show judges

### Founder-facing sample outputs
- `examples/sample_outputs/qris_payment_bot_report.txt`
- `examples/sample_outputs/qris_payment_bot_report.json`
- `examples/sample_outputs/flask_product_report.txt`
- `examples/sample_outputs/flask_product_report.json`

### Follow-up autonomy artifacts
- `examples/sample_outputs/qris_payment_bot_followup_before.json`
- `examples/sample_outputs/qris_payment_bot_followup_after.json`
- `examples/sample_outputs/qris_payment_bot_followup_result.json`

### Calibration references
- `examples/calibration/full_stack_fastapi_template.txt`
- `examples/calibration/full_stack_fastapi_template.json`
- `examples/calibration/click.txt`
- `examples/calibration/click.json`

### Pitch assets
- `pitch_deck/repo_readiness_agent_pitch_deck.pdf`
- `pitch_deck/notebooklm/repo_readiness_agent_pitch_deck_notebooklm.pdf`
- `docs/pitch_pack.md`
- `docs/demo_production_brief.md`

---

## Product-layer implementation

Current product-layer modules:
- `src/repo_readiness_agent/contract.py` - canonical product vocabulary and report structures
- `src/repo_readiness_agent/schema.json` - canonical JSON schema for product-layer output
- `src/repo_readiness_agent/engine.py` - adapter from scorer output into founder-facing report output
- `src/repo_readiness_agent/formatter.py` - text rendering helpers
- `src/repo_readiness_agent/followup.py` - follow-up concepts and status wording
- `src/repo_readiness_agent/cli.py` - product-layer CLI entrypoint
- `src/repo_readiness_agent/bot/` - Telegram bot scaffold with SQLite storage, user tracking, and follow-up runner

The scoring engine currently lives in:
- `tools/repo_quality_scorer/repo_quality_scorer.py`

This keeps the architecture split clean:
- **scorer/tool layer** = repo inspection and evidence gathering
- **product layer** = founder-facing contract, rendering, and interaction flow

---

## Telegram bot

Repo Readiness Agent also ships with a Telegram bot surface for founder-facing usage.

### Live bot

You can try the live bot at:
- `@repoReadinessBot`

Current intended usage flow:
1. send `/start`
2. send a GitHub repo URL or use `/inspect <github_url>`
3. ask follow-up questions naturally
4. optionally track the repo for later follow-up

### Example commands

- `/start`
- `/help`
- `/inspect <github_url>`
- `/track <github_url>`
- `/myrepos`
- `/report <tracking_id>`
- `/followup <tracking_id>`
- `/untrack <tracking_id>`

### Natural language examples

- `cek repo ini https://github.com/pallets/flask`
- `apa risiko utamanya?`
- `beri prompt perbaikannya`
- `relay buat solo founder`
- `cek lagi repo yang tadi`

### Run the bot locally

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Set your Telegram token inside `.env` or export it directly:

```bash
export REPO_READINESS_TELEGRAM_BOT_TOKEN=your_bot_token_here
```

3. Start the bot:

```bash
PYTHONPATH=src .venv/bin/python -m repo_readiness_agent.bot.app
```

4. Run the scheduled follow-up runner manually:

```bash
PYTHONPATH=src .venv/bin/python -m repo_readiness_agent.bot.runner
```

5. Export PDF founder-facing output when needed:

```bash
PYTHONPATH=src .venv/bin/python -m repo_readiness_agent.cli inspect <github_url> --format pdf --output report.pdf
```

Use `.env.example` and `docs/public_telegram_bot_runbook.md` for local setup.
Do not commit real secrets.

---

## Key docs

### Product and positioning
- `docs/repo_readiness_agent_identity.md`
- `docs/repo_readiness_product_contract.md`
- `docs/scoring_model.md`
- `docs/repo_quality_scorer_hackathon_positioning.md`
- `docs/hackathon_submission.md`

### Demo and pitch
- `docs/demo_script.md`
- `docs/demo_production_brief.md`
- `docs/pitch_pack.md`
- `pitch_deck/notebooklm/repo_readiness_agent_pitch_deck_notebooklm.pdf`

### Architecture and ops
- `docs/architecture_boundaries.md`
- `docs/public_telegram_bot_architecture.md`
- `docs/public_telegram_bot_implementation_plan.md`
- `docs/public_telegram_bot_runbook.md`

---

## Honest limitations

Current limitations to be transparent about:
- scoring heuristics are still conservative in some cases
- some supporting analyzers may have environment-specific caveats
- autonomous follow-up is strong for hackathon/demo use, but still intentionally lightweight
- the product is stronger as a hackathon-ready decision tool than as a fully hardened production SaaS

That is acceptable for the current scope as long as the demo stays focused, coherent, and evidence-based.
