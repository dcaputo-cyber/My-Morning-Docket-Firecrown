# Script structure + voice guidelines

## Word count target
- **3,500–4,200 words** (~23–28 min at 150 wpm)
- If the draft comes in short, the deep dive needs more substance — do NOT pad with restatement
- If it comes in long, compress the headline roundup (not the deep dive)

## Sections (in order)

### 1. SHOW OPEN (~30–50 words)
```
MORNING DOCKET — <Day>, <Month> <Day>, YYYY
A daily brief for the general counsel of a media company.
Produced by Darren Caputo.

---
```

### 2. COLD OPEN (~100–150 words)
- Lead with the single most interesting item of the day
- One arresting sentence or vignette — do NOT summarize, tease
- Make the listener curious enough to stay for the headline roundup

### 3. INTRO (~100–150 words)
- "Good morning. It's <day>, <date>. Welcome to Morning Docket."
- One orienting paragraph about what's on today's docket — frame it in terms of the top profile theme if it matches, otherwise in terms of the biggest news story
- If the previous business day's episode was missed or unusual, briefly acknowledge

### 4. HEADLINE ROUNDUP (~600–900 words, 4–6 items)
- Each item: ~100–150 words
- Opening line: 1-sentence frame of the news
- Followed by: 2–3 sentences of what happened, why it matters, and the GC-relevant implication
- Order by importance, weighted: news-significance + profile-match
- Items boosted by profile match should get EQUAL word count, not more — no favoritism, just ordering

### 5. DEEP DIVE (~1,400–1,800 words)
- Pick ONE theme. Title it descriptively (e.g., "Children's Privacy's New Floor and the Federal Preemption Gambit")
- Structure inside the deep dive:
  - Background / context (~300–400 words)
  - What happened today / this week (~400–500 words)
  - Doctrinal or procedural analysis (~400–500 words)
  - Practical implications for a GC at a media company (~300–400 words)
- If two related major stories both deserve the slot, BRAID them (explicit call-out in the transition)
- Cite cases, rules, statute sections precisely — but say them as a human would speak

### 6. GC BENCH (~300–450 words)
- Section header: "GC bench — what I'd do this week"
- 3–5 action items, numbered
- Each item: 60–90 words
- Format: "*<Action verb imperative>.* <What it means tactically.> <Why it matters now.>"
- Concrete and operational — "audit your analytics SDKs for COPPA compliance" not "think about privacy"

### 7. INDUSTRY ANGLE (~300–450 words)
- The "zoom out" — what does all this mean for media specifically, or advertisers, or Firecrown's verticals
- Predictive: "here's what I'd watch for in the next 60 days"
- Can touch lightly on freight (bucket 5) if there's a tie-in to the day's main threads

### 8. CLOSING BRIEF / WATCH LIST (~150–250 words)
- Section header: "Watch list — what's coming up"
- 5–8 dated items in chronological order
- Format: "<Month> <Day> — <Event/deadline>"
- Court hearings, rule effective dates, comment deadlines, congressional markups

### 9. SIGNOFF (~50–80 words)
- "That's Morning Docket for <spoken day>, <spoken date>."
- One forward-looking line ("We'll be back <next listen day> with <preview>...")
- A drive-safely or similar signoff
- Final line: `END OF EPISODE.`

## Voice

- First-person, conversational, authoritative — Darren is an in-house GC reading you in on the morning, not a news anchor and not a professor
- Plain English, but precise. No filler legalese ("aforementioned", "pursuant to") — but correct terms of art ("motion to dismiss", "summary judgment", "preempted")
- Cite cases in italics: `*Bartz v. Anthropic*` (asterisks survive TTS as emphasis)
- Cite statute sections as spoken: "Section one oh two" not "§ 102"

## TTS-readability rules

The script is read by edge-tts. Format things so they speak correctly:

- **Numbers**: spell out when spoken. "one point five billion dollars" not "$1.5B". "twenty-nine million jobs" not "29M jobs".
- **Dates**: write out. "April twenty-second" not "4/22" or "Apr 22".
- **Time**: "nine a.m. Eastern" not "9:00 AM ET".
- **URLs**: never in script. URLs go in the Slack shownotes only.
- **Acronyms**: first use, spell it out. After that, use the acronym if it's commonly spoken as an acronym ("FTC" yes, "EDPB" no — that second one should be "the European Data Protection Board" each time because a TTS engine stumbles on letter-strings).
- **Case names**: italicized with asterisks — `*Bartz v. Anthropic*`. TTS reads these fine, and it cues the emphasis.
- **Footnotes / parentheticals**: avoid — or turn them into a dependent clause

## No-repeat enforcement (before save)

Check the last 3 episode scripts against the current draft:

- Deep-dive topic must not match any of the last 3 deep dives (unless new major development)
- First headline must not match the last episode's first headline (unless same story with new development)
- If you find a conflict, re-rank and re-draft the affected section

## File save

Path: `scripts/episodes/episode-<target-date>-script.txt`

Do not commit. Darren pushes manually so he can review the script and the profile snapshot together before they go to main.
