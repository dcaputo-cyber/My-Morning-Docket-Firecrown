"""
Morning Docket — local audio generator.

Converts a text script (with [BRACKETED] stage directions and `---` separators
automatically stripped) into a single MP3.

Default provider is Microsoft edge-tts: free, high-quality neural voice,
no API key required.
"""

#!/usr/bin/env python3

import argparse
import asyncio
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import edge_tts
from pydub import AudioSegment


DEFAULT_VOICE = "en-US-AriaNeural"
DEFAULT_RATE = "+0%"
DEFAULT_VOLUME = "+0%"
DEFAULT_MAX_CHARS = 2800
DEFAULT_RETRIES = 5
DEFAULT_INITIAL_BACKOFF_SECONDS = 20


def read_script(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Script file not found: {path}")

    text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError(f"Script file is empty: {path}")

    return normalize_text_for_tts(text)


def normalize_text_for_tts(text: str) -> str:
    """
    Basic cleanup to make plain-text scripts safer for TTS.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive whitespace.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common markdown artifacts that sound awkward when read aloud.
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")

    return text.strip()


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def split_text_into_chunks(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    """
    Splits text into chunks for edge-tts.

    Tries to split on paragraph boundaries first, then sentence boundaries,
    then hard splits only if absolutely necessary.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph

        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        # Paragraph itself is too long, so split by sentences.
        sentences = split_into_sentences(paragraph)

        sentence_buffer = ""

        for sentence in sentences:
            candidate_sentence = f"{sentence_buffer} {sentence}".strip() if sentence_buffer else sentence

            if len(candidate_sentence) <= max_chars:
                sentence_buffer = candidate_sentence
                continue

            if sentence_buffer:
                chunks.append(sentence_buffer)
                sentence_buffer = ""

            if len(sentence) <= max_chars:
                sentence_buffer = sentence
            else:
                # Sentence itself is too long. Hard split.
                hard_parts = hard_split(sentence, max_chars)
                chunks.extend(hard_parts[:-1])
                sentence_buffer = hard_parts[-1] if hard_parts else ""

        if sentence_buffer:
            current = sentence_buffer

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def split_into_sentences(text: str) -> list[str]:
    """
    Lightweight sentence splitting without external NLP dependencies.
    """
    pieces = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in pieces if p.strip()]


def hard_split(text: str, max_chars: int) -> list[str]:
    """
    Hard split by words while keeping chunks below max_chars.
    """
    words = text.split()
    chunks = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip() if current else word

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks


async def synthesize_chunk_with_retries(
    text: str,
    output_path: Path,
    voice: str,
    rate: str,
    volume: str,
    chunk_number: int,
    total_chunks: int,
    retries: int,
    initial_backoff_seconds: int,
) -> None:
    """
    Synthesizes one chunk with retry/backoff.

    This is the important long-term fix. A transient Microsoft/Bing/edge-tts
    websocket failure should retry this chunk instead of killing the whole job.
    """
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            print(
                f"[edge-tts] chunk {chunk_number}/{total_chunks}, "
                f"attempt {attempt}/{retries} -> {output_path.name}",
                flush=True,
            )

            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume,
            )

            await communicate.save(str(output_path))

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError(f"edge-tts created an empty file: {output_path}")

            print(
                f"[edge-tts] chunk {chunk_number}/{total_chunks} succeeded "
                f"({output_path.stat().st_size} bytes)",
                flush=True,
            )
            return

        except Exception as exc:
            last_error = exc
            print(
                f"[edge-tts] chunk {chunk_number}/{total_chunks} failed on "
                f"attempt {attempt}/{retries}: {repr(exc)}",
                flush=True,
            )

            # Remove partial/corrupt chunk file before retrying.
            try:
                if output_path.exists():
                    output_path.unlink()
            except Exception as cleanup_exc:
                print(f"Warning: could not remove partial file {output_path}: {cleanup_exc}", flush=True)

            if attempt < retries:
                backoff = initial_backoff_seconds * attempt
                print(f"Waiting {backoff} seconds before retrying chunk {chunk_number}...", flush=True)
                await asyncio.sleep(backoff)

    raise RuntimeError(
        f"Failed to synthesize chunk {chunk_number}/{total_chunks} "
        f"after {retries} attempts."
    ) from last_error


async def synthesize_all_chunks(
    chunks: list[str],
    chunk_dir: Path,
    voice: str,
    rate: str,
    volume: str,
    retries: int,
    initial_backoff_seconds: int,
) -> list[Path]:
    chunk_files: list[Path] = []

    total_chunks = len(chunks)

    for index, chunk in enumerate(chunks, start=1):
        chunk_file = chunk_dir / f"chunk_{index:03d}.mp3"

        await synthesize_chunk_with_retries(
            text=chunk,
            output_path=chunk_file,
            voice=voice,
            rate=rate,
            volume=volume,
            chunk_number=index,
            total_chunks=total_chunks,
            retries=retries,
            initial_backoff_seconds=initial_backoff_seconds,
        )

        chunk_files.append(chunk_file)

    return chunk_files


def combine_mp3_chunks_with_pydub(chunk_files: list[Path], output_path: Path) -> None:
    if not chunk_files:
        raise ValueError("No chunk files to combine.")

    combined = AudioSegment.empty()

    for chunk_file in chunk_files:
        if not chunk_file.exists():
            raise FileNotFoundError(f"Missing chunk file: {chunk_file}")

        if chunk_file.stat().st_size == 0:
            raise RuntimeError(f"Chunk file is empty: {chunk_file}")

        print(f"Adding chunk to final MP3: {chunk_file.name}", flush=True)
        combined += AudioSegment.from_file(chunk_file, format="mp3")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_output = output_path.with_suffix(".tmp.mp3")
    combined.export(tmp_output, format="mp3")

    if not tmp_output.exists() or tmp_output.stat().st_size == 0:
        raise RuntimeError(f"Failed to create final MP3: {tmp_output}")

    tmp_output.replace(output_path)

    print(f"Final MP3 written: {output_path}", flush=True)
    print(f"Final MP3 size: {output_path.stat().st_size} bytes", flush=True)


def verify_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is not available. Install ffmpeg before running this script.")

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except Exception as exc:
        raise RuntimeError("ffmpeg exists but could not be executed.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a podcast MP3 from a text script using edge-tts."
    )

    parser.add_argument(
        "--script",
        required=True,
        help="Path to the input episode script text file.",
    )

    parser.add_argument(
        "--out",
        required=True,
        help="Path to the output MP3 file.",
    )

    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help=f"TTS voice to use. Default: {DEFAULT_VOICE}",
    )

    parser.add_argument(
        "--rate",
        default=DEFAULT_RATE,
        help=f"TTS rate adjustment. Default: {DEFAULT_RATE}",
    )

    parser.add_argument(
        "--volume",
        default=DEFAULT_VOLUME,
        help=f"TTS volume adjustment. Default: {DEFAULT_VOLUME}",
    )

    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Maximum characters per TTS chunk. Default: {DEFAULT_MAX_CHARS}",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=f"Retries per chunk. Default: {DEFAULT_RETRIES}",
    )

    parser.add_argument(
        "--initial-backoff-seconds",
        type=int,
        default=DEFAULT_INITIAL_BACKOFF_SECONDS,
        help=f"Initial retry backoff in seconds. Default: {DEFAULT_INITIAL_BACKOFF_SECONDS}",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    script_path = Path(args.script)
    output_path = Path(args.out)

    print(f"Script: {script_path}", flush=True)
    print(f"Output: {output_path}", flush=True)
    print(f"Voice: {args.voice}", flush=True)
    print(f"Rate: {args.rate}", flush=True)
    print(f"Volume: {args.volume}", flush=True)
    print(f"Max chars per chunk: {args.max_chars}", flush=True)
    print(f"Retries per chunk: {args.retries}", flush=True)

    verify_ffmpeg_available()

    text = read_script(script_path)

    word_count = count_words(text)
    estimated_minutes = word_count / 155

    print(
        f"Script: {word_count} words, {len(text)} chars "
        f"(~{estimated_minutes:.1f} min at 155 wpm)",
        flush=True,
    )

    chunks = split_text_into_chunks(text, max_chars=args.max_chars)

    if not chunks:
        raise ValueError("No TTS chunks were generated from the script.")

    print(f"Split into {len(chunks)} chunks.", flush=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="morning-docket-tts-") as tmp:
        chunk_dir = Path(tmp)

        start_time = time.time()

        chunk_files = asyncio.run(
            synthesize_all_chunks(
                chunks=chunks,
                chunk_dir=chunk_dir,
                voice=args.voice,
                rate=args.rate,
                volume=args.volume,
                retries=args.retries,
                initial_backoff_seconds=args.initial_backoff_seconds,
            )
        )

        combine_mp3_chunks_with_pydub(chunk_files, output_path)

        elapsed = time.time() - start_time
        print(f"MP3 generation completed in {elapsed:.1f} seconds.", flush=True)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        raise
