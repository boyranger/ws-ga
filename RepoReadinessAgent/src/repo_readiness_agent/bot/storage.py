"""SQLite storage helpers for Repo Readiness Agent bot."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
create table if not exists telegram_users (
  id integer primary key autoincrement,
  telegram_user_id text not null unique,
  username text,
  first_name text,
  last_name text,
  created_at text not null,
  updated_at text not null,
  last_seen_at text not null
);

create table if not exists tracked_repositories (
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

create table if not exists inspection_reports (
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

create table if not exists followup_jobs (
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

create table if not exists conversation_state (
  telegram_user_id text primary key,
  active_tracking_id integer,
  active_repo_url text,
  last_report_id integer,
  last_user_goal text,
  last_agent_action text,
  conversation_summary text,
  updated_at text not null
);
"""


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("pragma foreign_keys = on")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA_SQL)
            connection.commit()
