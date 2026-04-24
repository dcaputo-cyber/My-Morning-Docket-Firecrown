---
name: morning-docket
description: Generate Darren Caputo's Morning Docket daily podcast episode — a brief for the general counsel of a media company. Use this skill whenever the scheduled "Morning Docket" task fires, or whenever the user asks to "generate the morning docket", "build the next episode", "run the daily brief", or similar. This skill owns the full pipeline end-to-end: profile refresh (Gmail/Slack/Drive) → news research → script draft → save → Slack DM shownotes → final report-back. Scripts are NOT committed to git automatically — Darren pushes manually so he can review first.
---

# Morning Docket — Full Pipeline

This skill generates the next Morning Docket episode and delivers it end-to-end. It is the single owner of the podcast workflow; the scheduled task should simply invoke this skill with no additional instructions.

## Context constants

- Host: Barrister Darren Caputo, General Counsel, Firecrown Media
- Slack user_id (DM target): `U06GQJUL7FE`
- Email: `dcaputo@firecrown.com`
- Repo root: `C:\Users\dcaputo\Documents\GitHub\My-Morning-Docket-Firecrown`
- Episode script path: `scripts/episodes/episode-YYYY-MM-DD-script.txt`
- Profile snapshot path: `scripts/profile-snapshots/YYYY-MM-DD.md`
- Build workflow: `.github/workflows/daily-build.yml` (generates MP3 + RSS on script push)
- Speaking rate: 150 wpm (for runtime estimates)

## Pipeline — run these stages in order

### Stage 1 — Resolve the target listen date

Use bash `date` to get today's weekday.

- Mon–Thu → target listen date is TOMORROW (next weekday)
- Fri → target listen date is NEXT MONDAY
- Sat/Sun → do not produce an episode; report back "weekend, skipping"

Scripts are generated the afternoon BEFORE the listen date. The build workflow uses `git diff HEAD^ HEAD` to detect the pushed script, so the filename date is the listen date, not today's date.

### Stage 2 — Profile refresh

Read `profile-refresh.md` and execute it fully. Output: `scripts/profile-snapshots/<target-date>.md` with the weighted topic vector.

This stage is NOT optional. Without the profile snapshot, the script is generic. The point of the refresh is to weight the day's brief toward what Darren is actually working on.

### Stage 3 — News research + no-repeat check

Read `research-sources.md` and execute it fully.

- Pull last 7–10 days of news across the priority topic buckets
- Read the last 3 episode scripts (most recent 3 files in `scripts/episodes/`) for the no-repeat rule
- Verify every fact with a web search before including it

### Stage 4 — Draft the script

Read `script-structure.md` for the word count, section-by-section structure, and voice guidelines.

- Target 3,500–4,200 words
- Weight content toward the profile-vector themes (recent-most items ~2x older items in the window)
- Save to `scripts/episodes/episode-<target-date>-script.txt`
- **DO NOT git commit.** Darren pushes manually so he can review first.

### Stage 5 — Slack DM shownotes

Read `slack-shownotes.md` for the DM format.

- Hard cap: 5,000 characters in a single Slack message
- Send to `U06GQJUL7FE` using `slack_send_message` (not draft — this is an automated run)
- If over 5,000 chars, follow the trim-down order in `slack-shownotes.md`

### Stage 6 — Report back

Final response to the user includes:

1. Target date
2. Word count + estimated runtime at 150 wpm
3. Structure variant used (news-heavy, profile-heavy, or braided)
4. Deep-dive one-liner
5. File path
6. Slack delivery confirmation + character count used
7. Top 3 profile-snapshot themes that drove the weighting
8. Git command reminder:

```
git add scripts/episodes/episode-<target-date>-script.txt scripts/profile-snapshots/<target-date>.md
git commit -m "Morning Docket: episode <target-date>"
git push
```

## Failure modes to watch for

- **Slack DM > 5,000 chars**: trim per `slack-shownotes.md`, iterate until under cap
- **Profile refresh returns empty**: don't fake a snapshot — note in the report-back that profile data was unavailable and the episode was news-weighted only
- **Last 3 scripts cover today's best topic**: pick a different deep-dive theme, note the skipped topic in the report-back for future coverage
- **Web research unavailable**: do NOT invent facts or dates. If a key source is unreachable, say so and work with what's verifiable
- **Target date is a federal holiday**: note it and proceed — the listener can always skip an episode
