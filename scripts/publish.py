import os, pathlib, urllib.parse, urllib.request, json

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise SystemExit("Missing TELEGRAM_BOT_TOKEN secret")
for channel, filename in [("@MarketPulseEliteDE", "posts/de.txt"), ("@MarketPulseEliteGlobal", "posts/en.txt")]:
    message = pathlib.Path(filename).read_text(encoding="utf-8").strip()
    if not message or len(message) > 4096:
        raise SystemExit("Post empty or too long: " + filename)
    data = urllib.parse.urlencode({"chat_id": channel, "text": message}).encode()
    req = urllib.request.Request("https://api.telegram.org/bot" + TOKEN + "/sendMessage", data=data)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.load(response)
    except Exception as exc:
        raise SystemExit("Failed to post to " + channel + ": " + type(exc).__name__) from exc
    if not result.get("ok"):
        raise SystemExit("Telegram rejected post to " + channel)
    print("Published to " + channel)
