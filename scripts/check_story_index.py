#!/usr/bin/env python3
"""Compare Inkstone's live story links with references/story_index.md."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse


DEFAULT_STORIES_URL = "https://inkstone.blog/stories"
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INDEX = SKILL_ROOT / "references" / "story_index.md"


def fetch_html(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "InkstoneOutreachIndexCheck/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", "replace")


def live_story_urls(html: str, base_url: str) -> set[str]:
    excluded = {"/", "/stories", "/explore-themes", "/about", "#"}
    urls: set[str] = set()
    for href in re.findall(r'<a\s+[^>]*href="([^"]+)"', html, flags=re.I):
        if not href.startswith("/") or href in excluded:
            continue
        if href.startswith(("/theme/", "/search", "/uploads/")):
            continue
        urls.add(urljoin(base_url, href).rstrip("/"))
    return urls


def indexed_story_urls(index_text: str) -> set[str]:
    return {
        match.rstrip("/")
        for match in re.findall(r"^- \*\*URL\*\*: (https?://\S+)$", index_text, flags=re.M)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether Inkstone's story index is current.")
    parser.add_argument("--stories-url", default=DEFAULT_STORIES_URL)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--html", type=Path, help="Use previously fetched HTML instead of network access.")
    args = parser.parse_args()

    try:
        html = args.html.read_text(encoding="utf-8") if args.html else fetch_html(args.stories_url)
        index_text = args.index.read_text(encoding="utf-8")
    except (OSError, urllib.error.URLError) as exc:
        print(f"Index check unavailable: {exc}", file=sys.stderr)
        return 2

    base = f"{urlparse(args.stories_url).scheme}://{urlparse(args.stories_url).netloc}"
    live = live_story_urls(html, base)
    indexed = indexed_story_urls(index_text)
    missing = sorted(live - indexed)
    removed = sorted(indexed - live)

    print(f"Live stories: {len(live)}")
    print(f"Indexed stories: {len(indexed)}")
    for url in missing:
        print(f"MISSING {url}")
    for url in removed:
        print(f"NOT_LIVE {url}")

    if missing or removed:
        return 1
    print("Story index is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
