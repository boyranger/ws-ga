# Repo Readiness Agent - Product Contract

## Purpose

This document locks the product-facing behavior contract for Repo Readiness Agent.

It defines:
- the intended product behavior
- the visible output shape
- the meaning of stages
- the follow-up logic
- the stopping logic for ongoing monitoring

---

## 1. Product behavior contract

The product should behave as this 4-step loop:

1. **Repo Intake**
   - accept a GitHub repository URL
2. **Signal Inspection**
   - inspect relevant repository evidence
3. **Readiness Judgment**
   - determine the current stage
4. **Founder Guidance**
   - return the most useful next actions

---

## 2. Visible output contract

Every visible report should feel like a founder decision artifact, not a raw scoring dump.

### Required sections
- **Stage**
- **Verdict**
- **Top risks**
- **Top 3 fixes**
- **Confidence**

### Optional gates
- **Demo-safe?** yes / not yet
- **Launch-ready?** yes / not yet
- **Handoff-ready?** yes / not yet

### Output principle
The output should help a founder answer:
1. What stage is this repo in?
2. Can I demo, launch, or hand this off yet?
3. What are the biggest risks?
4. What should I fix next?

---

## 3. Stage definitions

### Prototype
The repository shows early product momentum, but still has meaningful engineering gaps that make it fragile for reliable demo, launch, or handoff.

Founder interpretation:
- promising, but still risky
- not yet trustworthy for confident handoff

Typical signals:
- weak or missing tests
- little delivery structure
- limited documentation
- fragile architecture or operational setup

### MVP
The repository is usable and promising, but still has important gaps before strong handoff or confident production use.

Founder interpretation:
- good enough to show progress
- may be demoable
- still needs strengthening before deeper trust

Typical signals:
- some structure is in place
- core flows exist
- docs/tests/ops are partial, not strong
- can likely be demoed, but not fully trusted yet

### Handoff-ready
The repository shows enough structure, clarity, and supporting evidence that it can be handed to another engineer with reasonable confidence.

Founder interpretation:
- strong enough for delegation
- lower hidden-engineering-risk than earlier stages

Typical signals:
- clearer architecture
- meaningful tests or verification coverage
- useful documentation
- delivery/ops signals are present
- fewer critical blockers

---

## 4. Follow-up logic

When a previously submitted repository is checked again, compare the latest result against the previous one.

### Follow-up status values
- **Improved**
  - readiness increased, blockers reduced, or key fixes landed
- **Unchanged**
  - no meaningful change in readiness outcome
- **Still blocked**
  - major blockers remain and prevent progress toward the target state

### Stop condition values
- **Target reached**
  - the founder's target readiness/confidence state has been achieved
- **Keep monitoring**
  - the target state has not yet been reached

### Monitoring principle
The product should not notify forever.
It should keep monitoring only while the founder's target state has not yet been reached.

---

## 5. Founder intent examples

Different founders may have different targets:
- demo-focused founder -> wants to become **Demo-safe**
- launch-focused founder -> wants stronger launch readiness
- delegation-focused founder -> wants **Handoff-ready** with high confidence

This means the stopping rule should be goal-aware, not fixed forever.
