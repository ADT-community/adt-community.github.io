Closes #5

## What this PR delivers

- `docs/discord.md` — the complete, reproducible Discord set-up: server name, the exact channels requested (`welcome`, `announcements`, `how-we-pay`, one channel per project from `tasks.json`, `ideas`, `help`, plus the bot-only `new-tasks`), roles/permissions, the rules copied from `CODE_OF_CONDUCT.md`, and step-by-step webhook/bot setup.
- `discord_bot/post_tasks.py` — dependency-free (Python 3.8+ stdlib) new-task feed. It reads `tasks.json`, posts one embed per **new open task** to a Discord webhook with a link back to `task.html?id=<id>`, keeps posted ids in a persistent state file, refuses non-Discord webhook hosts, and never advances state on a failed post. `--dry-run` and `--bootstrap` are included. The webhook URL comes only from `DISCORD_WEBHOOK_URL`; no secret is committed.
- `.github/workflows/discord-feed.yml` — scheduled feed (every 6 hours + manual dispatch) that runs the tests and posts new tasks, with the state cached between runs. It stays green with a clear message when the secret is not configured.
- `docs/updates/` — `template.md` (shipped / paid / new tasks / next), `2026-11-21.md` (the first update, using real data from `tasks.json`) and `README.md` (index and cadence).
- `README.md` links to the Discord guide and the weekly updates; `.gitignore` keeps the local bot state and bytecode out of git.

## Verification

```
python -m unittest discover -s discord_bot/tests -v   # 20 tests, OK
python -m py_compile discord_bot/post_tasks.py discord_bot/tests/test_post_tasks.py
python discord_bot/post_tasks.py --tasks tasks.json --state-file <tmp>/state.json --dry-run --limit 3
git diff --check
```

No third-party packages were installed. The dry run uses the repository's real `tasks.json` and emits embeds without making any network request.

## Honest limitation

A Discord server, its invite and the webhook can only be created by a maintainer with a Discord account; that is an operational step, not something a pull request can perform. `docs/discord.md` marks the invite as `INVITE_URL_TBD`, lists every manual step, and the first weekly update states plainly that the feed is configured but not yet live. Once a maintainer creates the server and adds the `DISCORD_WEBHOOK_URL` secret, the documented bootstrap + workflow enable the live new-task feed. No private keys, seed phrases or payout details are used anywhere in this change.
