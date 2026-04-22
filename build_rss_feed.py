"""
Morning Docket — private podcast RSS feed builder.

Scans a directory of MP3 episodes and generates a valid podcast RSS XML file
that Apple Podcasts / Overcast / Pocket Casts can subscribe to.

Designed for use with GitHub Pages hosting.

USAGE
-----
    python build_rss_feed.py \
        --episodes-dir ./episodes \
        --feed-out     ./feed/podcast.xml \
        --base-url     https://<username>.github.io/<repo>/episodes \
        --title        "Morning Docket" \
        --author       "Darren Caputo"

Filename convention expected: morning-docket-YYYY-MM-DD.mp3
"""

import argparse
import email.utils
import re
import xml.sax.saxutils as xu
from datetime import datetime, time, timezone
from pathlib import Path


def rfc2822(dt: datetime) -> str:
    return email.utils.format_datetime(dt)


def mp3_duration_seconds(path: Path) -> int:
    """Best-effort duration read. Uses mutagen if available; else returns 0."""
    try:
        from mutagen.mp3 import MP3  # type: ignore
        return int(MP3(str(path)).info.length)
    except Exception:
        return 0


def hms(total_sec: int) -> str:
    if total_sec <= 0:
        return "00:00:00"
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes-dir", required=True)
    ap.add_argument("--feed-out", required=True)
    ap.add_argument(
        "--base-url",
        required=True,
        help="Public URL prefix where the MP3s are hosted, e.g. https://user.github.io/repo/episodes",
    )
    ap.add_argument("--title", default="Morning Docket")
    ap.add_argument("--author", default="Darren Caputo")
    ap.add_argument(
        "--description",
        default=(
            "A daily 25-30 minute audio briefing for the general counsel of a media company. "
            "Privacy, IP, ad tech, publishing, corporate governance, legal tech, business AI, "
            "and the industry angles that matter."
        ),
    )
    ap.add_argument(
        "--image-url",
        default="",
        help="Optional URL to a 1400x1400 or larger cover image.",
    )
    args = ap.parse_args()

    episodes_dir = Path(args.episodes_dir)
    feed_path = Path(args.feed_out)
    feed_path.parent.mkdir(parents=True, exist_ok=True)

    mp3s = sorted(
        episodes_dir.glob("morning-docket-*.mp3"),
        key=lambda p: p.name,
        reverse=True,
    )

    now = datetime.now(timezone.utc)
    items_xml = []

    for p in mp3s:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", p.name)
        if not m:
            continue

        date_str = m.group(1)
        pub_dt = datetime.combine(
            datetime.strptime(date_str, "%Y-%m-%d").date(),
            time(5, 0, 0),
            tzinfo=timezone.utc,
        )
        size = p.stat().st_size
        duration = mp3_duration_seconds(p)
        url = f"{args.base_url.rstrip('/')}/{p.name}"
        title = f"Morning Docket — {date_str}"
        guid = url
        desc = f"Today's briefing for {date_str}."

        item = f"""
    <item>
      <title>{xu.escape(title)}</title>
      <description>{xu.escape(desc)}</description>
      <pubDate>{rfc2822(pub_dt)}</pubDate>
      <enclosure url="{xu.escape(url)}" length="{size}" type="audio/mpeg"/>
      <guid isPermaLink="true">{xu.escape(guid)}</guid>
      <itunes:duration>{hms(duration)}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>"""
        items_xml.append(item)

    image_block = ""
    if args.image_url:
        image_block = f"""
    <itunes:image href="{xu.escape(args.image_url)}"/>
    <image>
      <url>{xu.escape(args.image_url)}</url>
      <title>{xu.escape(args.title)}</title>
      <link>{xu.escape(args.base_url)}</link>
    </image>"""

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{xu.escape(args.title)}</title>
    <link>{xu.escape(args.base_url)}</link>
    <description>{xu.escape(args.description)}</description>
    <language>en-us</language>
    <lastBuildDate>{rfc2822(now)}</lastBuildDate>
    <itunes:author>{xu.escape(args.author)}</itunes:author>
    <itunes:owner>
      <itunes:name>{xu.escape(args.author)}</itunes:name>
    </itunes:owner>
    <itunes:category text="News"/>
    <itunes:category text="Business"/>
    <itunes:explicit>false</itunes:explicit>{image_block}
{''.join(items_xml)}
  </channel>
</rss>
"""
    feed_path.write_text(rss, encoding="utf-8")
    print(f"Wrote {feed_path} with {len(items_xml)} episodes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
