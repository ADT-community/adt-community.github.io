"""Tests for the Discord new-task feed (standard library only)."""

import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from discord_bot import post_tasks as bot  # noqa: E402


class FakeResponse:
    def __init__(self, status=204):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeOpener:
    def __init__(self, status=204, error=None):
        self.status = status
        self.error = error
        self.requests = []

    def urlopen(self, request, timeout=None):
        self.requests.append((request, timeout))
        if self.error is not None:
            raise self.error
        return FakeResponse(self.status)


def sample_task(identifier="ops-5", status="open", **extra):
    task = {
        "id": identifier,
        "title": "Community set-up",
        "project": "ADT Work & community",
        "reward": 20,
        "paid": True,
        "level": "Beginner",
        "hours": "6-10",
        "deliverable": "A Discord server and a weekly update habit.",
        "status": status,
    }
    task.update(extra)
    return task


class TempMixin:
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tasks_path = Path(self.tmp.name) / "tasks.json"
        self.state_path = Path(self.tmp.name) / "state.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write_tasks(self, tasks, updated="2026-11-21"):
        self.tasks_path.write_text(
            json.dumps({"updated": updated, "tasks": tasks}), encoding="utf-8"
        )


class LoadTests(TempMixin, unittest.TestCase):
    def test_load_tasks(self):
        self.write_tasks([sample_task(), sample_task("ts-4", status="done")])
        self.assertEqual([bot.task_id(t) for t in bot.load_tasks(self.tasks_path)],
                         ["ops-5", "ts-4"])

    def test_load_tasks_missing_file(self):
        with self.assertRaises(bot.FeedError):
            bot.load_tasks(Path(self.tmp.name) / "missing.json")

    def test_load_tasks_bad_json_and_shape(self):
        self.tasks_path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(bot.FeedError):
            bot.load_tasks(self.tasks_path)
        self.tasks_path.write_text('{"updated": "2026-11-21"}', encoding="utf-8")
        with self.assertRaises(bot.FeedError):
            bot.load_tasks(self.tasks_path)

    def test_state_roundtrip_and_missing(self):
        self.assertEqual(bot.load_state(self.state_path), set())
        bot.save_state(self.state_path, {"b", "a"}, updated="2026-11-21")
        self.assertEqual(bot.load_state(self.state_path), {"a", "b"})
        self.assertEqual(json.loads(self.state_path.read_text(encoding="utf-8"))["updated"],
                         "2026-11-21")

    def test_state_corrupt(self):
        self.state_path.write_text('{"posted": [1]}', encoding="utf-8")
        with self.assertRaises(bot.FeedError):
            bot.load_state(self.state_path)

    def test_repository_tasks_are_valid(self):
        tasks = bot.load_tasks(bot.DEFAULT_TASKS)
        ids = [bot.task_id(task) for task in tasks]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)), "task ids must be unique")
        self.assertTrue(all(ids))
        self.assertTrue(any(bot.is_open(task) for task in tasks))


class SelectionTests(unittest.TestCase):
    def test_filters_closed_posted_duplicates_and_applies_limit(self):
        tasks = [
            sample_task("a"),
            sample_task("b", status="taken"),
            sample_task("a"),
            sample_task("c"),
            sample_task("d"),
        ]
        selected = bot.select_new_tasks(tasks, {"a"}, limit=1)
        self.assertEqual([bot.task_id(t) for t in selected], ["c"])
        self.assertEqual([bot.task_id(t) for t in bot.select_new_tasks(tasks, set(), 3)],
                         ["a", "c", "d"])

    def test_zero_and_negative_limit(self):
        tasks = [sample_task("a")]
        self.assertEqual(bot.select_new_tasks(tasks, set(), 0), [])
        with self.assertRaises(bot.FeedError):
            bot.select_new_tasks(tasks, set(), -1)

    def test_embed_fields_and_link(self):
        embed = bot.format_embed(sample_task())
        self.assertIn("ops-5", embed["title"])
        self.assertEqual(embed["url"],
                         "https://adt-community.github.io/task.html?id=ops-5")
        self.assertEqual(embed["description"], "A Discord server and a weekly update habit.")
        fields = {field["name"]: field["value"] for field in embed["fields"]}
        self.assertEqual(fields["Pay"], "$20")
        self.assertEqual(fields["Project"], "ADT Work & community")
        self.assertEqual(fields["Level"], "Beginner")

    def test_unpaid_task_and_long_text(self):
        embed = bot.format_embed(sample_task(paid=False, reward=0, deliverable="x" * 5000))
        fields = {field["name"]: field["value"] for field in embed["fields"]}
        self.assertEqual(fields["Pay"], "Unpaid")
        self.assertEqual(len(embed["description"]), bot.MAX_DESCRIPTION)

    def test_webhook_validation(self):
        good = "https://discord.com/api/webhooks/123/abc"
        self.assertTrue(bot.webhook_allowed(good))
        self.assertTrue(bot.webhook_allowed(good.replace("discord.com", "discordapp.com")))
        for bad in ("http://discord.com/api/webhooks/123/abc",
                    "https://example.com/api/webhooks/123/abc",
                    "https://discord.com/api/channels/123", ""):
            self.assertFalse(bot.webhook_allowed(bad))


class PostTests(TempMixin, unittest.TestCase):
    WEBHOOK = "https://discord.com/api/webhooks/123/abc"

    def test_post_embed_success_payload(self):
        opener = FakeOpener(status=204)
        self.assertTrue(bot.post_embed(self.WEBHOOK, bot.format_embed(sample_task()),
                                       opener=opener, timeout=3))
        request, timeout = opener.requests[0]
        self.assertEqual(timeout, 3)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["username"], "ADT Tasks")
        self.assertEqual(payload["embeds"][0]["url"], bot.task_url(sample_task()))

    def test_post_embed_http_and_network_errors(self):
        error = urllib.error.HTTPError(self.WEBHOOK, 429, "rate limit", {}, None)
        self.assertFalse(bot.post_embed(self.WEBHOOK, {}, opener=FakeOpener(error=error)))
        self.assertFalse(bot.post_embed(self.WEBHOOK, {},
                                        opener=FakeOpener(error=OSError("offline"))))

    def test_post_embed_rejects_wrong_host(self):
        with self.assertRaises(bot.FeedError):
            bot.post_embed("https://example.com/api/webhooks/1/2", {})

    def test_dry_run_changes_nothing(self):
        self.write_tasks([sample_task()])
        opener = FakeOpener()
        output = []
        summary = bot.run_once(self.tasks_path, self.state_path, self.WEBHOOK,
                               dry_run=True, opener=opener, emit=output.append)
        self.assertEqual(summary["would_post"], 1)
        self.assertEqual(summary["posted"], 0)
        self.assertFalse(opener.requests)
        self.assertFalse(self.state_path.exists())
        self.assertIn("ops-5", output[0])

    def test_posts_and_persists_state(self):
        self.write_tasks([sample_task("a"), sample_task("b"), sample_task("c", "done")])
        opener = FakeOpener()
        summary = bot.run_once(self.tasks_path, self.state_path, self.WEBHOOK,
                               limit=5, opener=opener)
        self.assertEqual(summary["posted"], 2)
        self.assertEqual(len(opener.requests), 2)
        self.assertEqual(bot.load_state(self.state_path), {"a", "b"})
        again = bot.run_once(self.tasks_path, self.state_path, self.WEBHOOK, opener=opener)
        self.assertEqual(again["posted"], 0)
        self.assertEqual(len(opener.requests), 2)

    def test_failed_post_does_not_advance_state(self):
        self.write_tasks([sample_task("a")])
        opener = FakeOpener(error=OSError("offline"))
        summary = bot.run_once(self.tasks_path, self.state_path, self.WEBHOOK, opener=opener)
        self.assertEqual(summary["failed"], ["a"])
        self.assertEqual(summary["posted"], 0)
        self.assertFalse(self.state_path.exists())

    def test_bootstrap_marks_without_posting(self):
        self.write_tasks([sample_task("a"), sample_task("b", "taken")])
        opener = FakeOpener()
        summary = bot.run_once(self.tasks_path, self.state_path, self.WEBHOOK,
                               bootstrap=True, opener=opener)
        self.assertEqual(summary["bootstrapped"], 1)
        self.assertEqual(bot.load_state(self.state_path), {"a"})
        self.assertFalse(opener.requests)

    def test_no_webhook_is_skipped_not_failed(self):
        self.write_tasks([sample_task()])
        summary = bot.run_once(self.tasks_path, self.state_path, "", opener=FakeOpener())
        self.assertTrue(summary["skipped_no_webhook"])
        self.assertEqual(summary["failed"], [])
        self.assertFalse(self.state_path.exists())

    def test_main_without_webhook_is_green(self):
        self.write_tasks([sample_task()])
        with mock.patch.dict("os.environ", {"DISCORD_WEBHOOK_URL": ""}, clear=False):
            code = bot.main(["--tasks", str(self.tasks_path),
                             "--state-file", str(self.state_path)])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
