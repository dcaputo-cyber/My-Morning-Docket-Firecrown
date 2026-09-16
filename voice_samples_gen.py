"""
Temporary voice sample generator for Morning Docket.

Generates a short (~30 second) narration clip in several candidate
edge-tts voices so a human can compare them by ear. Not part of the
production pipeline -- safe to delete after use.
"""
import asyncio
import edge_tts

SAMPLE_TEXT = """
A publisher in California pays one and a half million dollars for a bad
cookie banner. The FTC sues the world's three largest ad agencies over what
it calls collusion on brand safety. And somewhere in Washington, two
commercial pilots get caught meowing at each other over air traffic control.
It has been, by any reasonable measure, an interesting ten days to practice
law at a media company. Good morning. This is Morning Docket, your daily
commute briefing on the law shaping the ground under a modern media company.
""".strip()

VOICES = {
    "andrew": "en-US-AndrewMultilingualNeural",
    "brian": "en-US-BrianMultilingualNeural",
    "guy": "en-US-GuyNeural",
    "davis": "en-US-DavisNeural",
    "tony": "en-US-TonyNeural",
    "emma": "en-US-EmmaMultilingualNeural",
    "aria_current": "en-US-AriaNeural",
}


async def main() -> None:
    for label, voice in VOICES.items():
        out = f"voice-samples/{label}.mp3"
        print(f"Generating {label} ({voice}) -> {out}", flush=True)
        communicate = edge_tts.Communicate(SAMPLE_TEXT, voice, rate="-5%")
        await communicate.save(out)
        print("  done", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
