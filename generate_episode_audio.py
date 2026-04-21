"""
Morning Docket — local audio generator.

Converts a text script (with [BRACKETED] stage directions and `---` separators
automatically stripped) into a single MP3.

Default provider is Microsoft edge-tts: free, high-quality neural voice,
no API key required. OpenAI and ElevenLabs are available as optional
paid providers.

USAGE
-----
1) Install deps in a venv:
       python3 -m venv .venv && source .venv/bin/activate
       pip install edge-tts pydub
       # Also install ffmpeg on your system:
       #   macOS:   brew install ffmpeg
       #   Ubuntu:  sudo apt-get install ffmpeg
       #   Windows: choco install ffmpeg

2) Run with the free default (edge-tts, no key required):
       python generate_episode_audio.py \
           --script episode-2026-04-21-script.txt \
           --out   morning-docket-2026-04-21.mp3

   Or specify a voice:
       python generate_episode_audio.py ... --voice en-US-AndrewMultilingualNeural

PROVIDERS
---------
edge-tts   (default, FREE)  — Microsoft neural voices via Edge's TTS endpoint.
openai     (paid)           — tts-1-hd, ~$0.03/1k chars (~$0.57 per episode).
elevenlabs (paid)           — eleven_multilingual_v2, ~$0.18/1k chars.

VOICE RECOMMENDATIONS
---------------------
edge-tts (NPR-ish, measured):
    en-US-AndrewMultilingualNeural   (default — broadcast, natural cadence)
    en-US-BrianMultilingualNeural    (warmer, slightly younger)
    en-US-GuyNeural                  (classic news-anchor)
    en-US-DavisNeural                (polished, confident)
    en-US-TonyNeural                 (deeper, documentary-style)

OpenAI:  onyx (default), ash, sage
ElevenLabs: use a voice_id from your ElevenLabs account
"""

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path


# --- Script cleaning ---------------------------------------------------------

def clean_script(raw: str) -> str:
    """Strip stage directions, headers, and separators."""
    out = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            out.append("")
            continue
        if re.fullmatch(r"\[[^\]]+\]", s):
            continue
        if s == "---":
            continue
        if s.startswith("MORNING DOCKET"):
            continue
        if s.startswith("A daily brief"):
            continue
        if s.startswith("END OF EPISODE"):
            continue
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


# --- Chunking (paid APIs cap per-request chars; edge-tts handles long) -------

def chunk_text(text: str, max_chars: int = 3500) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in paragraphs:
        if len(buf) + len(p) + 2 <= max_chars:
            buf = (buf + "\n\n" + p).strip()
            continue
        if buf:
            chunks.append(buf)
            buf = ""
        if len(p) <= max_chars:
            buf = p
        else:
            sentences = re.split(r"(?<=[.!?])\s+", p)
            s_buf = ""
            for s in sentences:
                if len(s_buf) + len(s) + 1 <= max_chars:
                    s_buf = (s_buf + " " + s).strip()
                else:
                    if s_buf:
                        chunks.append(s_buf)
                    s_buf = s
            if s_buf:
                buf = s_buf
    if buf:
        chunks.append(buf)
    return chunks


# --- Providers ---------------------------------------------------------------

def synthesize_edge(chunks: list[str], voice: str, out_dir: Path) -> list[Path]:
    """Microsoft edge-tts — free, no API key."""
    import edge_tts

    async def _do_chunk(i: int, chunk: str, p: Path) -> None:
        print(f"  [edge-tts] chunk {i+1}/{len(chunks)} ({len(chunk)} chars) -> {p.name}")
        # rate="-5%" makes the delivery slightly slower for an NPR cadence
        communicate = edge_tts.Communicate(chunk, voice, rate="-5%")
        await communicate.save(str(p))

    async def _run() -> list[Path]:
        paths: list[Path] = []
        for i, chunk in enumerate(chunks):
            p = out_dir / f"chunk_{i:03d}.mp3"
            await _do_chunk(i, chunk, p)
            paths.append(p)
        return paths

    return asyncio.run(_run())


def synthesize_openai(chunks: list[str], voice: str, out_dir: Path) -> list[Path]:
    from openai import OpenAI
    client = OpenAI()
    paths: list[Path] = []
    for i, chunk in enumerate(chunks):
        p = out_dir / f"chunk_{i:03d}.mp3"
        print(f"  [OpenAI] chunk {i+1}/{len(chunks)} ({len(chunk)} chars) -> {p.name}")
        with client.audio.speech.with_streaming_response.create(
            model="tts-1-hd",
            voice=voice,
            input=chunk,
            response_format="mp3",
        ) as r:
            r.stream_to_file(p)
        paths.append(p)
    return paths


def synthesize_elevenlabs(chunks: list[str], voice_id: str, out_dir: Path) -> list[Path]:
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    paths: list[Path] = []
    for i, chunk in enumerate(chunks):
        p = out_dir / f"chunk_{i:03d}.mp3"
        print(f"  [ElevenLabs] chunk {i+1}/{len(chunks)} ({len(chunk)} chars) -> {p.name}")
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=chunk,
            output_format="mp3_44100_128",
        )
        with open(p, "wb") as f:
            for part in audio:
                f.write(part)
        paths.append(p)
    return paths


# --- Concatenate -------------------------------------------------------------

def concat_mp3s(parts: list[Path], out_path: Path) -> None:
    from pydub import AudioSegment
    combined = AudioSegment.empty()
    gap = AudioSegment.silent(duration=350)
    for p in parts:
        combined += AudioSegment.from_mp3(p) + gap
    combined.export(out_path, format="mp3", bitrate="128k")


# --- Main --------------------------------------------------------------------

DEFAULT_VOICES = {
    "edge": "en-US-AndrewMultilingualNeural",
    "openai": "onyx",
    "elevenlabs": "pNInz6obpgDQGcFmaJgB",  # "Adam"
}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="Path to the script .txt")
    ap.add_argument("--out", required=True, help="Path for the final MP3")
    ap.add_argument("--provider", choices=("edge", "openai", "elevenlabs"),
                    default="edge", help="(default: edge — free, no API key)")
    ap.add_argument("--voice", default=None,
                    help="Voice name/id. If omitted, uses a provider default.")
    args = ap.parse_args()

    voice = args.voice or DEFAULT_VOICES[args.provider]
    scr