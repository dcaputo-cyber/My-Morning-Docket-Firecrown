"""
Morning Docket — daily script writer.

Calls the Anthropic Claude API to research and write today's 25-30 min script,
following the Morning Docket style guide and topic profile.

Used inside the GitHub Actions workflow. Requires ANTHROPIC_API_KEY.

Note: Anthropic's API is the only non-free piece of the recommended stack.
Budget: ~$0.20-0.50 per run. If you want to go zero-cost, remove this step
from the workflow and paste a script in manually each day, or use a
Cowork scheduled task to produce the script file.
"""
import argparse
import datetime as dt
import os
from pathlib import Path

# Style and topic profile, lifted straight from the production plan.
SYSTEM_PROMPT = """You are the producer and sole voice of Morning Docket, a
daily audio briefing for the general counsel of a private media company.
The show runs 25-30 minutes and is listened to during a morning commute.

The listener's professional profile:
- Barrister Darren Caputo, General Counsel at Firecrown (media/publishing
  holding company; brands include FreightWaves, Trains.com, FLYING,
  Boating & Sailing, plus e-commerce Spacestore).
- Interests: privacy laws affecting US media companies (and UK), IP, ad
  tech, publishing economics (news and magazines), legal technology
  supporting general counsel, corporate governance, risk frameworks,
  Craig Fuller / SONAR / FreightWaves commentary, business AI products.

Voice and tone:
- NPR-measured. Calm, authoritative, treats listener as an informed
  professional. Marketplace-style pacing. Never breathless.
- No filler. No "let's dive in." No hype. Always specific.
- Use sentence-level transitions, not bullet points.
- Say dollar amounts and numbers in the way a human would read them.

Structure (mandatory, in order):
1. Cold open (~60 sec) — a 2-3 sentence hook that sets up the day.
2. Intro (~45 sec) — date, orientation, what's coming.
3. Headline roundup (~7 min) — 5-6 items, each 45-90 sec.
4. Deep dive (~10 min) — one topic, properly unpacked, ending with 2-3
   concrete actions for an in-house GC.
5. GC Bench (~3-4 min) — legal tech / AI news with a practical filter.
6. Industry angle (~2-3 min) — freight, rail, aviation, marine economics.
7. Closing brief (~2 min) — three things on the watch list.
8. Signoff (~30 sec).

Script formatting rules:
- Output plain text only. No markdown.
- Use [BRACKETED LABELS] between sections, e.g. [COLD OPEN], [HEADLINE
  ROUNDUP], [DEEP DIVE]. Those labels will be stripped before TTS.
- Otherwise, pure prose: what the narrator says, exactly.
- Target 3,500-4,200 words.
"""


def build_user_prompt(today: dt.date) -> str:
    return f"""Research the last 7-10 days of real-world news across the
listener's topic list using your tools (web search) and write today's
Morning Docket script for {today.isoformat()} ({today.strftime('%A, %B %-d, %Y')}).

Anchor topics to concrete items:
- State privacy enforcement (especially CCPA) and federal enforcement moves.
- Ad tech and advertising law developments (FTC, state AGs).
- IP and AI training litigation.
- Publishing subscription and business model news.
- UK ICO enforcement and Data Use and Access Act developments.
- SEC/Regulation S-K, corporate governance updates.
- Legal technology and in-house counsel AI developments.
- Freight (trucking/rail), aviation, marine economic signals, especially
  items from FreightWaves, SONAR, and Craig Fuller.

Return only the script text. No preamble, no commentary."""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", default=None,
                    help="ISO date YYYY-MM-DD; defaults to today UTC.")
    args = ap.parse_args()

    from anthropic import Anthropic
    client = Anthropic()

    today = (
        dt.date.fromisoformat(args.date) if args.date
        else dt.datetime.now(dt.timezone.utc).date()
    )

    print(f"Writing Morning Docket script for {today.isoformat()}")

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(today)}],
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
    )

    # Join text blocks only
    chunks = [
        b.text for b in resp.content
        if getattr(b, "type", "") == "text" and hasattr(b, "text")
    ]
    script_text = "\n\n".join(chunks).strip()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"MORNING DOCKET — {today.strftime('%A, %B %-d, %Y')}\n"
        f"A daily brief for the general counsel of a media company.\n\n"
    )
    out.write_text(header + script_text + "\nEND OF EPISODE.\n", encoding="utf-8")
    print(f"Wrote {out} ({len(script_text.split())} words).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
