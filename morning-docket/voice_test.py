"""
Morning Docket — voice test.

Generates ~30 seconds of narration using Microsoft's free edge-tts neural
voices, so you can hear the narrator quality before committing to the
full pipeline setup.

USAGE
-----
    pip install edge-tts
    python voice_test.py

That's it. No ffmpeg needed for this test. Produces:
    voice_test.mp3   (Andrew Multilingual Neural — the default)

To hear a different voice, edit the VOICE constant below. Candidates:
    en-US-AndrewMultilingualNeural      (default, warm NPR-ish)
    en-US-BrianMultilingualNeural       (slightly younger)
    en-US-GuyNeural                     (classic news anchor)
    en-US-DavisNeural                   (polished, confident)
    en-US-TonyNeural                    (deeper, documentary feel)
    en-US-EmmaMultilingualNeural        (warm female)
"""
import asyncio
import edge_tts

VOICE = "en-US-AndrewMultilingualNeural"

# ~100-120 words = ~30 seconds of narration at measured pace.
SAMPLE_TEXT = """
A publisher in California pays one and a half million dollars for a bad
cookie banner. The FTC sues the world's three largest ad agencies over what
it calls collusion on brand safety. Anthropic writes a one point five billion
dollar check to book publishers. And somewhere in Washington, two commercial
pilots get caught meowing at each other over air traffic control. It has
been, by any reasonable measure, an interesting ten days to practice law at
a media company. Good morning. This is Morning Docket, your daily commute
briefing on the law, the business, and the regulators shaping the ground
under a modern media company.
""".strip()


async def main() -> None:
    print(f"Voice: {VOICE}")
    print(f"Generating voice_test.mp3 ...")
    communicate = edge_tts.Communicate(SAMPLE_TEXT, VOICE, rate="-5%")
    await communicate.save("voice_test.mp3")
    print("Done. Play voice_test.mp3 to hear the narrator.")


if __name__ == "__main__":
    asyncio.run(main())
