# Repo Readiness Agent Plan

## Purpose of this document

This document turns the current product direction into an execution plan.

It exists to prevent scope creep and keep implementation aligned with the hackathon goal.

This is the planning companion to:
- `docs/repo_quality_scorer_hackathon_positioning.md`
- `docs/hackathon_submission.md`
- `docs/clara_identity.md`

---

## Product decision

For the hackathon version, the product should use **one product agent only**:

# Repo Readiness Agent

This is intentional.

We are not building a multi-agent repo analysis platform for the hackathon version.

We are building a single, specialized, founder-facing autonomous agent.

---

## Why one agent is enough

### Clarity

One user, one problem, one agent, one output.

This makes the product easy to explain and easy to demo.

### Focus

The user does not need multiple agents. The user needs one trustworthy answer:
- what stage is this repo in?
- can I demo, launch, or hand it off yet?
- what should I fix next?

### Better demoability

A single-agent flow is cleaner:
1. input GitHub URL
2. inspect repo
3. return stage + verdict + fixes

### Strong enough autonomy

Autonomy does not require multi-agent orchestration.

A single agent can still be clearly autonomous if it:
- chooses what signals matter
- inspects the repository independently
- synthesizes findings into a judgment
- prioritizes next actions without manual step-by-step prompting

---

## Identity split

### Clara

Clara is the **builder agent**.

Responsibilities:
- product framing
- scope control
- implementation
- docs and artifacts
- keeping product and implementation aligned

### Repo Readiness Agent

Repo Readiness Agent is the **product agent**.

Responsibilities:
- inspect a GitHub repository
- judge engineering maturity
- classify repo stage
- provide founder-facing verdict and fixes

### repo_quality_scorer

`repo_quality_scorer` is the **analysis engine / backbone tool**.

Responsibilities:
- collect technical signals
- compute scores and evidence
- support the product agent's judgment

---

## Product architecture

### Layer 1 - Builder layer
- Clara

### Layer 2 - Product layer
- Repo Readiness Agent

### Layer 3 - Engine layer
- repo_quality_scorer
- code-quality-check where applicable

Simple model:

**Clara builds** -> **Repo Readiness Agent presents the product behavior** -> **repo_quality_scorer powers the analysis**

---

## Primary user

**Solo founder / indie hacker**

Not the generic developer market.

The product should optimize for the founder who built quickly and now wants a reliable readiness judgment.

---

## Core problem

The founder can build fast, but cannot confidently judge whether the repo is:
- still a prototype
- already an MVP
- ready to hand off to an engineer

The product solves repo readiness uncertainty.

---

## Core job-to-be-done

> Tell me whether my repo is still a Prototype, already an MVP, or ready for handoff — and what I should fix next.

If a feature does not strengthen this job, it should not be prioritized for the hackathon build.

---

## Core product behavior

Repo Readiness Agent should do four things well:

### 1. Inspect
- accept a GitHub URL
- clone and inspect the repository autonomously

### 2. Judge
- review signals across:
  - architecture
  - code quality
  - security
  - testing
  - documentation
  - production readiness

### 3. Classify
- return one stage:
  - Prototype
  - MVP
  - Handoff-ready

### 4. Guide
- return:
  - verdict
  - top risks
  - top 3 fixes

If these four behaviors work, the hackathon product is strong enough.

---

## Phase plan

## Phase 1 - Lock framing and scope

### Goal
Make sure product language, user, and identity are fixed.

### Deliverables
- Clara identity defined
- Repo Readiness Agent positioning defined
- hackathon submission doc written
- single-agent decision recorded

### Status
Mostly complete.

---

## Phase 2 - Align tool output with product language

### Goal
Make the actual tool speak the same language as the pitch.

### Required changes
- stage labels should prefer:
  - Prototype
  - MVP
  - Handoff-ready
- verdict language should be founder-friendly
- outputs should clearly emphasize:
  - stage
  - verdict
  - top risks
  - top 3 fixes

### Definition of done
A demo output can be shown directly in hackathon context without translation.

---

## Phase 3 - Define product agent identity

### Goal
Make Repo Readiness Agent a first-class product identity.

### Deliverable
- `docs/repo_readiness_agent_identity.md`

### Should include
- role
- user
- mission
- tone
- boundaries
- expected outputs

---

## Phase 4 - Improve explainability

### Goal
Help founders understand not only the stage, but why.

### Candidate additions
- founder summary
- handoff blockers
- launch blockers
- why this stage
- why these fixes first

### Definition of done
The report is understandable by a founder, not only by an engineer.

---

## Phase 5 - Demo pack

### Goal
Make the product easy to show.

### Deliverables
- `docs/demo_script.md`
- selected sample repos
- ideal demo outputs

### Demo flow
1. paste GitHub URL
2. Repo Readiness Agent inspects repo
3. founder sees stage, verdict, risks, and fixes

---

## Phase 6 - Final polish

### Goal
Tighten what already exists instead of expanding the scope.

### Possible polish items
- wording cleanup
- better sample outputs
- consistent naming everywhere
- final founder-friendly output review

---

## In scope for hackathon build

- one product agent
- GitHub URL input
- repo inspection
- scoring-backed judgment
- Prototype / MVP / Handoff-ready classification
- verdict
- top risks
- top 3 fixes
- founder-friendly explanation
- demo-ready output

---

## Out of scope for hackathon build

Do not prioritize these now:
- multi-agent architecture
- autonomous code modification
- PR comments / GitHub bot workflows
- enterprise dashboards
- compliance workflows
- full dependency vulnerability audit
- broad persona switching
- deep ecosystem-complete static analysis
- project management features

---

## Decision checkpoints

Before building something new, ask:

1. Does this help a solo founder decide whether to demo, launch, or hand off the repo?
2. Does this make the single agent more useful, more autonomous, or more understandable?
3. Can this still be explained in a 30-second demo?
4. Is this improving the core loop, or just expanding the surface area?

If the answer is weak, do not prioritize it for hackathon scope.

---

## Definition of done for the hackathon product

The product is ready enough when all of the following are true:
- the scope is stable
- the output language matches the positioning
- the product agent identity is documented
- the repo review output is founder-friendly
- the submission artifact is ready
- the demo flow is ready
- at least 1-2 sample repos are usable for demo

---

## Current recommendation

Next implementation priority:

1. align `repo_quality_scorer` output with Prototype / MVP / Handoff-ready
2. define `docs/repo_readiness_agent_identity.md`
3. create demo script artifact
4. polish sample outputs and submission consistency
