#!/usr/bin/env python3
"""
ADT Community Discord Bounty Feed Bot.

Monitors GitHub repositories in the ADT-community organization for new bounty tasks
and posts formatted rich embeds to the configured Discord channel via webhook.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

# ADT flagship repositories and their friendly display names
REPOS: Dict[str, str] = {
    "trans_sport": "Minibus app",
    "locallity_ai": "Local-language AI",
    "content_feed": "Creator social app",
    "ADT_agent": "ADT agent",
    "trader": "Quant trading lab",
    "adt-community.github.io": "ADT Community",
}

DEFAULT_STATE_FILE = ".bounty_feed_cache.json"
DEFAULT_AVATAR_URL = "https://adt-community.github.io/logo.png"
ADT_WORK_URL = "https://adt-community.github.io/work.html"


def extract_field(body: Optional[str], field_name: str) -> str:
    """Extract a bold header field like **Level:** Beginner from markdown body."""
    if not body:
        return ""
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s*([^·\n]+)"
    match = re.search(pattern, body, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def extract_section(body: Optional[str], section_name: str, max_lines: int = 4) -> str:
    """Extract bullet points or lines under a markdown section like ### Done when."""
    if not body:
        return ""
    pattern = rf"###\s+{re.escape(section_name)}[^\n]*\n([\s\S]*?)(?=\n###|\Z)"
    match = re.search(pattern, body, re.IGNORECASE)
    if not match:
        return ""
    content = match.group(1).strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if max_lines and len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + "\n..."
    return "\n".join(lines)


def get_label_names(issue: Dict[str, Any]) -> List[str]:
    """Normalize labels into a list of lowercase string names."""
    labels = issue.get("labels", [])
    result = []
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name", "")
        else:
            name = str(label)
        if name:
            result.append(name.strip())
    return result


def is_bounty_issue(issue: Dict[str, Any]) -> bool:
    """Check if an issue is a bounty task or next-wave task and not a pull request."""
    if issue.get("pull_request") is not None:
        return False

    labels = [l.lower() for l in get_label_names(issue)]
    has_bounty = any(
        l == "bounty"
        or l.startswith("bounty:")
        or l == "next-wave"
        for l in labels
    )
    return has_bounty


def parse_bounty_issue(issue: Dict[str, Any], repo_name: str) -> Optional[Dict[str, Any]]:
    """Parse a GitHub issue into a structured bounty task representation."""
    if not is_bounty_issue(issue):
        return None

    raw_labels = get_label_names(issue)
    labels_lower = [l.lower() for l in raw_labels]
    body = issue.get("body") or ""

    # Determine bounty price
    price = "Next wave"
    for label in raw_labels:
        match = re.match(r"^bounty:(\$\d+)", label, re.IGNORECASE)
        if match:
            price = match.group(1)
            break
    if price == "Next wave" and "bounty" in labels_lower:
        # Check if reward is stated in body
        reward_field = extract_field(body, "Reward")
        match = re.search(r"\$\d+", reward_field)
        if match:
            price = match.group(0)

    # Determine task type
    if repo_name == "adt-community.github.io":
        task_type = "Operations"
    elif any("design" in l for l in labels_lower):
        task_type = "Design"
    elif any("research" in l for l in labels_lower):
        task_type = "Research"
    else:
        task_type = "Code"

    # Extract metadata fields
    level = extract_field(body, "Level") or "Beginner"
    time_estimate = extract_field(body, "Time") or extract_field(body, "Size") or "2–5 hours"
    deliverable = extract_field(body, "Deliverable")
    done_when = extract_section(body, "Done when", max_lines=3)
    assignees = issue.get("assignees", []) or []
    is_assigned = len(assignees) > 0

    return {
        "id": issue.get("id"),
        "number": issue.get("number"),
        "title": issue.get("title", "Untitled Bounty"),
        "url": issue.get("html_url") or issue.get("url", ""),
        "repo": repo_name,
        "project": REPOS.get(repo_name, repo_name),
        "type": task_type,
        "pay": price,
        "is_paid": price != "Next wave",
        "level": level,
        "time": time_estimate,
        "deliverable": deliverable,
        "done_when": done_when,
        "assigned": is_assigned,
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
    }


def format_discord_embed(task: Dict[str, Any]) -> Dict[str, Any]:
    """Create a Discord Embed dictionary from a parsed bounty task."""
    # Color: Green (0x2ECC71) for paid bounties, Blue (0x3498DB) for next wave
    color = 0x2ECC71 if task.get("is_paid") else 0x3498DB

    # Description summary
    description_parts = []
    if task.get("deliverable"):
        description_parts.append(f"**Deliverable:** {task['deliverable']}")
    if task.get("done_when"):
        description_parts.append(f"**Done when:**\n{task['done_when']}")

    description = "\n\n".join(description_parts)
    if not description:
        description = "A new task is open for contributors in the ADT Community."

    # Fields
    fields = [
        {"name": "💰 Reward", "value": task.get("pay", "Next wave"), "inline": True},
        {"name": "📦 Project", "value": f"{task.get('project')} (`{task.get('repo')}`)", "inline": True},
        {"name": "🏷️ Type", "value": task.get("type", "Code"), "inline": True},
        {"name": "🎯 Level", "value": task.get("level", "Beginner"), "inline": True},
        {"name": "⏱️ Time", "value": task.get("time", "2–5 hours"), "inline": True},
        {
            "name": "📌 Status",
            "value": "Assigned" if task.get("assigned") else "Open for claim",
            "inline": True,
        },
        {
            "name": "🚀 How to claim",
            "value": "Comment *\"I'd like to take this\"* on GitHub and wait to be assigned before starting.",
            "inline": False,
        },
    ]

    # ISO timestamp
    timestamp = task.get("created_at") or datetime.now(timezone.utc).isoformat()

    return {
        "title": f"🎯 New Task: {task.get('title')}",
        "url": task.get("url"),
        "description": description,
        "color": color,
        "fields": fields,
        "footer": {
            "text": "ADT Community • Build for Africa. Get paid. • adt-community.github.io/work.html",
            "icon_url": DEFAULT_AVATAR_URL,
        },
        "timestamp": timestamp,
    }


def create_webhook_payload(
    task: Dict[str, Any],
    content: Optional[str] = None,
    username: str = "ADT Bounty Feed",
    avatar_url: str = DEFAULT_AVATAR_URL,
) -> Dict[str, Any]:
    """Create the full Discord webhook payload including embeds."""
    embed = format_discord_embed(task)
    payload: Dict[str, Any] = {
        "username": username,
        "avatar_url": avatar_url,
        "embeds": [embed],
    }
    if content:
        payload["content"] = content
    return payload


def send_discord_webhook(webhook_url: str, payload: Dict[str, Any], timeout: int = 10) -> bool:
    """Send JSON payload to a Discord webhook URL using urllib."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ADT-Bounty-Bot/1.0 (+https://adt-community.github.io)",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.getcode()
            # Discord webhooks respond with 204 No Content or 200 OK
            return status in (200, 204)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"Discord webhook HTTP error {e.code}: {e.reason}\n")
        return False
    except urllib.error.URLError as e:
        sys.stderr.write(f"Discord webhook URL error: {e.reason}\n")
        return False
    except Exception as e:
        sys.stderr.write(f"Unexpected error sending Discord webhook: {e}\n")
        return False


def load_cache(cache_path: str) -> set:
    """Load previously posted issue IDs or URLs from cache file."""
    if not os.path.exists(cache_path):
        return set()
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return set(data)
            if isinstance(data, dict):
                return set(data.get("posted", []))
    except Exception as e:
        sys.stderr.write(f"Warning: could not read cache file {cache_path}: {e}\n")
    return set()


def save_cache(cache_path: str, posted_ids: set) -> None:
    """Save posted issue IDs or URLs to cache file."""
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"posted": sorted(list(posted_ids))}, f, indent=2)
    except Exception as e:
        sys.stderr.write(f"Warning: could not write cache file {cache_path}: {e}\n")


def fetch_repo_issues(repo_name: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch open issues for a repository in the ADT-community organization."""
    url = f"https://api.github.com/repos/ADT-community/{repo_name}/issues?state=open&per_page=100"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ADT-Bounty-Bot/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.getcode() == 200:
                data = json.loads(res.read().decode("utf-8"))
                return data if isinstance(data, list) else []
    except Exception as e:
        sys.stderr.write(f"Failed to fetch issues for ADT-community/{repo_name}: {e}\n")
    return []


def scan_and_post_bounties(
    webhook_url: Optional[str],
    repos: Optional[List[str]] = None,
    state_file: str = DEFAULT_STATE_FILE,
    dry_run: bool = False,
    token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Scan ADT repositories for open bounty tasks and post new ones to Discord.
    Returns list of posted task dictionaries.
    """
    repos_to_scan = repos or list(REPOS.keys())
    posted_cache = load_cache(state_file)
    new_posted: List[Dict[str, Any]] = []

    for repo in repos_to_scan:
        issues = fetch_repo_issues(repo, token=token)
        for issue in issues:
            task = parse_bounty_issue(issue, repo)
            if not task:
                continue

            # Unique key for tracking
            issue_key = str(task["id"]) if task.get("id") else task["url"]
            if issue_key in posted_cache:
                continue

            payload = create_webhook_payload(task)
            if dry_run:
                sys.stdout.write(f"[DRY-RUN] Found bounty: {task['project']} - {task['title']} ({task['pay']})\n")
                new_posted.append(task)
                posted_cache.add(issue_key)
            else:
                if not webhook_url:
                    sys.stderr.write("Error: webhook URL required when not in dry-run mode\n")
                    continue
                sys.stdout.write(f"Posting bounty: {task['project']} - {task['title']}\n")
                success = send_discord_webhook(webhook_url, payload)
                if success:
                    new_posted.append(task)
                    posted_cache.add(issue_key)

    if not dry_run and new_posted:
        save_cache(state_file, posted_cache)

    return new_posted


def handle_github_event(
    event_path: str,
    webhook_url: Optional[str],
    dry_run: bool = False,
) -> Optional[Dict[str, Any]]:
    """Handle a GitHub Action event payload (e.g. issue opened or labeled)."""
    if not os.path.exists(event_path):
        sys.stderr.write(f"Event file not found: {event_path}\n")
        return None

    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    issue = event.get("issue")
    if not issue:
        sys.stderr.write("No issue found in event payload\n")
        return None

    repository = event.get("repository", {})
    repo_name = repository.get("name", "adt-community.github.io")

    task = parse_bounty_issue(issue, repo_name)
    if not task:
        sys.stdout.write("Issue is not a bounty task; skipping.\n")
        return None

    payload = create_webhook_payload(task)
    if dry_run:
        sys.stdout.write(f"[DRY-RUN] Issue payload generated:\n{json.dumps(payload, indent=2)}\n")
        return task

    if not webhook_url:
        sys.stderr.write("Error: DISCORD_WEBHOOK_URL required to post issue\n")
        return None

    success = send_discord_webhook(webhook_url, payload)
    return task if success else None


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="ADT Community Discord Bounty Feed Bot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: scan
    scan_parser = subparsers.add_parser("scan", help="Scan ADT repos for new bounties")
    scan_parser.add_argument("--webhook-url", default=os.getenv("DISCORD_WEBHOOK_URL"), help="Discord webhook URL")
    scan_parser.add_argument("--state-file", default=DEFAULT_STATE_FILE, help="Path to state cache file")
    scan_parser.add_argument("--dry-run", action="store_true", help="Print actions without posting")
    scan_parser.add_argument("--repos", nargs="*", help="Specific repos to scan (defaults to all)")

    # Subcommand: post-event
    event_parser = subparsers.add_parser("post-event", help="Handle a GitHub Actions event JSON file")
    event_parser.add_argument("--event-path", default=os.getenv("GITHUB_EVENT_PATH"), help="Path to GITHUB_EVENT_PATH")
    event_parser.add_argument("--webhook-url", default=os.getenv("DISCORD_WEBHOOK_URL"), help="Discord webhook URL")
    event_parser.add_argument("--dry-run", action="store_true", help="Print actions without posting")

    # Subcommand: test-message
    test_parser = subparsers.add_parser("test-message", help="Send a test message to the Discord webhook")
    test_parser.add_argument("--webhook-url", default=os.getenv("DISCORD_WEBHOOK_URL"), required=True, help="Discord webhook URL")

    args = parser.parse_args()

    if args.command == "scan":
        scan_and_post_bounties(
            webhook_url=args.webhook_url,
            repos=args.repos,
            state_file=args.state_file,
            dry_run=args.dry_run,
        )
    elif args.command == "post-event":
        if not args.event_path:
            sys.stderr.write("Error: --event-path or GITHUB_EVENT_PATH required\n")
            sys.exit(1)
        handle_github_event(
            event_path=args.event_path,
            webhook_url=args.webhook_url,
            dry_run=args.dry_run,
        )
    elif args.command == "test-message":
        test_task = {
            "title": "Welcome to the ADT Community Bounty Feed",
            "url": ADT_WORK_URL,
            "project": "ADT Community",
            "repo": "adt-community.github.io",
            "type": "Operations",
            "pay": "$20",
            "is_paid": True,
            "level": "Beginner",
            "time": "2–5 hours",
            "deliverable": "Automated bounty feed bot live in Discord",
            "done_when": "- [x] Bot posting tasks to channel\n- [x] Rich embed formatting",
            "assigned": False,
        }
        payload = create_webhook_payload(test_task, content="🤖 **ADT Bounty Feed Bot is live!**")
        success = send_discord_webhook(args.webhook_url, payload)
        if success:
            sys.stdout.write("Test message sent successfully!\n")
        else:
            sys.stderr.write("Failed to send test message.\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
