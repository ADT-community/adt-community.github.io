# ADT Community Discord

This is the set-up guide for the ADT Community Discord server. The server is where contributors meet, find paid work and see progress every week. The single source of truth for tasks is [`tasks.json`](../tasks.json) on ADT Work; the bot in [`discord_bot/`](../discord_bot/) posts new tasks into the server.

> **Maintenance note:** a Discord server and its webhook can only be created by a maintainer with a Discord account. This document is the complete, reproducible set-up recipe. Replace `INVITE_URL_TBD` below with the real invite once the server exists, then commit that one-line change. No token, webhook URL or private payout detail belongs in this repository.

## 1. Server and channels

Create one server named **ADT Community** and these channels, in this order. Use the exact names: the bot writes to `#new-tasks` and the weekly update is cross-posted to `#announcements`.

| Category | Channel | Purpose |
| --- | --- | --- |
| Start here | `#welcome` | Short intro, the invite promise ("paid open-source work on African problems"), link to [ADT Work](https://adt-community.github.io/work.html) and the rules below. Set as the only channel visible to new members. |
| Start here | `#announcements` | Weekly updates, launches, server changes. Read-only for everyone except maintainers. |
| Start here | `#how-we-pay` | How bounties work: tasks are fixed-price ($20), claim on ADT Work, deliver in a PR, paid weekly. Never ask for or post payment details here — see the [payout process issue](https://github.com/ADT-community/adt-community.github.io/issues/7). |
| Start here | `#new-tasks` | Automatic feed from `tasks.json` (bot-only channel, read-only for humans). |
| Projects | `#minibus-app` | Minibus app (owner dashboard, driver app, backend). |
| Projects | `#adt-work-community` | ADT Work and the community itself, including this Discord set-up. |
| Projects | `#investing-app` | Investing app (Ghana-first). |
| Projects | `#local-language-ai` | Local-language AI assistant. |
| Projects | `#adt-agent` | ADT agent (automation that watches the network). |
| Projects | `#creator-social-app` | Creator social app. |
| Community | `#ideas` | Propose a project or an improvement to a project. Link to [propose.html](https://adt-community.github.io/propose.html) for formal proposals. |
| Community | `#help` | Ask for help with a claim, a task or the tooling. Search before asking; include the task id (`ops-5`) and the repo. |

Add a new `#<project-name>` channel whenever a new project appears in `tasks.json`, and keep the table above in sync.

### Roles and permissions

| Role | Who | Permissions |
| --- | --- | --- |
| Maintainer | ADT maintainers | Manage channels, messages and the webhook; post in `#announcements`. |
| Contributor | Everyone after a short welcome | Read all channels, write in project channels, `#ideas` and `#help`. |
| Bot | `ADT Tasks` | `Send Messages`, `Embed Links` in `#new-tasks` only. No `Manage Messages`, no admin. |

Recommended onboarding: new members see only `#welcome`; they get `Contributor` by reacting to the welcome message or after confirming they have read the rules.

## 2. Rules (from `CODE_OF_CONDUCT.md`)

Pin this in `#welcome` and link it from every project channel. The text is copied from [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md); that file remains the authoritative version.

**Expected behaviour**

- Be respectful and patient, especially with newcomers.
- Give constructive feedback on work, not on people.
- Credit others' contributions honestly.
- Keep discussions on topic in project channels.

**Not acceptable**

- Harassment, insults or discrimination of any kind, including based on nationality, ethnicity, tribe, religion, gender or language.
- Claiming someone else's work as your own, or gaming the points system.
- Sharing other people's private information, including payment details.
- Spam or unrelated self-promotion.

**Enforcement**

Report problems to a project maintainer or ADT moderator privately by email, or use GitHub's "Report content" option on any comment. Moderators may warn, remove content, remove points earned in bad faith, or ban people from the community.

## 3. New-task feed (the bot)

[`discord_bot/post_tasks.py`](../discord_bot/post_tasks.py) reads `tasks.json` and posts one embed per **new open task** to `#new-tasks`. It has no third-party dependencies (Python 3.8+ standard library only).

### One-time set-up

1. In Discord: *Server Settings → Integrations → Webhooks → New Webhook*, name it `ADT Tasks`, choose `#new-tasks`, copy the webhook URL.
2. Store the URL **outside the repository**:
   - locally: `export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/...'` (PowerShell: `$env:DISCORD_WEBHOOK_URL='...'`);
   - for the scheduled feed: add a repository secret named `DISCORD_WEBHOOK_URL` (*Settings → Secrets and variables → Actions*).
3. Bootstrap the state so the first run does not repost all 38 currently open tasks:

   ```sh
   python discord_bot/post_tasks.py --bootstrap
   ```

   This records the current open task ids in `discord_bot/state.json` without posting anything. The state file is ignored by git.
4. Post a test message with `--dry-run` first, then run for real:

   ```sh
   python discord_bot/post_tasks.py --dry-run
   python discord_bot/post_tasks.py
   ```

5. Enable the scheduled job in [`.github/workflows/discord-feed.yml`](../.github/workflows/discord-feed.yml) (Actions → *Discord new-task feed* → *Run workflow*) and check that `#new-tasks` receives a message after you add a test task to `tasks.json`.

### How it behaves

- Only tasks with `"status": "open"` are considered; each id is posted at most once (`discord_bot/state.json`).
- The webhook URL must be on `discord.com` or `discordapp.com`; anything else is refused.
- A failed post never advances the state, so the task is retried on the next run.
- `--limit N` caps posts per run (default 10) to avoid Discord rate limits.
- `--dry-run` prints the embeds and changes nothing. No webhook URL is needed for a dry run.
- Each embed links to `https://adt-community.github.io/task.html?id=<task id>`, so every Discord post leads back to ADT Work.

Operational note: the state file must be persistent. Locally it is a file; in the scheduled workflow it is restored from the Actions cache (see the workflow). Anyone running the script both locally and in CI should use `--state-file` to point at separate files.

## 4. Weekly update habit

Every Monday, publish a short update using [`docs/updates/template.md`](updates/template.md) with exactly four sections: **Shipped**, **Paid**, **New tasks**, **Next**. Post it to `#announcements`, copy the same text into a new file in [`docs/updates/`](updates/) and open a PR with it. Keep the files in `YYYY-MM-DD.md` form; [the index](updates/README.md) lists them. The first update is [`2026-11-21.md`](updates/2026-11-21.md).

This is a habit, not a new tool: a maintainer spends ten minutes a week on it. Long-term moderation is out of scope for this task; day-to-day moderation is shared by the maintainers listed in the server roles.
