# MarketPulse Elite — operating record

Updated: 4 November 2026 (Europe/Brussels).

## Active scope

- Project mailbox: marketpulseelite@gmail.com.
- YouTube: **@marketpulseelite**, channel **UCJYUmCEkEBdGWI20ef3Pquw**.
- TikTok: **@marketpulseelite_de**. The current display name is marketpuls; the platform shows 11 November 2026 for the next name change.
- Telegram: https://t.me/MarketPulseEliteDE and https://t.me/MarketPulseEliteGlobal.
- Instagram is excluded at the owner's request.
- Never use the owner's private social accounts. No purchases, paid advertising, paid upgrades, bought followers, mass direct messages, or spam.

## Social publishing rule

Provisional cadence: **one original clip per day, published to both YouTube and TikTok**. Alternate German and English between daily clips. This means one creative adapted to two destinations, not two different clips per platform per day.

Use the existing [14-day launch calendar](LAUNCH_CALENDAR.md): begin with a German project-introduction clip, then continue the educational sequence. Clips should be vertical, 20–45 seconds, clearly captioned, and lead to the appropriate free Telegram channel.

Use dated, verifiable sources for factual market claims. Do not invent performance, prices, testimonials, urgency, or guaranteed returns. Content is general education, not personalized investment advice. Follow the [brand guide](BRAND_GUIDE.md).

Upload directly to the confirmed project channels. Before every publication, verify the active destination against the exact handle and YouTube channel ID above.

**Metricool restriction:** brand **7708724** is connected to the separate Oddly Orbit YouTube channel (**UCE3mCsG1KvTrmcBswFanCIg**). It is not a MarketPulse destination. Do not publish MarketPulse content through it, reconnect it, or replace any existing connection.

## Existing Telegram automation — do not duplicate

- Workflow: [.github/workflows/daily.yml](../.github/workflows/daily.yml).
- Schedule: **07:13 UTC daily**; **08:13 in Brussels during winter, 09:13 during summer**.
- Script: [scripts/daily.py](../scripts/daily.py).
- Behavior: selects one of **seven static educational topics** by the Brussels calendar date and sends its German and English versions to the respective Telegram channels.
- This is not live market research, current news analysis, or a continuously researched watchlist.
- Do not add another Telegram daily schedule or trigger an extra run merely to start social publishing.
- There is no persistent sent-post deduplication in this script; an additional run can repeat a day's post.

The daily workflow was added on 4 November 2026 at 11:12 UTC, after that day's scheduled time. At the audit, no daily run had yet been recorded; the first expected scheduled run is 5 November 2026 at 08:13 Brussels time. A successful manual welcome-post run is confirmed:
https://github.com/icedevil88/marketpulse-elite/actions/runs/41819083943

The separate [.github/workflows/publish.yml](../.github/workflows/publish.yml) is manual only and sends [posts/de.txt](../posts/de.txt) and [posts/en.txt](../posts/en.txt). These still contain the welcome posts; do not rerun them unintentionally.

## Launch log

Treat this table as a record of evidence, not a declaration that an upload or automation already exists. Replace pending entries only after receiving and verifying the corresponding result.

| Item | Status | ID / verified URL |
| --- | --- | --- |
| First German introduction clip | In production | Pending |
| First YouTube Short | Not yet recorded here | Pending |
| First TikTok post | Not yet recorded here | Pending |
| Daily YouTube/TikTok task | Not yet recorded here | Pending automation ID |
| TikTok display-name change | Blocked by platform date shown as 11 November 2026 | Recheck before change |
| First scheduled Telegram daily run | Awaiting first recorded execution | Pending run URL |

## Routine checks

- Before posting: confirm project identity, language, rights to media/music, sources, captions, and the intended Telegram destination.
- After posting: inspect the actual published result; record its URL/ID and any moderation or processing status. An attempted upload is not a confirmed publication.
- Weekly: review qualified views, profile clicks, Telegram joins, retention, saves, and corrections. Never substitute invented figures for unavailable metrics.
