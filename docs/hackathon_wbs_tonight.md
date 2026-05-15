# Hackathon WBS - Tonight

Target deadline: **10:00 PM tonight**

## Objective

Deliver a clear, demoable hackathon version of **Repo Readiness Agent** that is coherent across:
- positioning
- identity
- output language
- demo flow

For the more operational execution guide with owners, dependencies, and completion criteria, see `docs/hackathon_implementation_plan.md`.


---

## Team

- **Mahdy** -> product lead, presentation lead, decision owner
- **Fauzi** -> builder teammate, parallel implementation/testing/polish
- **Clara** -> builder agent, planner, reviewer, documentation and alignment support

---

## Must-have outcomes by 10 PM

- founder-facing stage labels are aligned
- product identity is documented
- demo flow is documented
- at least one reliable demo repo/output pair exists
- submission and implementation language do not conflict

---

## Work Breakdown Structure

## Track A - Output alignment
**Goal:** make the actual product output match the hackathon story.

### Tasks
- [ ] Update `repo_quality_scorer` stage language to:
  - Prototype
  - MVP
  - Handoff-ready
- [ ] Tighten verdict text so it sounds founder-friendly
- [ ] Ensure text output emphasizes:
  - stage
  - verdict
  - top risks
  - top 3 fixes
- [ ] Re-run a sample repo and inspect the output

---

## Track B - Product identity
**Goal:** make the product agent explicit and presentable.

### Tasks
- [ ] Create `docs/repo_readiness_agent_identity.md`
- [ ] Ensure identity is distinct from Clara
- [ ] Document mission, user, boundaries, and output contract

---

## Track C - Presentation and autonomy framing
**Goal:** make the autonomy easy to explain live.

### Tasks
- [ ] Prepare a simple autonomy explanation:
  - Observe
  - Interpret
  - Judge
  - Recommend
- [ ] Prepare the short answer to: "Why is this autonomous?"
- [ ] Prepare the short answer to: "Why one agent only?"
- [ ] Prepare the short answer to: "Why is this useful for founders?"

---

## Track D - Demo preparation
**Goal:** make the product easy to show in a short presentation.

### Tasks
- [ ] Choose 1 primary demo repo
- [ ] Choose optional backup demo repo
- [ ] Capture expected example output
- [ ] Write 30-second demo flow
- [ ] Write 2-minute demo flow

---

## Track E - Verification
**Goal:** reduce demo risk.

### Tasks
- [ ] Verify the CLI still runs cleanly
- [ ] Verify one text output path
- [ ] Verify one JSON output path
- [ ] Check for confusing wording or broken fields
- [ ] Confirm no blocker in the live demo path

---

## Suggested parallel split

### Mahdy
- final scope decisions
- presentation narrative
- judging-angle refinement
- choose what to show in demo
- approve the final visible product wording
- own the live explanation of autonomy and founder value

### Fauzi
- run checks in parallel
- validate outputs on sample repos
- help test any changed implementation
- help reduce demo friction
- own scorer output alignment and verification

### Clara
- maintain scope guardrails
- update docs and artifacts
- refine wording
- support implementation review
- keep all outputs aligned with the product story

---

## Clear assignment by person

### Mahdy owns
- product framing
- final wording approval
- primary + backup demo repo choice
- pitch clarity
- autonomy explanation
- founder-value explanation

### Fauzi owns
- scorer output updates
- text/json verification
- sample run execution
- demo reliability checks
- blocker reporting

### Shared checkpoint
Before final demo prep, Mahdy and Fauzi should align on only 3 things:
1. the exact visible stage labels
2. the exact visible output sections
3. the exact demo repo to present

---

## Sequence recommendation

### First
- complete Track A and Track B

### Then
- complete Track D and Track E

### Throughout
- keep Track C ready for presentation

---

## Hard stop rule

If something does not improve:
- founder clarity
- demo quality
- single-agent usefulness
- tonight's deliverability

it should not be prioritized before 10 PM.
