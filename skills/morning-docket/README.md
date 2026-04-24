# morning-docket skill

The single source of truth for how Morning Docket episodes get made.

## What's in here

| File | Purpose |
|---|---|
| `SKILL.md` | The skill entry point. Orchestrates the six-stage pipeline. Start here. |
| `profile-refresh.md` | Stage 2 — how to sample Gmail, Slack, and Drive and build the weekly topic vector. |
| `research-sources.md` | Stage 3 — what to search for in the news and how the no-repeat rule works. |
| `script-structure.md` | Stage 4 — section-by-section structure, word counts, and TTS-readability voice rules. |
| `slack-shownotes.md` | Stage 5 — the Slack DM format, character budget, and trim-down order. |

## How the scheduled task uses this

The scheduled task brief should simply say:

> Run the `morning-docket` skill. Read `skills/morning-docket/SKILL.md` in this repo and execute the pipeline end-to-end. No additional instructions — the skill owns the whole flow.

Everything else — recipient user_id, word count targets, section structure, 5,000-char Slack cap — lives in the skill files and gets read at run time. Iterating on the process means editing files here and committing, not updating the scheduled task.

## Output paths

- Episode script: `scripts/episodes/episode-YYYY-MM-DD-script.txt`
- Profile snapshot: `scripts/profile-snapshots/YYYY-MM-DD.md`

Both are written locally. Darren pushes manually (review-before-push).

## Build pipeline (downstream)

When Darren pushes a script, `.github/workflows/daily-build.yml` generates the MP3 with edge-tts and updates `feed/podcast.xml`. The workflow uses `git diff HEAD^ HEAD` to pick exactly the script that was just pushed.

## Iterating on this skill

If you want to change how episodes get made:
1. Edit the relevant file(s) here
2. Commit — the next scheduled run picks up the change automatically
3. No need to update the scheduled task brief

If you want to add a new stage, add a new reference file here and add a corresponding stage to `SKILL.md`.
