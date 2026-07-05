#!/usr/bin/env python3
"""Score outreach candidate communities from JSON and emit a review table.

Input JSON shape:
[
  {
    "title": "Thread or community title",
    "url": "https://...",
    "platform": "Reddit",
    "topic": "abortion ethics",
    "thread_text": "Visible discussion excerpt...",
    "rules": "No spam. Self-promo allowed if relevant.",
    "notes": "Optional notes"
  }
]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BLOCKING_RULE_PATTERNS = [
    r"\bno self[- ]promo(?:tion)?\b",
    r"\bself[- ]promo(?:tion)? (?:is )?(?:not allowed|banned|prohibited)\b",
    r"\bno advertising\b",
    r"\bno outside links\b",
    r"\bno external links\b",
    r"\bno promotion\b",
]

RISK_PATTERNS = [
    r"\bmedical advice\b",
    r"\blegal advice\b",
    r"\bcrisis\b",
    r"\bsuicide\b",
    r"\bminor(?:s)?\b",
    r"\bharass(?:ment|ing)?\b",
    r"\bhate speech\b",
]


@dataclass
class ScoredCandidate:
    title: str
    url: str
    platform: str
    score: int
    rule_status: str
    risk: str
    recommendation: str
    reasons: list[str]


def words(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9'-]{2,}", text.lower())
        if token
        not in {
            "the",
            "and",
            "for",
            "with",
            "that",
            "this",
            "from",
            "have",
            "has",
            "are",
            "was",
            "were",
        }
    }


def has_pattern(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in patterns)


def score_candidate(candidate: dict[str, Any], keywords: set[str]) -> ScoredCandidate:
    title = str(candidate.get("title") or "Untitled")
    url = str(candidate.get("url") or "")
    platform = str(candidate.get("platform") or "Unknown")
    rules = str(candidate.get("rules") or "")
    searchable = " ".join(
        str(candidate.get(field) or "")
        for field in ("title", "topic", "thread_text", "rules", "notes", "platform")
    )
    candidate_words = words(searchable)
    overlap = keywords & candidate_words

    score = min(65, len(overlap) * 9)
    reasons: list[str] = []
    if overlap:
        reasons.append("keyword overlap: " + ", ".join(sorted(overlap)[:8]))

    if re.search(r"\b(allowed|welcome|weekly thread|share|resources|links)\b", rules, flags=re.I):
        score += 15
        reasons.append("rules appear link-friendly")
    if re.search(r"\b(question|how|why|argument|debate|discussion|source|resource)\b", searchable, flags=re.I):
        score += 10
        reasons.append("discussion format appears suitable")
    if url:
        score += 5

    blocked = has_pattern(BLOCKING_RULE_PATTERNS, rules)
    risky = has_pattern(RISK_PATTERNS, searchable)

    if blocked:
        score = min(score, 25)
        rule_status = "likely blocks promotion"
        recommendation = "do not post"
        reasons.append("blocking rule language found")
    elif not rules.strip():
        score = min(score, 70)
        rule_status = "needs manual rule check"
        recommendation = "needs manual rule check"
        reasons.append("no rules captured")
    else:
        rule_status = "rules need final manual check"
        recommendation = "postable after user review" if score >= 60 else "revise"

    if risky:
        score = min(score, 55)
        recommendation = "needs manual rule check" if recommendation != "do not post" else recommendation
        reasons.append("sensitive-topic risk language found")

    risk = "medium" if risky or not rules.strip() else "low"
    if blocked:
        risk = "high"

    return ScoredCandidate(
        title=title,
        url=url,
        platform=platform,
        score=max(0, min(100, score)),
        rule_status=rule_status,
        risk=risk,
        recommendation=recommendation,
        reasons=reasons or ["insufficient context"],
    )


def load_candidates(path: str) -> list[dict[str, Any]]:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("Input must be a JSON list of candidate objects.")
    return [item for item in data if isinstance(item, dict)]


def markdown_table(scored: list[ScoredCandidate]) -> str:
    lines = [
        "| Target | Fit | Rule Status | Risk | Recommendation |",
        "|---|---:|---|---|---|",
    ]
    for item in sorted(scored, key=lambda row: row.score, reverse=True):
        target = f"{item.platform}: {item.title}"
        if item.url:
            target = f"[{target}]({item.url})"
        lines.append(
            "| {target} | {score} | {rules} | {risk} | {rec} |".format(
                target=target.replace("|", "\\|"),
                score=item.score,
                rules=item.rule_status.replace("|", "\\|"),
                risk=item.risk,
                rec=item.recommendation.replace("|", "\\|"),
            )
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Score outreach candidates for human-reviewed promotion.")
    parser.add_argument("candidates_json", help="Path to candidates JSON, or '-' for stdin.")
    parser.add_argument("--content", required=True, help="Summary of the article, video, site, or offer.")
    args = parser.parse_args()

    keywords = words(args.content)
    if not keywords:
        raise ValueError("--content must contain meaningful keywords.")

    candidates = load_candidates(args.candidates_json)
    scored = [score_candidate(candidate, keywords) for candidate in candidates]

    print("## Candidate Scores")
    print()
    print(markdown_table(scored))
    print()
    print("## Notes")
    print()
    for item in sorted(scored, key=lambda row: row.score, reverse=True):
        print(f"- {item.platform}: {item.title}: {'; '.join(item.reasons)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
