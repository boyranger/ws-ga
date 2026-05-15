# Public Telegram Bot Implementation Plan

## Objective

Add a public Telegram-facing product surface for RepoReadinessAgent where each Telegram user can inspect and track their own repositories.

## Recommended stack for v1

- Python 3
- existing `RepoReadinessAgent` package
- SQLite database
- Telegram bot library (one of: `python-telegram-bot` or `aiogram`)
- optional cron/background runner for follow-up checks

Recommendation: use **python-telegram-bot** for fastest stable v1.

## Why this is the right shape

This keeps the demo architecture believable without overbuilding:
- public access works
- per-user tracking works
- reporting persists
- follow-up becomes real product behavior
- scoring logic stays centralized

## Minimal robust feature set

### Must-have
- public bot token/config
- `/start`
- `/inspect <repo_url>`
- `/myrepos`
- `/report <tracking_id>`
- database persistence for users + repos + reports
- ownership checks

### Should-have
- `/track <repo_url>`
- `/followup <tracking_id>`
- `/untrack <tracking_id>`
- daily follow-up via cron/worker

### Nice-to-have
- inline buttons
- pretty repo cards
- pagination
- admin metrics

## Proposed implementation seams

### 1. Add a bot package

Suggested new files:

```text
src/repo_readiness_agent/bot/__init__.py
src/repo_readiness_agent/bot/app.py
src/repo_readiness_agent/bot/handlers.py
src/repo_readiness_agent/bot/service.py
src/repo_readiness_agent/bot/repository.py
src/repo_readiness_agent/bot/storage.py
src/repo_readiness_agent/bot/types.py
```

### 2. Add a DB file path convention

Suggested path:
- `data/repo_readiness_agent.sqlite3`

For demo deployments, keep this outside source packages.

### 3. Add bot-specific entrypoint

Example:
- `python -m repo_readiness_agent.bot.app`

### 4. Keep engine dependency one-way

Bot layer -> application service -> product engine -> scorer

Not the reverse.

## Storage responsibilities

### storage.py
Owns:
- opening DB connections
- schema init
- migration bootstrap
- transaction helpers

### repository.py
Owns:
- `upsert_telegram_user(...)`
- `get_user_by_telegram_id(...)`
- `get_or_create_tracked_repo(...)`
- `list_user_tracked_repos(...)`
- `insert_report(...)`
- `get_latest_report_for_repo(...)`
- `get_latest_report_by_tracking_id_for_user(...)`
- `set_followup_config(...)`
- `archive_tracking(...)`

## Service responsibilities

### service.py
Owns use-cases such as:
- inspect repo for user
- track repo for user
- list repos for user
- fetch latest report for user-owned tracking id
- run follow-up and compare with previous report

The service layer should be where ownership checks happen.

## Handler responsibilities

### handlers.py
Owns only Telegram transport logic:
- parse incoming command args
- call service methods
- convert results to message text
- map exceptions to user-friendly replies

No DB SQL and no scoring logic here.

## Example inspect flow

1. user sends `/inspect https://github.com/owner/repo`
2. handler validates argument presence
3. service upserts Telegram user
4. service normalizes repo URL
5. service gets or creates tracked repo row
6. service calls `build_product_report(run_engine(...))`
7. service stores the resulting product report JSON
8. handler returns a formatted founder-facing summary

## Example follow-up flow

1. user sends `/followup 12`
2. handler resolves tracking id
3. service verifies ownership for that Telegram user
4. service loads previous stored product report
5. service re-runs inspection
6. service uses existing product follow-up logic to compare old vs new
7. service stores new report
8. handler replies with improved/unchanged/still-blocked summary

## Database schema sketch

```sql
create table telegram_users (
  id integer primary key autoincrement,
  telegram_user_id text not null unique,
  username text,
  first_name text,
  last_name text,
  created_at text not null,
  updated_at text not null,
  last_seen_at text not null
);

create table tracked_repositories (
  id integer primary key autoincrement,
  user_id integer not null,
  repo_url text not null,
  repo_normalized text not null,
  default_branch text,
  status text not null default 'active',
  created_at text not null,
  updated_at text not null,
  last_checked_at text,
  unique(user_id, repo_normalized),
  foreign key(user_id) references telegram_users(id)
);

create table inspection_reports (
  id integer primary key autoincrement,
  tracked_repository_id integer not null,
  trigger_kind text not null,
  report_json text not null,
  stage text not null,
  confidence text not null,
  verdict text not null,
  top_risks_json text not null,
  top_fixes_json text not null,
  demo_safe text,
  launch_ready text,
  handoff_ready text,
  created_at text not null,
  foreign key(tracked_repository_id) references tracked_repositories(id)
);

create table followup_jobs (
  id integer primary key autoincrement,
  tracked_repository_id integer not null unique,
  enabled integer not null default 1,
  cadence text not null default 'daily',
  target_stage text not null default 'Handoff-ready',
  target_confidence text not null default 'High',
  last_run_at text,
  next_run_at text,
  stop_when_reached integer not null default 1,
  created_at text not null,
  updated_at text not null,
  foreign key(tracked_repository_id) references tracked_repositories(id)
);
```

## Background follow-up options

### Option A — easiest demo path
Use gateway cron to wake a runner command daily.

Flow:
- cron wakes job
- runner loads due `followup_jobs`
- re-runs inspections
- writes new reports
- sends notifications through the bot

### Option B — worker process
Run a small worker loop that checks due jobs periodically.

Recommendation for hackathon: **Option A**.
It is simpler, more explainable, and aligns with OpenClaw's cron model.

## Error handling rules

- invalid repo URL -> explain supported format
- non-GitHub URL -> reject clearly
- timeout -> say inspection took too long and invite retry
- scorer failure -> return a short failure message without stack trace
- unauthorized tracking id access -> generic "not found" style response

## Privacy rules

- users should only see their own tracked repositories and reports
- do not expose global repo history across users
- do not store unnecessary personal data
- do not mix Mahdy/Fauzi internal workspace memory with public user data

## Recommendation on public launch

Yes, make the bot public for the demo.

But make the first version intentionally narrow:
- GitHub repos only
- Telegram only
- manual inspect first
- tracked follow-up second

That gives the strongest demo-to-implementation ratio.
