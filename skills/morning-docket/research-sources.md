# Research sources + no-repeat rule

## Priority topic buckets

The Morning Docket is a brief for a GC at a media company. Prioritize items in this order:

### 1. Privacy / data protection
- US state privacy law patchwork (IAPP tracker, state AG enforcement actions)
- COPPA, CCPA/CPRA, VCDPA, CTDPA, UCPA, and newer state equivalents
- FTC enforcement actions — especially on dark patterns, kids' privacy, data brokers
- EU: GDPR enforcement actions, DSA / DMA enforcement waves, European Board for Digital Services
- UK: ICO actions, DUAA

### 2. Adtech / consumer marketing
- FTC click-to-cancel / ARL / state subscription laws (California, NY, NYC municipal)
- Cookie / consent litigation (wiretap theories, session replay)
- FTC endorsement guides, sponsored content, creator disclosures
- State AG attention on subscription practices

### 3. AI / IP
- Copyright litigation (Bartz v. Anthropic, NYT v. OpenAI, class actions)
- Training data disclosure (EU AI Act Art. 53, California SB 942/SB 1047)
- US Copyright Office guidance on AI outputs
- Fair use jurisprudence applied to training

### 4. Media-specific regulatory
- Section 230 case law
- SEC disclosure: Reg S-K amendments, cyber-incident 4-day rule, cybersecurity governance
- SEC 10b5-1, insider trading actions
- Shield laws, journalist protections, reporter's privilege cases

### 5. Freight / logistics (secondary thread — Firecrown operates freight brands)
- SONAR / FreightWaves rate snapshots (NTI, intermodal, dry van)
- FMCSA rulemakings, broker transparency, HOS updates
- Congressional activity on freight (SHIP Act, trucking bills)

## Research cadence

For each episode:

1. Pull last 7–10 days of news across buckets 1–4 (bucket 5 is a 1–2 headline sidecar)
2. Check against the 3 most recent episode scripts for the no-repeat rule
3. For EVERY fact going in the script, verify with a web search — dates, holdings, names, dollar figures, jurisdiction
4. If a source paywall blocks verification, either (a) find a free source with the same fact, or (b) don't include the claim

## Primary sources (always check these first)

- FTC press releases: https://www.ftc.gov/news-events/news/press-releases
- SEC press releases: https://www.sec.gov/news/pressreleases
- DOJ press releases: https://www.justice.gov/news
- IAPP daily dashboard: https://iapp.org/news/
- European Commission press corner: https://ec.europa.eu/commission/presscorner
- Law360 (paywall; headlines only for navigation)
- Bloomberg Law (paywall; headlines only)
- Reuters Legal: https://www.reuters.com/legal/
- Ars Technica policy section: https://arstechnica.com/tech-policy/
- FreightWaves / SONAR: https://www.freightwaves.com/

## No-repeat rule

Before finalizing headlines and deep dive:

1. Read the 3 most recent episode scripts in `scripts/episodes/`
2. Extract the HEADLINES and DEEP DIVE TITLE from each
3. For the current episode:
   - If a topic was the deep dive in any of the last 3 episodes, do NOT repeat it as deep dive unless there's a meaningful new development
   - If a topic was a headline in the last episode, demote it (can appear as a one-line update but shouldn't be #1)
   - If the SAME story has moved (e.g., hearing happened, ruling came down), it can be covered — but lead with the new development, not a re-frame of the old facts

## Profile-vector weighting

After research is complete, before drafting:

1. Read the profile snapshot for this episode (`scripts/profile-snapshots/<target-date>.md`)
2. Score each candidate headline/deep-dive topic against the top 3 profile themes
3. Boost topics that hit a profile theme (raise them 1–2 spots in the running order)
4. The deep dive should ideally hit at least 1 profile theme — if the day's biggest news story doesn't match any profile theme, either (a) braid it with a profile theme if they're related, or (b) keep the news story as deep dive and use the GC bench section to hit profile themes

This is weighting, not filtering. If the day has huge news that doesn't match the profile, we still cover it — we just don't over-index on profile matches at the expense of news judgment.
