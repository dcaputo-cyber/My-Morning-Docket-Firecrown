# Morning Docket — repo setup

A private daily audio briefing for the general counsel of a media company.
Runs on GitHub Pages + GitHub Actions + Microsoft's free edge-tts voices.
Zero ongoing cost; Firecrown's existing Claude Team plan powers the script writing through Cowork.

---

## What's in this repo

```
morning-docket/
├── .github/
│   └── workflows/
│       └── daily-build.yml           # builds MP3 + RSS on every script push
├── generate_episode_audio.py          # edge-tts → MP3
├── build_rss_feed.py                  # regenerates feed/podcast.xml
├── voice_test.py                      # one-off: play a 30s sample of the voice
├── scripts/
│   └── episodes/                      # Cowork pushes daily script .txt files here
│       └── .gitkeep
├── episodes/                          # generated MP3s land here
│   └── .gitkeep
├── feed/                              # generated podcast.xml served by Pages
│   └── .gitkeep
├── write_daily_script.py              # OPTIONAL — only if you later get a
│                                      # personal Anthropic API key
└── REPO_README.md                     # this file
```

---

## One-time setup checklist

### 1. Create the repo (2 min)
Go to github.com → New repository.

- Name: something unguessable, e.g. `morning-docket-a7f3k2`. Even if public, the unguessable URL keeps the feed effectively private.
- Private is fine too — GitHub Pages works from private repos on free accounts as long as you're the owner.
- Initialize empty. No README template needed.

### 2. Drop the files in (3 min)
Extract the contents of this package and push them to the repo's `main` branch:

```bash
cd morning-docket-a7f3k2
unzip /path/to/morning-docket-repo.zip -d .
git add .
git commit -m "Initial Morning Docket setup"
git push
```

### 3. Enable GitHub Pages (1 min)
Settings → Pages.
- Source: "Deploy from a branch"
- Branch: `main`
- Folder: `/ (root)`
- Click Save.

After ~30 seconds, your site is live at `https://<yourusername>.github.io/<repo-name>/`.

### 4. Add one repo secret (1 min)
Settings → Secrets and variables → Actions → New repository secret.

- Name: `PODCAST_BASE_URL`
- Value: `https://<yourusername>.github.io/<repo-name>/episodes`

Example: `https://darren-c.github.io/morning-docket-a7f3k2/episodes`

That's the only secret you need. No API keys.

### 5. (Optional) Adjust the cron schedule for your timezone
Open `.github/workflows/daily-build.yml`.

The current safety-net cron is `"0 9 * * 1-5"` = 09:00 UTC Monday–Friday = **05:00 America/New_York** in DST, **04:00 EST** otherwise.

That's fine for Florida / Eastern time and gives a backstop in case you forget to push a script in the evening. Adjust if you want a different backstop time.

Note: GitHub Actions cron runs in UTC. Use [crontab.guru](https://crontab.guru) to visualize.

### 6. First test push
Add today's script (which is already in your workspace as `episode-2026-04-21-script.txt`) to `scripts/episodes/` and push:

```bash
cp ../episode-2026-04-21-script.txt scripts/episodes/
git add scripts/episodes/
git commit -m "First episode: 2026-04-21"
git push
```

Watch the Actions tab. The workflow will run, build the MP3, regenerate the RSS feed, and push everything back. Expect ~3 minutes end to end.

### 7. Subscribe in Overcast (2 min)
- Install Overcast on your iPhone.
- Tap `+` → "Add URL".
- Paste: `https://<yourusername>.github.io/<repo-name>/feed/podcast.xml`
- On the show's settings page, turn on "Auto-download new episodes".

### 8. CarPlay (1 min)
- iPhone Settings → General → CarPlay → [your car] → Customize.
- Add Overcast to your CarPlay home screen.
- Next time you plug in, Overcast is there.

---

## The daily rhythm

**End of your work day (~5 PM):**

Open Cowork. Say:

> "Build tomorrow's Morning Docket script and push it to my `morning-docket-a7f3k2` repo at `scripts/episodes/episode-YYYY-MM-DD-script.txt`, dated for tomorrow."

Cowork does web research on your topics, writes the script, commits and pushes. Takes about a minute of your time. You can read the script first if you want to redirect any coverage.

**Automatic (within 5 minutes of the push):**

GitHub Actions builds the MP3 using edge-tts, regenerates the RSS feed, commits everything back. Your phone (Overcast) sees the new episode on its next feed check and auto-downloads.

**Next morning:**

Plug into CarPlay. Tap Overcast. Tap the episode. Drive.

---

## Changing the narrator voice

Edit `.github/workflows/daily-build.yml`, line with `--voice`. Replace the voice ID. Options:

- `en-US-AndrewMultilingualNeural` (default, measured)
- `en-US-BrianMultilingualNeural`
- `en-US-GuyNeural`
- `en-US-DavisNeural`
- `en-US-TonyNeural`
- `en-US-EmmaMultilingualNeural`

Commit and push. The next build uses the new voice.

---

## Troubleshooting

**The Action ran but no MP3 was produced.** Check that the script file is in `scripts/episodes/` with a filename like `episode-YYYY-MM-DD-script.txt`. The workflow looks for that naming pattern.

**Overcast doesn't see the new episode.** Pull-to-refresh on Overcast. If it's still missing, open the feed URL in a browser and confirm the `<item>` block for today exists.

**GitHub Pages isn't serving files.** Wait 60 seconds after the commit. First-time Pages deployment can take up to 10 minutes. Settings → Pages shows the current deploy status.

**CarPlay shows the episode but won't play.** Check Overcast's Downloads section on the phone — if the file is still "queued," it hasn't finished downloading. Turn on auto-download in Overcast settings.

---

## Optional upgrades, later

- **Cover art.** Drop a 1400x1400 PNG in `feed/cover.png`, add `--image-url` to the RSS step in the workflow. Shows up in Overcast.
- **Personal Anthropic API key.** If you want the whole pipeline to run in GitHub's cloud (no Cowork push needed), uncomment the script-writing step in the workflow and add `ANTHROPIC_API_KEY` as a secret. ~$5-10/mo.
- **Evening companion episode.** Once the morning show is tuned, add an evening wrap — same pipeline, different script prompt, different filename suffix.
- **Voice cloning.** ElevenLabs can clone your voice from a clean ~3 minute recording. If you ever want the show narrated in your own voice, that's a straightforward swap.
