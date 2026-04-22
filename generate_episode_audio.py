"""
Morning Docket — local audio generator.

Converts a text script (with [BRACKETED] stage directions and `---` separators
automatically stripped) into a single MP3.

Default provider is Microsoft edge-tts: free, high-quality neural voice,
no API key required.
"""

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path


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


def synthesize_edge(chunks: list[str], voice: str, out_dir: Path) -> list[Path]:
    import edge_tts

    async def _do_chunk(i: int, chunk: str, p: Path) -> None:
        print(f"  [edge-tts] chunk {i+1}/{len(chunks)} ({len(chunk)} chars) -> {p.name}")
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


def concat_mp3s(parts: list[Path], out_path: Path) -> None:
    from pydub import AudioSegment

    combined = AudioSegment.empty()
    gap = AudioSegment.silent(duration=350)
    for p in parts:
        combined += AudioSegment.from_mp3(p) + gap
    combined.export(out_path, format="mp3", bitrate="128k")


DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="Path to the script .txt")
    ap.add_argument("--out", required=True, help="Path for the final MP3")
    ap.add_argument("--voice", default=DEFAULT_VOICE, help="Edge voice name")
    args = ap.parse_args()

    script_path = Path(args.script)
    out_path = Path(args.out)

    if not script_path.exists():
        print(f"ERROR: script not found: {script_path}", file=sys.stderr)
        return 1

    raw = script_path.read_text(encoding="utf-8")
    text = clean_script(raw)

    if not text.strip():
        print("ERROR: cleaned script is empty", file=sys.stderr)
        return 1

    words = len(text.split())
    chars = len(text)
    print(f"Script: {words} words, {chars} chars (~{words/155:.1f} min at 155 wpm)")
    print(f"Voice: {args.voice}")

    chunks = chunk_text(text)
    print(f"Split into {len(chunks)} chunks.")

    work_dir = out_path.parent / f".{out_path.stem}_chunks"
    work_dir.mkdir(parents=True, exist_ok=True)

    parts = synthesize_edge(chunks, args.voice, work_dir)

    print(f"Concatenating {len(parts)} chunks -> {out_path}")
    concat_mp3s(parts, out_path)

    if out_path.exists():
        print(f"Done. {out_path}")
        return 0

    print(f"ERROR: output not created: {out_path}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
