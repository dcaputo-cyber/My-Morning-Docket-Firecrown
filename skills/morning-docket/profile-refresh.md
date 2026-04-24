# Profile refresh — what to pull and how to weight it

Goal: build a short "what is Darren actually working on this week" topic vector that the script can be weighted against. Save output to `scripts/profile-snapshots/<target-date>.md`.

## Scope
- Window: last 7 days before today
- Recency weight: items from today/yesterday count 2.0x; sliding down to 1.0x at 7 days ago
- Ignore: newsletters, marketing, vendor cold outreach, spam, out-of-office replies, automated system notifications

## Step 1 — Gmail

Use the Gmail MCP tools (`search_threads`, `get_thread`).

Priority searches:
- `from:me newer_than:7d` — what Darren has been writing/deciding
- `to:dcaputo@firecrown.com is:important newer_than:7d` — inbound items flagged important
- `is:starred newer_than:7d` — explicitly flagged by Darren
- `in:inbox -category:promotions -category:social -category:updates newer_than:7d` — general inbox minus noise

Exclusions (drop these before analysis):
- Labels: `CATEGORY_PROMOTIONS`, `CATEGORY_SOCIAL`
- Sender domain patterns suggesting newsletters: substack.com, beehiiv.com, mailchimp-hosted lists, *.marketo.com
- Subject patterns: "unsubscribe", "newsletter", "digest"

For each surviving thread, capture:
- Subject
- Counterparty (or counterpart company)
- 1–2 sentence summary of what's being negotiated/decided
- Apply recency weight based on latest message in thread

## Step 2 — Slack

Use `slack_read_user_profile` to confirm Darren's user_id (`U06GQJUL7FE`) before searches.

Priority pulls:
- Messages Darren posted in the last 7 days (`slack_search_public_and_private` with `from:@darren`)
- Active DMs in the last 7 days — read recent messages in each
- Top 3–5 channels he's most active in — skim last 7 days

Capture:
- Recurring company / person names (people he's messaging often this week)
- Topics that appear in 3+ messages
- Any explicit deadlines/dates mentioned

Do NOT read messages Darren did not write unless they're direct replies to his messages (context). Respect his privacy on broader channel chatter.

## Step 3 — Google Drive

Use the Drive MCP tools (`list_recent_files`, `get_file_metadata`, `read_file_content`).

Priority pulls:
- 15 most recently modified files Darren owns
- 10 most recently modified files Darren has edited (not owned) in the last 14 days
- Skip: templates, old exports, files untouched for 14+ days

For each: title + first 100–200 chars of content (enough to infer topic).

## Step 4 — Synthesize

Build a weighted topic vector:

1. Cluster mentions into 5–8 themes. Examples:
   - "Privacy/COPPA compliance"
   - "Vendor MSA negotiations"
   - "Ad Orbit integration"
   - "Freight rate contracts"
   - "Employment matters"
2. For each theme:
   - Sum recency-weighted counts across Gmail + Slack + Drive
   - Flag cross-surface themes (appearing in 2+ of email/slack/drive) — these are HIGHEST signal
3. Identify the top 3 themes by weight for this week

## Step 5 — Save snapshot

Write to `scripts/profile-snapshots/<target-date>.md` in this format:

```markdown
# Profile snapshot — <target-date>
Generated for Morning Docket episode of <target-date>.
Window: last 7 days.

## Top themes (weighted)
1. **<Theme>** — weight X.X — sources: email (N), slack (N), drive (N) — cross-surface: yes/no
2. **<Theme>** — weight X.X — ...
3. ...

## Active matters
- [Brief bullets, max 8]

## Recurring names / entities
- [List — people, companies, counterparties appearing 3+ times]

## Signal to script weighting
<1–3 sentences: what should the episode lean on this week? If profile themes match well with the day's news, note that. If they diverge, note that too and decide whether to weight toward profile or toward news for this episode.>

## Sources sampled
- Gmail: <N threads>
- Slack: <N messages, <N channels/DMs>
- Drive: <N files>
```

## Privacy note

The profile snapshot gets committed to the repo along with the episode script. Do NOT include:
- Verbatim quotes from emails/Slack/documents
- Attorney-client privileged specifics (settlement numbers, litigation strategy details)
- Personal health / financial specifics
- Anything that would be awkward in a git history

The snapshot should summarize at the topic level only — "negotiating renewal on a major vendor MSA" is fine; "negotiating the $X renewal with Vendor ABC, counterparty is threatening to escalate" is not.
