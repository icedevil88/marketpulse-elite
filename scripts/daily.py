"""Publish curated bilingual Telegram lessons. Running without arguments is offline."""
import argparse
from datetime import date, datetime
from http.client import HTTPException
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request
from uuid import uuid4
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "content/education.json"
ZONE = ZoneInfo("Europe/Brussels")
STATE_REF = "refs/heads/marketpulse-state"
CHANNELS = {"de": "@MarketPulseEliteDE", "en": "@MarketPulseEliteGlobal"}
CATEGORIES = {"equity", "valuation", "crypto", "risk", "literacy"}
FOOTERS = {
    "de": "Finanzbildung · Keine persönliche Anlageberatung.",
    "en": "Financial education · Not personalized investment advice.",
}
SOURCE_LABEL = {"de": "Quelle", "en": "Source"}


class InvalidData(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidData(message)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def render(topic, lang):
    post = topic[lang]
    return "\n\n".join((post["title"], post["body"], post["question"],
                        SOURCE_LABEL[lang] + "\n" + topic["source"], FOOTERS[lang]))


def fingerprints(topic):
    # Only the lesson body counts. Retitling, relinking or reformatting is not a new lesson.
    return {(lang, " ".join(unicodedata.normalize("NFKC", topic[lang]["body"]).casefold().split()))
            for lang in CHANNELS}


def validate_topic(topic):
    require(isinstance(topic, dict) and set(topic) == {"id", "category", "source", *CHANNELS},
            "Invalid topic fields")
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", topic["id"]), "Invalid topic ID")
    require(topic["category"] in CATEGORIES, "Unknown category")
    url = urlsplit(topic["source"])
    require(url.scheme == "https" and url.hostname and not url.username, "Invalid source URL")
    for lang in CHANNELS:
        post = topic[lang]
        require(isinstance(post, dict) and set(post) == {"title", "body", "question"},
                f"Missing copy in {topic['id']}/{lang}")
        require(all(isinstance(value, str) and value.strip() for value in post.values()),
                "Empty post field")
        require(len(render(topic, lang).encode("utf-16-le")) // 2 <= 4096, "Post too long")


def check_unique(topics):
    ids, texts = set(), set()
    for topic in topics:
        validate_topic(topic)
        bodies = fingerprints(topic)
        require(topic["id"] not in ids and texts.isdisjoint(bodies), "Repeated ID or lesson body")
        ids.add(topic["id"])
        texts.update(bodies)
    return ids, texts


def load_catalog():
    topics = read_json(CATALOG)
    require(isinstance(topics, list) and topics, "Empty catalog")
    check_unique(topics)
    return topics


def valid_day(value):
    return isinstance(value, str) and date.fromisoformat(value).isoformat() == value


def validate_journal(state):
    require(set(state) == {"schema", "legacy_through", "days"} and type(state["schema"]) is int
            and state["schema"] == 1, "Unknown ledger schema")
    require(valid_day(state["legacy_through"]) and isinstance(state["days"], dict),
            "Invalid cutover or ledger dates")
    for day, entry in state["days"].items():
        require(valid_day(day) and day > state["legacy_through"], "Invalid publication day")
        require(set(entry) == {"topic", "delivery"} and set(entry["delivery"]) == set(CHANNELS),
                "Incomplete ledger entry")
        for slot in entry["delivery"].values():
            status = slot.get("status")
            require(status in {"pending", "reserved", "sent", "skipped"}, "Unknown delivery state")
            expected = {"status"}
            if status in {"reserved", "sent", "skipped"}:
                expected.add("claim")
                require(re.fullmatch(r"[a-f0-9]{32}", slot.get("claim", "")), "Missing claim")
            if status == "sent":
                expected.add("message_id")
                require(type(slot.get("message_id")) is int and slot["message_id"] > 0,
                        "Missing receipt")
            require(set(slot) == expected, "Unexpected delivery fields")
    return check_unique(entry["topic"] for entry in state["days"].values())


class GitJournal:
    """Each change is a direct child of the last local HEAD; the remote must still match it."""
    def __init__(self, directory):
        self.directory = directory.resolve()
        require(Path(self.git("rev-parse", "--show-toplevel")).resolve() == self.directory,
                "Expected a dedicated state checkout")
        require(not self.git("status", "--porcelain", "--untracked-files=no"), "Dirty ledger checkout")
        self.git("ls-files", "--error-unmatch", "ledger.json")
        self.path = self.directory / "ledger.json"
        self.state = read_json(self.path)
        validate_journal(self.state)

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.directory, capture_output=True, text=True)
        if result.returncode:
            # Do not log the remote URL, credentials or child diagnostics.
            raise RuntimeError(f"Ledger git {args[0]} failed; inspect remote state before retrying")
        return result.stdout.strip()

    def save(self, label):
        parent = self.git("rev-parse", "HEAD")
        self.path.write_text(json.dumps(self.state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self.git("-c", "user.name=MarketPulse publisher", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                 "commit", "--only", "-m", label, "--", "ledger.json")
        # A lease also prevents silently re-creating a concurrently deleted state branch.
        self.git("push", f"--force-with-lease={STATE_REF}:{parent}", "origin", f"HEAD:{STATE_REF}")


class Rejected(RuntimeError):
    """A structured, definitive Bot API rejection. Another run may retry this channel."""


class Unconfirmed(RuntimeError):
    """No reliable receipt. The durable reservation must survive."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def telegram_send(token, channel, message):
    data = urlencode({"chat_id": channel, "text": message,
                      "link_preview_options": '{"is_disabled":true}'}).encode()
    request = Request("https://api.telegram.org/bot" + token + "/sendMessage", data=data)
    try:
        with build_opener(NoRedirect()).open(request, timeout=20) as response:
            result = json.load(response)
    except HTTPError as error:
        try:
            with error:
                payload = json.load(error)
            if (error.code in {400, 401, 403, 404, 429} and isinstance(payload, dict)
                    and payload.get("ok") is False and payload.get("error_code") == error.code):
                raise Rejected(f"Telegram rejected request (HTTP {error.code})") from None
        except (ValueError, OSError, HTTPException):
            pass
        raise Unconfirmed("Unconfirmed HTTP response") from None
    except (ValueError, OSError, URLError, HTTPException):
        raise Unconfirmed("Unconfirmed transport or response") from None
    msg = result.get("result") if isinstance(result, dict) else None
    if not isinstance(msg, dict) or result.get("ok") is not True:
        raise Unconfirmed("Missing Telegram receipt")
    mid = msg.get("message_id")
    chat = msg.get("chat")
    if (type(mid) is not int or mid <= 0 or not isinstance(chat, dict)
            or chat.get("type") != "channel"
            or str(chat.get("username", "")).casefold() != channel[1:].casefold()):
        raise Unconfirmed("Unexpected channel or message ID")
    return mid


def run_day(created_at):
    moment = datetime.fromisoformat(created_at)
    require(moment.utcoffset() is not None, "Run creation time must include a UTC offset")
    return moment.astimezone(ZONE).date().isoformat()


def brussels_today():
    return datetime.now(ZONE).date().isoformat()


def publish(topics, journal, day, send, today=brussels_today):
    state = journal.state
    used_ids, used_text = validate_journal(state)
    if day != today() or day <= state["legacy_through"]:
        print(f"{day} outside current eligible day; skipped")
        return
    entry = state["days"].get(day)
    if entry is None:
        available = [t for t in topics if t["id"] not in used_ids and used_text.isdisjoint(fingerprints(t))]
        if not available:
            raise RuntimeError("Catalog exhausted. Add reviewed bilingual lessons before publishing.")
        if len(available) <= 8:
            print(f"::warning::{len(available) - 1} unused lessons remain after today's selection")
        entry = {"topic": available[0], "delivery": {lang: {"status": "pending"} for lang in CHANNELS}}
        state["days"][day] = entry
    topic = entry["topic"]  # The first durable reservation freezes both language versions.
    issues = []
    for lang, channel in CHANNELS.items():
        slot = entry["delivery"][lang]
        label = f"{day} {topic['id']} {lang}"
        if slot["status"] in {"sent", "skipped"}:
            print(f"{label} already {slot['status']}")
            continue
        if slot["status"] == "reserved":
            issues.append(f"{label} has an unresolved reservation")
            continue
        if today() != day:
            issues.append(f"{label} expired at midnight")
            break
        text = render(topic, lang)
        slot.update(status="reserved", claim=uuid4().hex)
        journal.save(f"{label} reserved")
        if today() != day:
            slot.update(status="skipped")
            journal.save(f"{label} expired before send")
            issues.append(f"{label} expired at midnight")
            break
        try:
            message_id = send(channel, text)
        except Rejected as error:
            entry["delivery"][lang] = {"status": "pending"}
            journal.save(f"{label} rejected")
            issues.append(f"{label}: {error}")
        except Unconfirmed:
            issues.append(f"{label} unconfirmed; inspect channel and ledger")
        else:
            slot.update(status="sent", message_id=message_id)
            journal.save(f"{label} sent {message_id}")
            print(f"{label} sent {message_id}")
    if issues:
        raise RuntimeError(" | ".join(issues))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", metavar="TOPIC_ID")
    mode.add_argument("--publish", action="store_true")
    parser.add_argument("--state-dir", type=Path)
    args = parser.parse_args()
    topics = load_catalog()
    if not args.publish:
        topic = next((t for t in topics if t["id"] == (args.preview or topics[0]["id"])), None)
        require(topic is not None, "Unknown preview topic")
        for lang, channel in CHANNELS.items():
            print(f"[{channel}]\n{render(topic, lang)}\n")
        return
    require(args.state_dir and os.environ.get("GITHUB_ACTIONS") == "true"
            and os.environ.get("GITHUB_REF") == "refs/heads/main"
            and os.environ.get("GITHUB_EVENT_NAME") in {"schedule", "workflow_dispatch"},
            "Live mode requires the daily workflow on main and a state checkout")
    day = run_day(os.environ["RUN_CREATED_AT"])
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    require(token, "Missing TELEGRAM_BOT_TOKEN")
    journal = GitJournal(args.state_dir)
    publish(topics, journal, day, lambda channel, text: telegram_send(token, channel, text))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, KeyError, TypeError, AttributeError) as exc:
        sys.exit(str(exc))
