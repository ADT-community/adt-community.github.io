"""Post new open ADT Work tasks to a Discord channel through a webhook.

Standard library only. The webhook URL is read from DISCORD_WEBHOOK_URL and is
never written to the repository. Run ``python discord_bot/post_tasks.py --help``.
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TASKS = REPO_ROOT / "tasks.json"
DEFAULT_STATE = Path(__file__).resolve().parent / "state.json"
TASK_BASE_URL = "https://adt-community.github.io/task.html?id="
WEBHOOK_HOSTS = frozenset(("discord.com", "discordapp.com"))
MAX_DESCRIPTION = 4096
MAX_FIELD_VALUE = 1024


class FeedError(Exception):
    """A configuration or input error that stops the feed."""


def task_id(task):
    return str(task.get("id") or "").strip()


def is_open(task):
    return str(task.get("status") or "").strip().lower() == "open"


def load_tasks(path=DEFAULT_TASKS):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise FeedError("cannot read tasks.json: {}".format(exc))
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise FeedError("tasks.json is not valid JSON: {}".format(exc))
    tasks = data.get("tasks") if isinstance(data, dict) else None
    if not isinstance(tasks, list):
        raise FeedError("tasks.json must contain a 'tasks' list")
    return [task for task in tasks if isinstance(task, dict)]


def load_state(path=DEFAULT_STATE):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return set()
    except OSError as exc:
        raise FeedError("cannot read state file: {}".format(exc))
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise FeedError("state file is not valid JSON: {}".format(exc))
    if isinstance(data, dict):
        posted = data.get("posted", [])
    elif isinstance(data, list):
        posted = data
    else:
        posted = None
    if not isinstance(posted, list) or not all(isinstance(item, str) for item in posted):
        raise FeedError("state file must contain a list of task ids in 'posted'")
    return set(posted)


def save_state(path, posted, updated=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated": updated or date.today().isoformat(),
        "posted": sorted(posted),
    }
    fd, tmp_name = tempfile.mkstemp(prefix=".state-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_name, str(path))
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def task_url(task):
    return TASK_BASE_URL + urllib.parse.quote(task_id(task), safe="")


def _clip(value, limit):
    text = str(value if value is not None else "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def reward_text(task):
    reward = task.get("reward")
    if not task.get("paid") or not reward:
        return "Unpaid"
    return "${}".format(reward)


def format_embed(task):
    identifier = task_id(task)
    embed = {
        "title": _clip("{} ({})".format(task.get("title") or "Untitled task", identifier), 256),
        "url": task_url(task),
        "description": _clip(task.get("deliverable") or "", MAX_DESCRIPTION),
        "fields": [],
    }
    for name, value in (
        ("Project", task.get("project")),
        ("Pay", reward_text(task)),
        ("Level", task.get("level")),
        ("Time", task.get("hours")),
    ):
        if value:
            embed["fields"].append(
                {"name": name, "value": _clip(value, MAX_FIELD_VALUE), "inline": True}
            )
    return embed


def select_new_tasks(tasks, posted, limit=10):
    """Open tasks whose id has not been posted yet, in tasks.json order."""
    if limit < 0:
        raise FeedError("--limit must be zero or positive")
    if limit == 0:
        return []
    chosen = []
    seen = set(posted)
    for task in tasks:
        if not is_open(task):
            continue
        identifier = task_id(task)
        if not identifier or identifier in seen:
            continue
        seen.add(identifier)
        chosen.append(task)
        if len(chosen) >= limit:
            break
    return chosen


def webhook_allowed(url):
    """Only Discord webhook endpoints are accepted as destinations."""
    try:
        parts = urllib.parse.urlsplit(str(url or "").strip())
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and parts.hostname in WEBHOOK_HOSTS
        and parts.path.startswith("/api/webhooks/")
    )


def post_embed(webhook_url, embed, opener=None, timeout=10):
    """POST one embed. Returns True on 2xx, False on an HTTP/network error."""
    if not webhook_allowed(webhook_url):
        raise FeedError("webhook URL must be an https Discord webhook on discord.com")
    payload = json.dumps({"username": "ADT Tasks", "embeds": [embed]}).encode("utf-8")
    request = urllib.request.Request(
        str(webhook_url).strip(),
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "adt-discord-feed/1.0"},
        method="POST",
    )
    http = opener or urllib.request
    try:
        with http.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            return 200 <= int(status) < 300
    except urllib.error.HTTPError as exc:
        return False
    except OSError:
        return False


def run_once(tasks_path=DEFAULT_TASKS, state_path=DEFAULT_STATE, webhook_url="",
             limit=10, dry_run=False, bootstrap=False, opener=None, timeout=10,
             emit=print):
    """Run one feed cycle and return a summary dict (no secrets in the summary)."""
    tasks = load_tasks(tasks_path)
    posted = load_state(state_path)
    open_ids = [task_id(task) for task in tasks if is_open(task) and task_id(task)]

    if bootstrap:
        save_state(state_path, posted.union(open_ids))
        emit("Bootstrapped {} open task ids (no messages posted)".format(len(open_ids)))
        return {"bootstrapped": len(open_ids), "posted": 0, "failed": [], "dry_run": False}

    new_tasks = select_new_tasks(tasks, posted, limit)
    if dry_run:
        for task in new_tasks:
            emit("[dry run] " + json.dumps(format_embed(task), ensure_ascii=False))
        return {"bootstrapped": 0, "posted": 0, "failed": [], "dry_run": True,
                "would_post": len(new_tasks)}

    if not new_tasks:
        emit("No new open tasks")
        return {"bootstrapped": 0, "posted": 0, "failed": [], "dry_run": False}
    if not str(webhook_url or "").strip():
        emit("DISCORD_WEBHOOK_URL is not set; skipping {} new tasks".format(len(new_tasks)))
        return {"bootstrapped": 0, "posted": 0, "failed": [], "dry_run": False,
                "skipped_no_webhook": True}

    done = 0
    failed = []
    for task in new_tasks:
        identifier = task_id(task)
        if post_embed(webhook_url, format_embed(task), opener=opener, timeout=timeout):
            posted.add(identifier)
            save_state(state_path, posted)
            done += 1
        else:
            failed.append(identifier)
    emit("Posted {} new tasks, {} failed".format(done, len(failed)))
    return {"bootstrapped": 0, "posted": done, "failed": failed, "dry_run": False}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tasks", default=str(DEFAULT_TASKS), help="path to tasks.json")
    parser.add_argument("--state-file", default=str(DEFAULT_STATE),
                        help="path to the persistent list of posted task ids")
    parser.add_argument("--limit", type=int, default=10,
                        help="maximum messages per run (default: 10)")
    parser.add_argument("--timeout", type=int, default=10, help="webhook timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="print embeds, change nothing")
    parser.add_argument("--bootstrap", action="store_true",
                        help="mark current open tasks as posted without sending anything")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    try:
        summary = run_once(
            tasks_path=args.tasks,
            state_path=args.state_file,
            webhook_url=webhook_url,
            limit=args.limit,
            dry_run=args.dry_run,
            bootstrap=args.bootstrap,
            timeout=args.timeout,
        )
    except FeedError as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 2
    return 1 if summary.get("failed") else 0


if __name__ == "__main__":
    sys.exit(main())
