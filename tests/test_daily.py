"""Offline tests. Git remotes are local temporary directories; Telegram transport is fake."""
from collections import Counter
from contextlib import redirect_stdout
import copy
from datetime import date, timedelta
from email.message import Message
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from scripts import daily

DAY = "2026-11-11"
DE, EN = daily.CHANNELS.values()


def new_state():
    return {"schema": 1, "legacy_through": "2026-11-10", "days": {}}


class MemoryJournal:
    def __init__(self, state=None, fail_at=None):
        self.durable = copy.deepcopy(new_state() if state is None else state)
        self.state = copy.deepcopy(self.durable)
        self.saves = 0
        self.fail_at = fail_at

    def save(self, label):
        self.saves += 1
        if self.saves == self.fail_at:
            raise RuntimeError("ledger write failed")
        self.durable = copy.deepcopy(self.state)


def run(journal, send, day=DAY, topics=None, today=None):
    with redirect_stdout(io.StringIO()):
        daily.publish(topics or daily.load_catalog(), journal, day, send, today or (lambda: day))


class CatalogTests(unittest.TestCase):
    def test_catalog_scope_and_rendered_messages(self):
        topics = daily.load_catalog()
        self.assertGreaterEqual(len(topics), 30)
        counts = Counter(t["category"] for t in topics)
        self.assertEqual(set(counts), daily.CATEGORIES)
        self.assertGreaterEqual(min(counts.values()), 5)
        for t in topics:
            for lang in daily.CHANNELS:
                with self.subTest(topic=t["id"], lang=lang):
                    text = daily.render(t, lang)
                    self.assertIn(t["source"], text)
                    self.assertIn(t[lang]["question"], text)
                    self.assertIn(daily.FOOTERS[lang], text)
                    self.assertLessEqual(len(text.encode("utf-16-le")) // 2, 4096)
            self.assertNotEqual(t["de"]["body"], t["en"]["body"])

    def test_source_copy_and_utf16_limit_checked_before_any_send(self):
        for edit in (lambda t: t.update(source="http://example.com"),
                     lambda t: t["en"].update(body=" "),
                     lambda t: t["de"].update(body="🔎" * 2049)):
            t = daily.load_catalog()[0]
            edit(t)
            with self.assertRaises(daily.InvalidData):
                daily.check_unique([t])

    def test_new_title_id_and_link_cannot_disguise_same_body(self):
        t = daily.load_catalog()[0]
        duplicate = copy.deepcopy(t)
        duplicate.update(id="another-id", source="https://example.com")
        duplicate["en"].update(title="New title", body="  " + t["en"]["body"].upper())
        duplicate["de"]["body"] = "Anderer Text"
        with self.assertRaisesRegex(daily.InvalidData, "Repeated"):
            daily.check_unique([t, duplicate])

    def test_default_preview_and_named_preview_never_open_network_or_state(self):
        for args in ([], ["--preview", "bitcoin-change"]):
            with patch("sys.argv", ["daily.py", *args]), patch.object(daily, "GitJournal") as ledger, \
                    patch.object(daily, "build_opener") as http, redirect_stdout(io.StringIO()) as buf:
                daily.main()
                self.assertIn(DE, buf.getvalue())
                self.assertIn(EN, buf.getvalue())
                ledger.assert_not_called()
                http.assert_not_called()


class DeliveryTests(unittest.TestCase):
    def test_restart_same_day_is_a_noop_across_both_channels(self):
        first = MemoryJournal()
        send = Mock(side_effect=[71, 72])
        run(first, send)
        run(MemoryJournal(first.durable), send)
        self.assertEqual([c.args[0] for c in send.call_args_list], [DE, EN])
        slots = first.durable["days"][DAY]["delivery"]
        self.assertEqual([slots[lang]["message_id"] for lang in ("de", "en")], [71, 72])

    def test_definite_rejection_retries_only_missing_channel(self):
        j = MemoryJournal()
        send = Mock(side_effect=[101, daily.Rejected("429"), 202])
        with self.assertRaisesRegex(RuntimeError, "429"):
            run(j, send)
        run(MemoryJournal(j.durable), send)
        self.assertEqual([x.args[0] for x in send.call_args_list], [DE, EN, EN])

    def test_ambiguous_de_does_not_block_en_or_resend_de(self):
        j = MemoryJournal()
        send = Mock(side_effect=[daily.Unconfirmed("timeout"), 42])
        with self.assertRaisesRegex(RuntimeError, "unconfirmed"):
            run(j, send)
        with self.assertRaisesRegex(RuntimeError, "unresolved"):
            run(MemoryJournal(j.durable), send)
        self.assertEqual([c.args[0] for c in send.call_args_list], [DE, EN])
        self.assertEqual(j.durable["days"][DAY]["delivery"]["de"]["status"], "reserved")

    def test_failure_to_save_claim_means_zero_sends(self):
        j = MemoryJournal(fail_at=1)
        send = Mock()
        with self.assertRaisesRegex(RuntimeError, "ledger write"):
            run(j, send)
        send.assert_not_called()
        self.assertFalse(j.durable["days"])

    def test_crash_before_confirming_success_does_not_replay(self):
        j = MemoryJournal(fail_at=2)
        send = Mock(side_effect=[13, 14])
        with self.assertRaisesRegex(RuntimeError, "ledger write"):
            run(j, send)
        with self.assertRaisesRegex(RuntimeError, "unresolved"):
            run(MemoryJournal(j.durable), send)
        self.assertEqual([c.args[0] for c in send.call_args_list], [DE, EN])

    def test_pre_send_crash_can_leave_one_gap_but_never_replays(self):
        j = MemoryJournal()
        with self.assertRaises(KeyboardInterrupt):
            run(j, Mock(side_effect=KeyboardInterrupt()))
        send = Mock(return_value=22)
        with self.assertRaisesRegex(RuntimeError, "unresolved"):
            run(MemoryJournal(j.durable), send)
        self.assertEqual([c.args[0] for c in send.call_args_list], [EN])

    def test_recovery_uses_frozen_translation_even_when_topic_removed(self):
        catalog = daily.load_catalog()
        j = MemoryJournal()
        with self.assertRaises(RuntimeError):
            run(j, Mock(side_effect=[71, daily.Rejected("403")]), topics=catalog)
        send = Mock(return_value=72)
        run(MemoryJournal(j.durable), send, topics=catalog[1:])
        send.assert_called_once_with(EN, daily.render(catalog[0], "en"))

    def test_exhaustion_no_recycling_and_new_topic_unblocks_next_run(self):
        j = MemoryJournal()
        send = Mock(return_value=7)
        start = date.fromisoformat(DAY)
        catalog = daily.load_catalog()
        for n in range(len(catalog)):
            run(j, send, (start + timedelta(days=n)).isoformat(), catalog)
        self.assertEqual([entry["topic"]["id"] for entry in j.durable["days"].values()],
                         [t["id"] for t in catalog])
        end = (start + timedelta(days=len(catalog))).isoformat()
        alias = copy.deepcopy(catalog[0])
        alias["id"] = "reused-body"
        with self.assertRaisesRegex(RuntimeError, "exhausted"):
            run(j, send, end, [alias])
        self.assertEqual(send.call_count, len(catalog) * 2)
        fresh = copy.deepcopy(alias)
        fresh["id"] = "fresh"
        for lang in daily.CHANNELS:
            fresh[lang]["body"] = "Fresh test copy in " + lang
        run(j, send, end, [alias, fresh])
        self.assertEqual(j.durable["days"][end]["topic"]["id"], "fresh")

    def test_cutover_and_expired_run_are_skipped(self):
        j = MemoryJournal()
        send = Mock()
        run(j, send, day="2026-11-10")
        run(j, send, today=lambda: "2026-11-12")
        self.assertEqual(j.saves, 0)
        send.assert_not_called()

    def test_next_day_uses_next_topic_without_backfilling_failed_language(self):
        j = MemoryJournal()
        with self.assertRaises(RuntimeError):
            run(j, Mock(side_effect=[1, daily.Unconfirmed("timeout")]))
        send = Mock(return_value=2)
        run(MemoryJournal(j.durable), send, day="2026-11-14")
        self.assertEqual(send.call_count, 2)
        self.assertIn(daily.load_catalog()[1]["de"]["title"], send.call_args_list[0].args[1])

    def test_midnight_between_claim_and_send_blocks_expired_post(self):
        j = MemoryJournal()
        send = Mock()
        clock = Mock(side_effect=[DAY, DAY, "2026-11-12"])
        with self.assertRaisesRegex(RuntimeError, "expired"):
            run(j, send, today=clock)
        send.assert_not_called()
        self.assertEqual(j.durable["days"][DAY]["delivery"]["de"]["status"], "skipped")

    def test_brussels_calendar_day_in_winter_and_summer(self):
        self.assertEqual(daily.run_day("2026-11-10T23:15:00Z"), DAY)
        self.assertEqual(daily.run_day("2026-06-15T22:15:00+00:00"), "2026-06-16")
        with self.assertRaises(daily.InvalidData):
            daily.run_day("2026-11-10T23:15:00")

    def test_corrupt_channel_entry_halts_before_sending(self):
        j = MemoryJournal()
        run(j, Mock(return_value=9))
        del j.state["days"][DAY]["delivery"]["de"]
        send = Mock()
        with self.assertRaises(daily.InvalidData):
            run(j, send)
        send.assert_not_called()

    def test_duplicate_json_keys_are_not_silently_overwritten(self):
        with self.assertRaisesRegex(daily.InvalidData, "Duplicate"):
            json.loads('{"de":"sent","de":"pending"}', object_pairs_hook=daily.unique_keys)


class TransportTests(unittest.TestCase):
    def test_receipt_binds_channel_and_positive_message_id(self):
        result = {"ok": True, "result": {"message_id": 33, "chat": {"type": "channel", "username": DE[1:]}}}
        with patch.object(daily, "build_opener") as opener:
            opener.return_value.open.return_value = io.BytesIO(json.dumps(result).encode())
            self.assertEqual(daily.telegram_send("test", DE, "Example"), 33)
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(request.get_method(), "POST")
            self.assertIn(b"%40MarketPulseEliteDE", request.data)
        for bad in (dict(result["result"], message_id=0), dict(result["result"], message_id=True),
                    dict(result["result"], chat={"type": "channel", "username": "Wrong"})):
            with patch.object(daily, "build_opener") as opener:
                opener.return_value.open.return_value = io.BytesIO(json.dumps({"ok": True, "result": bad}).encode())
                with self.assertRaises(daily.Unconfirmed):
                    daily.telegram_send("test", DE, "Example")

    def test_definite_telegram_4xx_vs_ambiguous_http_errors(self):
        for code, body, expected in [(429, b'{"ok":false,"error_code":429}', daily.Rejected),
                                     (403, b'{"ok":false,"error_code":403}', daily.Rejected),
                                     (500, b'{"ok":false,"error_code":500}', daily.Unconfirmed),
                                     (429, b"bad gateway", daily.Unconfirmed),
                                     (401, b'{"ok":false,"error_code":400}', daily.Unconfirmed),
                                     (302, b"", daily.Unconfirmed)]:
            with self.subTest(code=code, body=body), patch.object(daily, "build_opener") as opener:
                opener.return_value.open.side_effect = HTTPError("https://invalid", code, "test", Message(),
                                                                 io.BytesIO(body))
                with self.assertRaises(expected):
                    daily.telegram_send("test", DE, "Example")
                self.assertEqual(opener.return_value.open.call_count, 1)

    def test_timeout_and_malformed_200_keep_reservation(self):
        with patch.object(daily, "build_opener") as opener:
            opener.return_value.open.side_effect = TimeoutError()
            with self.assertRaises(daily.Unconfirmed):
                daily.telegram_send("test", DE, "Example")
        with patch.object(daily, "build_opener") as opener:
            opener.return_value.open.return_value = io.BytesIO(b"not JSON")
            with self.assertRaises(daily.Unconfirmed):
                daily.telegram_send("test", DE, "Example")


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class GitJournalTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.bare = self.root / "origin.git"
        git(self.root, "init", "--bare", "-b", "marketpulse-state", str(self.bare))
        self.a = self.root / "a"
        git(self.root, "clone", str(self.bare), str(self.a))
        (self.a / "ledger.json").write_text(json.dumps(new_state()), encoding="utf-8")
        git(self.a, "add", "ledger.json")
        git(self.a, "-c", "user.email=tests@example.invalid", "-c", "user.name=Tests", "commit", "-m", "seed")
        git(self.a, "push", "origin", "HEAD:refs/heads/marketpulse-state")
        self.b = self.root / "b"
        git(self.root, "clone", "--depth", "1", self.bare.as_uri(), str(self.b))
        git(self.b, "checkout", "--detach")

    def test_publish_entry_point_with_local_git_and_fake_transport(self):
        env = {"GITHUB_ACTIONS": "true", "GITHUB_REF": "refs/heads/main",
               "GITHUB_EVENT_NAME": "workflow_dispatch", "TELEGRAM_BOT_TOKEN": "unused-test-value",
               "RUN_CREATED_AT": "2026-11-11T07:13:00Z"}
        # Inject the calendar date explicitly while using the real parser, journal and publish loop.
        real_publish = daily.publish
        def fixed_day(topics, journal, day, send):
            return real_publish(topics, journal, day, send, lambda: DAY)
        with patch.dict(daily.os.environ, env, clear=True), patch("sys.argv", [
                "daily.py", "--publish", "--state-dir", str(self.b)]), patch.object(
                daily, "telegram_send", side_effect=[11, 12]) as send, patch.object(
                daily, "publish", side_effect=fixed_day), redirect_stdout(io.StringIO()):
            daily.main()
            daily.main()
        self.assertEqual([call.args[1] for call in send.call_args_list], [DE, EN])

    def test_live_entry_point_refuses_non_main(self):
        env = {"GITHUB_ACTIONS": "true", "GITHUB_REF": "refs/heads/review",
               "GITHUB_EVENT_NAME": "workflow_dispatch"}
        with patch.dict(daily.os.environ, env, clear=True), patch("sys.argv", [
                "daily.py", "--publish", "--state-dir", str(self.b)]), patch.object(
                daily, "telegram_send") as send, self.assertRaises(daily.InvalidData):
            daily.main()
        send.assert_not_called()

    def test_two_runners_same_parent_cannot_both_send(self):
        # Run the second stale clone after the first reservation, before its caller gets a receipt.
        first, stale = daily.GitJournal(self.a), daily.GitJournal(self.b)
        losing_send = Mock()
        def winning_send(channel, message):
            if channel == DE:
                with self.assertRaisesRegex(RuntimeError, "push failed"):
                    run(stale, losing_send)
            return 101
        run(first, winning_send)
        losing_send.assert_not_called()
        ledger = json.loads(git(self.bare, "show", "HEAD:ledger.json"))
        self.assertEqual(ledger["days"][DAY]["delivery"]["en"]["message_id"], 101)

    def test_shallow_detached_checkout_persists_across_fresh_clone(self):
        run(daily.GitJournal(self.b), Mock(side_effect=[41, 42]))
        git(self.a, "pull", "--ff-only", "origin", "marketpulse-state")
        send = Mock()
        run(daily.GitJournal(self.a), send)
        send.assert_not_called()

    def test_missing_ledger_cannot_bootstrap_itself(self):
        (self.b / "ledger.json").unlink()
        with self.assertRaisesRegex(daily.InvalidData, "Dirty"):
            daily.GitJournal(self.b)

    def test_deleted_remote_branch_is_not_recreated_by_a_stale_claim(self):
        j = daily.GitJournal(self.b)
        git(self.bare, "update-ref", "-d", daily.STATE_REF)
        send = Mock()
        with self.assertRaisesRegex(RuntimeError, "push failed"):
            run(j, send)
        send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
