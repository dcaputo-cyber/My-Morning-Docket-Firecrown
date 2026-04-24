# Slack DM shownotes format

## Destination

- Channel: Darren's DM
- User ID: `U06GQJUL7FE`
- Tool: `slack_send_message` (NOT `slack_send_message_draft` — this is an automated run, send directly)

## Hard limits

- **5,000 characters maximum** in a single message (Slack's per-text-element cap)
- Send as ONE message, not multiple
- Do not thread — this is a DM, stay in the top-level channel

## Format

```
*Morning Docket — <Day>, <Month> <Day>, YYYY*
Shownotes + sources. ~<NN> min @ 150 wpm.

*Deep dive: <Title>*
<2–4 sentence punchy summary. What was the argument, why does it matter.>

*Headline roundup*
• *<Item 1 headline.>* <One-line frame.> <URL|Source>
• *<Item 2 headline.>* <One-line frame.> <URL|Source>
(4–6 bullets)

*GC bench — what I'd actually do this week*
1. *<Action verb imperative.>* <1–2 sentence why + tactical how.>
2. *<Action.>* <...>
(3–5 items)

*Watch list / calendar*
• <Month> <Day> — <event/deadline>
(5–8 items, chronological)

*Industry angle — media/adtech*
<2–4 sentences. The zoom-out.>

*Script*
`scripts/episodes/episode-<target-date>-script.txt` — <N> words, ~<NN> min.

<Optional: one flag/note/bug to surface to Darren — max 2 sentences.>
```

## Slack markdown

- `*bold*` — single asterisks, not double (this is Slack, not standard markdown)
- `_italic_` — single underscores
- `<URL|display text>` — links; the display text shows, the URL doesn't
- Backticks for `code/filepaths`
- No headers (`#`, `##`) — Slack doesn't render them, uses the asterisks as visual structure instead

## Character budgeting

Rough allocation when you're aiming at ~4,600 chars (leaving 400-char buffer):
- Header + deep dive summary: ~500 chars
- Headline roundup (5 items × ~280 chars): ~1,400 chars
- GC bench (4 items × ~300 chars): ~1,200 chars
- Watch list: ~400 chars
- Industry angle: ~500 chars
- Script + flags: ~400 chars

## If over 5,000 chars — trim in this order

1. Drop the industry angle down to 2 sentences
2. Drop any URL that appears twice (e.g., if both bullet and deep-dive link to same FTC page, keep one)
3. Drop the second source URL from any item that has two
4. Drop the 5th/6th bullet if roundup has 6
5. Compress watch list to top 4 items
6. Drop the optional flag line at the bottom
7. Drop URLs entirely (last resort — script itself still has the info)

## Link handling

- Every headline bullet should have ONE link (if a source is citeable). Max one.
- Link the most authoritative source: primary gov source (FTC/SEC/DOJ/EC page) > trade press > general press
- Shorten display text: `<https://www.ftc.gov/...|FTC release>` not `<https://www.ftc.gov/...|https://www.ftc.gov/legal-library/...>`

## After sending

Capture the returned `message_link` in the final report-back so Darren can open the DM directly from the run summary.

## Privacy reminder

Shownotes are sent over Slack — they go through Firecrown's Slack workspace. Do NOT include:
- Specific matter details that were in the profile snapshot and aren't in the public script
- Attorney-client privileged context
- Any direct email/message quotes from Darren's correspondents

The DM should summarize the public episode + sources only. The profile snapshot stays in the repo, not in the DM.
