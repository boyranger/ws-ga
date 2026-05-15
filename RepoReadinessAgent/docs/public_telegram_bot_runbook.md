# Public Telegram Bot Runbook

## Install

```bash
cd RepoReadinessAgent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-bot.txt
```

## Configure

Do **not** commit the real bot token.

Create a local `.env` or export environment variables directly:

```bash
export REPO_READINESS_TELEGRAM_BOT_TOKEN="<your-telegram-bot-token>"
export REPO_READINESS_DB_PATH="$PWD/data/repo_readiness_agent.sqlite3"
```

## Run the public bot

```bash
cd RepoReadinessAgent
PYTHONPATH=src python3 -m repo_readiness_agent.bot.app
```

## Bot commands

- `/start`
- `/help`
- `/inspect <github_url>`
- `/track <github_url>`
- `/myrepos`
- `/report <tracking_id>`
- `/followup <tracking_id>`
- `/untrack <tracking_id>`

## Run the follow-up runner manually

```bash
cd RepoReadinessAgent
PYTHONPATH=src python3 -m repo_readiness_agent.bot.runner
```

## Example cron setup

Run once daily at 9:00 AM server time:

```cron
0 9 * * * cd /path/to/RepoReadinessAgent && PYTHONPATH=src REPO_READINESS_TELEGRAM_BOT_TOKEN="$REPO_READINESS_TELEGRAM_BOT_TOKEN" REPO_READINESS_DB_PATH="/path/to/RepoReadinessAgent/data/repo_readiness_agent.sqlite3" python3 -m repo_readiness_agent.bot.runner >> /tmp/repo-readiness-followup.log 2>&1
```

## Notes

- SQLite is enough for demo/hackathon traffic.
- Keep the DB file local and ignored.
- Keep the Telegram token in environment variables or a secrets manager.
- The follow-up runner now supports automatic Telegram delivery for due follow-ups when `REPO_READINESS_TELEGRAM_BOT_TOKEN` is present.
- Practical hackathon setup: run the bot normally for chat interactions, and run the follow-up runner from cron once per day to deliver autonomous progress checks.
