# Public Telegram Bot Architecture for RepoReadinessAgent

## Goal

Turn RepoReadinessAgent into a public Telegram bot that any user can access.

Each Telegram user should have their own repo-readiness tracking records so the bot can:
- accept a repository URL
- run a readiness inspection
- store the latest founder-facing report
- let the same user review previous reports later
- optionally run follow-up checks on the same tracked repository

This should stay intentionally compact for v1:
- one public bot
- one product agent / one application service
- one small relational database
- one inspection engine (the existing RepoReadinessAgent scorer + product layer)

## Product stance

This is **not** a generic chatbot.

The Telegram bot should behave like a focused product surface for RepoReadinessAgent:
- intake a repo
- inspect it
- return a founder-facing report
- remember that user's tracked repos
- compare progress later

The bot layer should not own scoring rules.
The scorer/product engine remains the source of truth for readiness judgment.

## Recommended v1 architecture

Use four layers:

1. **Telegram transport layer**
   - receives Telegram updates
   - parses commands/messages
   - sends formatted replies

2. **Application service layer**
   - maps Telegram actions into product use-cases
   - handles user/repo/report tracking workflows
   - coordinates inspect/follow-up flows

3. **RepoReadinessAgent product engine**
   - already exists
   - produces founder-facing reports
   - remains the canonical source of scoring and product output

4. **Persistence layer**
   - stores users, tracked repos, reports, and follow-up jobs

## Do not spawn a second scoring agent

For v1, do **not** create a separate autonomous agent that duplicates report logic.

Better:
- keep one Telegram-facing application service
- call the existing RepoReadinessAgent engine for inspection
- store the resulting product report in the database

This preserves single-source-of-truth behavior and prevents drift between demo surface and CLI surface.

## Recommended runtime shape

### Service A: public Telegram bot app

Responsibilities:
- receive updates from Telegram
- authenticate bot token
- route commands/messages
- call application services
- render outputs back to chat

Suggested commands:
- `/start`
- `/help`
- `/inspect <github_url>`
- `/myrepos`
- `/report <tracking_id>`
- `/followup <tracking_id>`
- `/track <github_url>`
- `/untrack <tracking_id>`

### Service B: optional background worker

Responsibilities:
- run longer inspections outside the request path if needed
- process scheduled follow-up checks
- update follow-up status records
- send result notifications back through the bot service

For hackathon v1, this can start as a lightweight in-process worker or cron-triggered job.
It does not need to become a full queue platform unless traffic grows.

## Database recommendation

Use **SQLite** for demo-first local simplicity, with a migration path to Postgres.

Why SQLite first:
- minimal setup
- easy to commit schema + run locally
- enough for hackathon/demo traffic
- works well for one small public bot

If you expect shared deployment or concurrent write pressure later, switch to Postgres.

## Core data model

Keep the schema small and explicit.

### 1. telegram_users
Tracks public bot users.

Fields:
- `id` (internal UUID or integer primary key)
- `telegram_user_id` (unique)
- `username` (nullable)
- `first_name` (nullable)
- `last_name` (nullable)
- `created_at`
- `updated_at`
- `last_seen_at`

Rules:
- one record per Telegram user
- `telegram_user_id` is the stable external identity

### 2. tracked_repositories
Tracks repositories a user has asked the bot to monitor or inspect.

Fields:
- `id`
- `user_id` (FK -> telegram_users.id)
- `repo_url`
- `repo_normalized`
- `default_branch` (nullable)
- `status` (`active`, `archived`)
- `created_at`
- `updated_at`
- `last_checked_at` (nullable)

Rules:
- unique per `(user_id, repo_normalized)`
- the same public repo may be tracked by many different users
- each user owns their own tracking state

### 3. inspection_reports
Stores the output of each inspection run.

Fields:
- `id`
- `tracked_repository_id` (FK)
- `trigger_kind` (`manual_inspect`, `manual_followup`, `scheduled_followup`)
- `report_json`
- `stage`
- `confidence`
- `verdict`
- `top_risks_json`
- `top_fixes_json`
- `demo_safe`
- `launch_ready`
- `handoff_ready`
- `created_at`

Rules:
- `report_json` stores the canonical product report payload
- duplicate summary columns exist only for filtering/query convenience
- product JSON remains the real artifact

### 4. followup_jobs
Stores whether a repository should be rechecked later.

Fields:
- `id`
- `tracked_repository_id` (FK)
- `enabled` (bool)
- `cadence` (`daily`, `manual_only`)
- `target_stage`
- `target_confidence`
- `last_run_at` (nullable)
- `next_run_at` (nullable)
- `stop_when_reached` (bool)
- `created_at`
- `updated_at`

Rules:
- one active follow-up config per tracked repo in v1 is enough
- stop automatically when target stage/confidence is reached

### 5. outbound_notifications
Optional table for auditability.

Fields:
- `id`
- `user_id`
- `tracked_repository_id` (nullable)
- `kind`
- `payload_json`
- `status`
- `created_at`
- `sent_at` (nullable)

This is optional in v1 but useful if you want reliable notification tracing.

## Canonical ownership by module

To keep architecture coherent:

- `src/repo_readiness_agent/contract.py`
  - owns founder-facing report structures
- `src/repo_readiness_agent/engine.py`
  - owns scorer invocation and translation
- new bot application module should own:
  - Telegram command orchestration
  - persistence workflows
  - user/repo/report lifecycle
- database layer should own:
  - schema creation
  - CRUD persistence
  - query helpers

The Telegram bot should **not** invent its own stage/verdict rules.

## Suggested new package structure

A clean v1 addition could look like:

```text
RepoReadinessAgent/
  src/
    repo_readiness_agent/
      contract.py
      engine.py
      formatter.py
      followup.py
      cli.py
      bot/
        __init__.py
        app.py
        handlers.py
        service.py
        repository.py
        models.py
        storage.py
```

Suggested ownership:
- `bot/app.py` -> bot entrypoint/runtime bootstrap
- `bot/handlers.py` -> Telegram command handlers only
- `bot/service.py` -> application use-cases
- `bot/repository.py` -> database queries and persistence
- `bot/models.py` -> DB row/dataclass definitions if useful
- `bot/storage.py` -> DB connection/init/migrations helper

## Recommended command behavior

### `/start`
- create or upsert Telegram user record
- show short product intro
- suggest `/inspect <github_url>`

### `/inspect <github_url>`
- upsert user
- normalize repo URL
- create tracked repo record if missing
- run RepoReadinessAgent inspection
- store resulting report
- return founder-facing text report

### `/track <github_url>`
- ensure tracked repo exists
- enable daily follow-up config
- confirm tracking enabled

### `/myrepos`
- list tracked repos for that Telegram user only
- show short IDs/status/last stage

### `/report <tracking_id>`
- fetch latest report for that user-owned repo
- return summary

### `/followup <tracking_id>`
- re-run inspection
- compare against latest stored report
- store new report with follow-up status
- return improved/unchanged/still blocked result

### `/untrack <tracking_id>`
- disable follow-up job or archive repo tracking record

## Normalization rules

Before writing repo URLs to the DB:
- normalize GitHub URLs to a canonical format
- strip trailing slash
- strip `.git`
- preserve owner/repo identity

Example canonical form:
- `https://github.com/owner/repo`

This matters because user input will vary.

## Security and abuse considerations

Because the bot is public, add guardrails even in v1:

### Input validation
- only allow GitHub URLs for now
- reject unsupported hosts clearly
- cap message length

### Per-user throttling
- simple rate limit per Telegram user
- example: max 5 inspect requests per 10 minutes

### Execution timeout
- enforce timeout for inspections
- surface a friendly retry message if exceeded

### Safe persistence
- never store Telegram bot token in the database
- store only minimal user metadata
- do not store unrelated chat history

### Ownership checks
- every `/report`, `/followup`, `/untrack` request must verify that the `tracking_id` belongs to the requesting Telegram user

This is the biggest correctness and privacy rule in the public-bot version.

## Suggested storage contract

The canonical saved artifact per run should be the **product-layer JSON report**, not raw scorer internals only.

Why:
- it matches what users see
- it matches the product contract
- it makes future UI/API surfaces simpler
- it keeps persistence aligned with the outward product

## Suggested follow-up strategy

For v1, keep it simple:
- default mode: manual inspect
- optional tracking mode: daily follow-up
- compare latest report vs previous report using existing follow-up logic
- stop notifications once target stage/confidence is reached

Use the existing product follow-up contract as the comparison source of truth.

## Suggested implementation order

### Phase 1 — storage foundation
- add DB schema
- add user/tracked-repo/report persistence layer
- add repo URL normalization

### Phase 2 — bot transport
- add Telegram command handlers
- wire `/start`, `/inspect`, `/myrepos`, `/report`

### Phase 3 — follow-up workflow
- add `/track`, `/followup`, `/untrack`
- add daily follow-up scheduler or cron-triggered runner

### Phase 4 — polish
- add throttling
- add better formatting
- add clearer error messages
- add observability/logging

## Recommendation

Yes, I think this is a strong direction.

But the most robust version is:
- **public Telegram bot** as the product surface
- **simple relational DB** for per-user tracking
- **RepoReadinessAgent engine** as the single source of truth
- **no duplicated scoring logic in the bot layer**

That gives you:
- demo clarity
- multi-user readiness
- believable product depth
- compact architecture that still feels production-shaped
