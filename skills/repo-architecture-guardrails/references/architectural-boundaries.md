# Architectural Boundaries, Feature Ownership & Source of Truth

## Purpose

Protect architectural coherence in touched code by reinforcing clear feature ownership, single sources of truth, disciplined dependency direction, and consistent business-rule enforcement across entrypoints.

This category is the default architecture lens for the skill. Use it to evaluate architectural fit without turning small changes into broad rewrites.

## Covers

- Feature-Based Architecture (FBA)
- Single Source of Truth (SSOT)
- SOLID
- Hexagonal Architecture
- Octagonal Architecture

## Look For

- feature code grouped by use-case or business capability instead of being scattered mainly by technical layer
- one canonical owner for rules, constants, schemas, mappings, and derived policy
- responsibilities separated so modules have one clear reason to change
- core policy depending on boundaries or abstractions instead of concrete framework or IO details
- business rules implemented in reusable application or domain seams rather than copied into controllers, jobs, workers, views, or adapters
- adapters translating external shapes at boundaries instead of leaking transport, ORM, or UI details inward
- alternate entrypoints reusing the same invariants, authorization, and validation rules
- shared modules remaining truly shared instead of becoming feature-specific dumping grounds

## Escalate When

- **Critical**: architectural violation creates correctness, safety, hidden-failure, or severe regression risk
- **Warning**: touched code introduces or deepens source-of-truth splits, boundary leakage, duplicated business rules across entrypoints, unstable feature ownership, or concrete-dependency coupling that materially harms maintainability
- **Note**: architecture direction could be improved, but current touched scope remains safe and understandable

## Good Signs

- one feature can be changed mostly within its own boundary
- rules and mappings have an obvious canonical owner
- core use cases can be reused from multiple entrypoints
- controllers, routes, views, jobs, and adapters stay thin
- domain or application logic can be exercised without real infrastructure where architecture style expects that
- dependency direction points inward toward policy, not outward toward frameworks

## Review Lens By Principle

### Feature-Based Architecture (FBA)

Look for:
- feature owns its UI, logic, tests, schema, and constants unless sharing is genuinely cross-feature
- cross-feature interaction happens through explicit seams
- unrelated features do not import each other's internals

Flag when:
- routine feature change requires scattered edits across unrelated folders with no explicit boundary reason
- `shared` or `utils` contains feature-specific business logic
- feature internals are imported directly by unrelated features

### Single Source of Truth (SSOT)

Look for:
- one canonical owner for enums, rules, mappings, schemas, and access policy
- derived representations generated or reused from canonical definitions
- UI, API, storage, and tests agree on names and shapes

Flag when:
- same rule or enum is hand-copied across layers
- validation rules differ by entrypoint without explicit reason
- docs, config, and types drift because more than one file claims authority

### SOLID

Look for:
- single responsibility in modules, classes, and functions
- extension seams instead of repetitive edits across many callers
- substitutable implementations that preserve contract expectations
- narrow interfaces that do not force unused data or methods
- policy depending on abstractions or boundaries rather than concrete infrastructure

Flag when:
- one unit mixes validation, orchestration, persistence, formatting, and transport concerns
- every new variant requires editing many conditionals across callers
- implementation details leak into contracts and break substitutability
- wide interfaces force consumers to depend on what they do not use
- domain or application logic imports concrete HTTP, ORM, queue, or UI mechanisms directly

### Hexagonal Architecture

Look for:
- business logic isolated from frameworks, transport, ORM, and UI details
- ports expressed in domain terms
- adapters translating edge concerns before calling inward
- application or use-case layer coordinating flow without hiding rules inside controllers or repositories

Flag when:
- route/controller/view contains business rules
- transport DTOs or ORM entities drive domain decisions directly
- infrastructure details determine core API shape

### Octagonal Architecture

Look for:
- multiple entrypoint types using the same core use-case logic
- validation, authorization, and invariants enforced consistently across HTTP, jobs, events, cron, and integrations
- one adapter not reaching into another adapter's internals

Flag when:
- same business rule is reimplemented separately in HTTP handlers, workers, cron jobs, or event consumers
- alternate entrypoints bypass invariants or authorization checks
- integration path shortcuts around domain or application rules

## Rewrite Guidance

- preserve behavior while moving duplicated policy toward one canonical owner
- extract smallest stable seam that separates policy from transport or IO detail
- reuse existing use-case or application boundaries before inventing new abstraction layers
- narrow shared modules back to truly shared concerns
- keep adapters thin and translation-focused
- fix touched-scope violations without using architecture as justification for unrelated rewrites

## Avoid Overreach

Do not demand full feature reorganization, complete ports-and-adapters adoption, or theoretical SOLID purity when the task is small. Improve touched boundaries materially, but keep the change proportional.

## Example Findings

- `Warning — src/orders/http/create-order.ts:L20-L97 — Source-of-truth split. HTTP handler redefines discount eligibility already enforced in order application service. Reuse service rule and remove duplicate branch.`
- `Warning — src/users/shared/role-utils.ts:L1-L68 — Feature ownership weak. Shared module contains user-specific authorization policy. Move canonical rule into users feature boundary and leave shared layer generic.`
- `Critical — src/billing/jobs/retry-charge.ts:L40-L121 — Octagonal consistency broken. Job path bypasses invariant checks required by API path, risking invalid charges. Route retry through same application use case.`

## Evidence Base

- **Primary evidence type:** Expert heuristic / design guidance + mixed empirical support
- **Why this category exists:** Clear feature ownership, canonical rule ownership, and boundary discipline reduce drift, duplication, and multi-entrypoint inconsistency.
- **Support:** Domain-driven and clean/hexagonal architecture literature strongly supports explicit boundaries, inward dependency direction, and use-case reuse across adapters. See [AR1], [AR2], [AR3], [AR4], [GF1].
- **Limitations:** Evidence for architecture style is often heuristic and context-sensitive rather than universally empirical. Use this category to improve touched-scope coherence, not to force wholesale architectural rewrites.
