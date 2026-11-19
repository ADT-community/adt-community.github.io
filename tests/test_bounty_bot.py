"""Unit tests for the ADT Community Discord Bounty Feed Bot."""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from bot.bounty_bot import (
    extract_field,
    extract_section,
    get_label_names,
    is_bounty_issue,
    parse_bounty_issue,
    format_discord_embed,
    create_webhook_payload,
    send_discord_webhook,
    load_cache,
    save_cache,
    scan_and_post_bounties,
    handle_github_event,
    REPOS,
)


class TestBountyBot(unittest.TestCase):
    """Comprehensive unit test suite for bounty feed bot."""

    def setUp(self):
        self.sample_body = (
            "**Deliverable:** A Discord server and a weekly update habit.\n"
            "**Size:** about 6–10 hours · **Reward:** $20 · **Level:** Beginner\n\n"
            "### Why it matters\nMomentum is visible: people join communities that ship every week.\n\n"
            "### Done when\n"
            "- [ ] Server live with bounty feed\n"
            "- [ ] `docs/discord.md` and `docs/updates/` written\n\n"
            "### Not part of this task\nLong-term moderation.\n"
        )

        self.sample_issue = {
            "id": 1001,
            "number": 5,
            "title": "Community set-up: Discord and weekly updates",
            "html_url": "https://github.com/ADT-community/adt-community.github.io/issues/5",
            "body": self.sample_body,
            "labels": [{"name": "bounty:$20"}, {"name": "good first issue"}],
            "assignees": [],
            "created_at": "2026-11-19T18:00:00Z",
            "updated_at": "2026-11-19T18:05:00Z",
        }

    def test_extract_field(self):
        """Test extraction of bold markdown fields."""
        self.assertEqual(extract_field(self.sample_body, "Deliverable"), "A Discord server and a weekly update habit.")
        self.assertEqual(extract_field(self.sample_body, "Reward"), "$20")
        self.assertEqual(extract_field(self.sample_body, "Level"), "Beginner")
        self.assertEqual(extract_field(self.sample_body, "Size"), "about 6–10 hours")
        self.assertEqual(extract_field(self.sample_body, "Nonexistent"), "")
        self.assertEqual(extract_field("", "Level"), "")
        self.assertEqual(extract_field(None, "Level"), "")

    def test_extract_section(self):
        """Test extraction of markdown sections like 'Done when'."""
        done_when = extract_section(self.sample_body, "Done when")
        self.assertIn("- [ ] Server live with bounty feed", done_when)
        self.assertIn("- [ ] `docs/discord.md` and `docs/updates/` written", done_when)
        self.assertEqual(extract_section(self.sample_body, "Nonexistent"), "")
        self.assertEqual(extract_section("", "Done when"), "")
        self.assertEqual(extract_section(None, "Done when"), "")

    def test_get_label_names(self):
        """Test label normalization for dict and string formats."""
        issue_with_dicts = {"labels": [{"name": "bounty:$20"}, {"name": "beginner"}]}
        self.assertEqual(get_label_names(issue_with_dicts), ["bounty:$20", "beginner"])

        issue_with_strings = {"labels": ["bounty", "help wanted"]}
        self.assertEqual(get_label_names(issue_with_strings), ["bounty", "help wanted"])

        issue_empty = {"labels": []}
        self.assertEqual(get_label_names(issue_empty), [])

    def test_is_bounty_issue(self):
        """Test detection of bounty tasks vs normal issues or PRs."""
        self.assertTrue(is_bounty_issue(self.sample_issue))

        next_wave_issue = {"labels": [{"name": "next-wave"}]}
        self.assertTrue(is_bounty_issue(next_wave_issue))

        general_bounty = {"labels": [{"name": "bounty"}]}
        self.assertTrue(is_bounty_issue(general_bounty))

        pr_issue = {"labels": [{"name": "bounty:$20"}], "pull_request": {"url": "https://..."}}
        self.assertFalse(is_bounty_issue(pr_issue))

        regular_issue = {"labels": [{"name": "bug"}, {"name": "enhancement"}]}
        self.assertFalse(is_bounty_issue(regular_issue))

    def test_parse_bounty_issue(self):
        """Test parsing of GitHub issues into structured bounty tasks."""
        task = parse_bounty_issue(self.sample_issue, "adt-community.github.io")
        self.assertIsNotNone(task)
        self.assertEqual(task["id"], 1001)
        self.assertEqual(task["number"], 5)
        self.assertEqual(task["title"], "Community set-up: Discord and weekly updates")
        self.assertEqual(task["repo"], "adt-community.github.io")
        self.assertEqual(task["project"], "ADT Community")
        self.assertEqual(task["type"], "Operations")
        self.assertEqual(task["pay"], "$20")
        self.assertTrue(task["is_paid"])
        self.assertEqual(task["level"], "Beginner")
        self.assertEqual(task["time"], "about 6–10 hours")
        self.assertEqual(task["deliverable"], "A Discord server and a weekly update habit.")
        self.assertFalse(task["assigned"])

    def test_parse_bounty_issue_types(self):
        """Test task type determination for different repositories and labels."""
        design_issue = {
            "title": "Design new landing page",
            "labels": [{"name": "bounty:$50"}, {"name": "design"}],
            "body": "**Level:** Intermediate · **Time:** 3 hours",
        }
        task_design = parse_bounty_issue(design_issue, "trans_sport")
        self.assertEqual(task_design["type"], "Design")
        self.assertEqual(task_design["project"], "Minibus app")

        research_issue = {
            "title": "Research mobile money APIs",
            "labels": [{"name": "bounty:$30"}, {"name": "research"}],
            "body": "",
        }
        task_research = parse_bounty_issue(research_issue, "locallity_ai")
        self.assertEqual(task_research["type"], "Research")

        code_issue = {
            "title": "Build WhatsApp voice bot bridge",
            "labels": [{"name": "next-wave"}],
            "body": "",
        }
        task_code = parse_bounty_issue(code_issue, "locallity_ai")
        self.assertEqual(task_code["type"], "Code")
        self.assertEqual(task_code["pay"], "Next wave")
        self.assertFalse(task_code["is_paid"])

    def test_format_discord_embed(self):
        """Test Discord embed generation formatting and colors."""
        task = parse_bounty_issue(self.sample_issue, "adt-community.github.io")
        embed = format_discord_embed(task)

        self.assertIn("🎯 New Task:", embed["title"])
        self.assertEqual(embed["url"], self.sample_issue["html_url"])
        self.assertEqual(embed["color"], 0x2ECC71)  # Green for paid bounties
        self.assertIn("ADT Community", embed["footer"]["text"])

        field_names = [f["name"] for f in embed["fields"]]
        self.assertIn("💰 Reward", field_names)
        self.assertIn("📦 Project", field_names)
        self.assertIn("🏷️ Type", field_names)
        self.assertIn("🎯 Level", field_names)
        self.assertIn("⏱️ Time", field_names)
        self.assertIn("🚀 How to claim", field_names)

        # Test next wave embed color
        next_wave_task = {
            "title": "Next Wave Task",
            "url": "https://...",
            "repo": "content_feed",
            "project": "Creator social app",
            "is_paid": False,
            "pay": "Next wave",
        }
        embed_nw = format_discord_embed(next_wave_task)
        self.assertEqual(embed_nw["color"], 0x3498DB)  # Blue for next wave

    def test_create_webhook_payload(self):
        """Test full webhook JSON payload generation."""
        task = parse_bounty_issue(self.sample_issue, "adt-community.github.io")
        payload = create_webhook_payload(task, content="📢 New bounty available!")

        self.assertEqual(payload["username"], "ADT Bounty Feed")
        self.assertIn("embeds", payload)
        self.assertEqual(len(payload["embeds"]), 1)
        self.assertEqual(payload["content"], "📢 New bounty available!")

    @patch("urllib.request.urlopen")
    def test_send_discord_webhook_success(self, mock_urlopen):
        """Test successful HTTP POST to Discord webhook."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 204
        mock_urlopen.return_value.__enter__.return_value = mock_response

        payload = {"content": "Hello Discord"}
        success = send_discord_webhook("https://discord.com/api/webhooks/test", payload)
        self.assertTrue(success)

    @patch("urllib.request.urlopen")
    def test_send_discord_webhook_http_error(self, mock_urlopen):
        """Test webhook handling of HTTP errors."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://discord.com/api/webhooks/test",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=None,
        )
        payload = {"content": "Bad payload"}
        success = send_discord_webhook("https://discord.com/api/webhooks/test", payload)
        self.assertFalse(success)

    def test_cache_save_and_load(self):
        """Test caching mechanism for deduplication."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "cache.json")
            initial = load_cache(cache_file)
            self.assertEqual(initial, set())

            save_cache(cache_file, {"1001", "1002"})
            loaded = load_cache(cache_file)
            self.assertEqual(loaded, {"1001", "1002"})

    @patch("bot.bounty_bot.fetch_repo_issues")
    def test_scan_and_post_bounties_dry_run(self, mock_fetch):
        """Test scanning repos and dry-run output."""
        mock_fetch.return_value = [self.sample_issue]

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "cache.json")
            posted = scan_and_post_bounties(
                webhook_url=None,
                repos=["adt-community.github.io"],
                state_file=cache_file,
                dry_run=True,
            )
            self.assertEqual(len(posted), 1)
            self.assertEqual(posted[0]["id"], 1001)

            # Second scan should recognize as posted in memory cache
            posted_again = scan_and_post_bounties(
                webhook_url=None,
                repos=["adt-community.github.io"],
                state_file=cache_file,
                dry_run=True,
            )
            self.assertEqual(len(posted_again), 1)

    def test_handle_github_event(self):
        """Test handling GitHub Actions event JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            event_file = os.path.join(tmpdir, "event.json")
            event_data = {
                "action": "opened",
                "issue": self.sample_issue,
                "repository": {"name": "adt-community.github.io"},
            }
            with open(event_file, "w", encoding="utf-8") as f:
                json.dump(event_data, f)

            task = handle_github_event(event_file, webhook_url=None, dry_run=True)
            self.assertIsNotNone(task)
            self.assertEqual(task["id"], 1001)


if __name__ == "__main__":
    unittest.main()
