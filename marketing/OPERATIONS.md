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

Active cadence: **one original clip per day, intended for both YouTube and TikTok**, subject to successful upload, platform review, and required confirmations. Alternate German and English between daily clips. This means one creative adapted to two destinations, not two different clips per platform per day.

The first German clip is **“Drei Fragen, bevor du dem Hype glaubst”**. Continue the educational sequence in the existing [14-day launch calendar](LAUNCH_CALENDAR.md). Clips should be vertical, 20–45 seconds, clearly captioned, and lead to the appropriate free Telegram channel.

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

## Active social automation

- Title: **MarketPulse Elite Shorts**
- Task ID: **6aeb7f0e1bc8819199e82303283545a5**
- State: **activated**.
- Starts: **5 November 2026**, daily at approximately **19:00 Europe/Brussels**, with a flexible scheduling window of **±1 hour**.
- Scope: one original clip per day for the confirmed YouTube and TikTok project accounts, alternating DE/EN. No Instagram.
- The launch clip is now publicly published on both YouTube (**N_Tz7w_25jY**) and TikTok (**7704390833612557591**). Do not upload or publish either again. Continue with the next original clip and the alternating DE/EN sequence.
- Reuse this task; do not create a duplicate social task or a second Telegram schedule.

## Launch log

Status recorded on 4 November 2026 from the production and platform checks. An upload submission is not a confirmed public publication.

| Item | Status | ID / verified location |
| --- | --- | --- |
| First German clip — “Drei Fragen, bevor du dem Hype glaubst” | Production complete; file ready | Asset details below |
| First YouTube Short | **Publicly published and verified on 4 November 2026.** YouTube confirms “Video ist veröffentlicht” and “Am 04.11.2026 veröffentlicht”. The public Shorts page shows the correct title, @marketpulseelite, and AI label. | Video ID **N_Tz7w_25jY**; https://www.youtube.com/shorts/N_Tz7w_25jY |
| First TikTok post | **Publicly published and verified.** Studio shows 4 November 2026, 19:51, visibility **“Alle”**, and no review notice. The actual public post was opened and its 34-second playback, caption, and handle confirmed. | Video ID **7704390833612557591**; https://www.tiktok.com/@marketpulseelite_de/video/7704390833612557591 |
| TikTok cover and disclosures | Cover saved. Public post labels **“Werbeinhalt”** and **“Von Creator*in als KI-generiert gekennzeichnet”** verified. | Same TikTok video ID |
| Daily YouTube/TikTok task | Activated; first scheduled run from 5 November 2026 | **6aeb7f0e1bc8819199e82303283545a5** |
| TikTok display-name change | Blocked by platform date shown as 11 November 2026 | Recheck before change |
| First scheduled Telegram daily run | Awaiting first recorded execution | Pending run URL |

Both launch publications are complete and publicly verified; do not duplicate either post.

### YouTube publication — confirmed

- Existing video ID: **N_Tz7w_25jY**.
- Public URL: https://www.youtube.com/shorts/N_Tz7w_25jY
- Status: **published on 4 November 2026**. The completion dialog explicitly reported “Video ist veröffentlicht” and “Am 04.11.2026 veröffentlicht”.
- Saved title: **“3 Fragen, bevor du dem Börsen-Hype glaubst | MarketPulse Elite”**.
- The opened public Shorts page confirms the title, **@marketpulseelite**, and the AI label. Video playback was still loading at that check; **a completed playback test is not claimed**.
- Description with both German and Global Telegram links saved.
- Audience: not made for children.
- AI-generated-content disclosure enabled; no paid partnership.
- Language: German; category: Education.
- Automatic location information disabled.
- Preliminary checks: no problems reported.
- German SRT uploaded and saved; the interface showed **“Deutsch von dir”**.
- The automatic video-frame thumbnail **(1)** was selected and saved.
- The owner explicitly approved the upload terms with “ja darfst du”; do not ask for the same upload-terms confirmation again.

### Phone verification and custom cover — deferred

- A custom cover remains unavailable because YouTube reports that the phone number is already associated with too many verified accounts: a maximum of two accounts per phone number per year.
- The owner says the number cannot be used again until next year and wants to continue **without another phone-verification attempt**. Do not request or retry phone verification or create a new account for this purpose.
- No phone number is visible or recorded in this operating record.
- The generated custom cover is retained as an asset. The first publication proceeded successfully using the saved automatic video-frame thumbnail.
- **Ongoing operating rule, until further notice:** continue publishing Shorts on the existing project accounts. Use YouTube automatic/video-frame thumbnails; a custom cover is not required. Missing phone verification must not hold up uploads. Do not prompt the owner for this verification again unless the owner changes this instruction.

## First clip assets

- Title: **Drei Fragen, bevor du dem Hype glaubst**
- Language: German.
- Duration: **34.0 seconds**.
- Video: **1080 × 1920**, **30 fps**, **H.264**.
- Audio: **AAC**.
- File size: **2,410,262 bytes**.
- SHA-256: `904b4515e3e4bc4d33871212b673bcdcfc90d3ef504ff8f4cf7465f0a4485323`.
- Library film ID: **libfile_ab3a075b56008191823fe1e7a41df7cf**.
- Library cover ID: **libfile_3967f17639c08191bfc5e90a043e133e**.
- Library production kit ID: **libfile_dbc2132781b48191af0fcadee67e8ab9**.
- InVideo project: https://invideo.io/@niels-69065/marketpulse-elite-drei-fragen-vor-dem-hype-de-start-short
- Confirmed InVideo credit balance: **589.8 → 588.2**, a decrease of **1.6 existing credits**. No purchases.

## Routine checks

- Before posting: confirm project identity, language, rights to media/music, sources, captions, and the intended Telegram destination.
- After posting: inspect the actual published result; record its URL/ID and any moderation or processing status. An attempted upload is not a confirmed publication.
- Weekly: review qualified views, profile clicks, Telegram joins, retention, saves, and corrections. Never substitute invented figures for unavailable metrics.
