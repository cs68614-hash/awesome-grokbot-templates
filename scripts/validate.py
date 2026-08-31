#!/usr/bin/env python3
"""Check templates.json and that every README listing matches it."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARE_RE = re.compile(r"^https://x\.ai/bot/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)?$")
LISTING_RE = re.compile(
    r"^- \[([^\]]+)\]\((https://x\.ai/bot/[^)]+)\) — (.+?)(?: \[@([A-Za-z0-9_]+)\]\(https://x\.com/\4\))?$"
)
README_FILES = [
    "README.md",
    "README.zh-CN.md",
    "README.zh-TW.md",
    "README.ja.md",
    "README.ko.md",
    "README.es.md",
    "README.fr.md",
    "README.de.md",
    "README.pt-BR.md",
    "README.ru.md",
]
ALLOWED = {
    "name",
    "description",
    "category",
    "twitter",
    "share_url",
    "scraped_at",
}
FORBIDDEN = (
    "templatebot.lol",
    "grokbot.wtf",
    "TemplateBot",
    "bot-directory",
    "keshav",
)


def bot_id(share_url: str) -> str:
    return share_url.removeprefix("https://x.ai/bot/").split("/")[0]


def main() -> int:
    errors: list[str] = []
    payload = json.loads((ROOT / "data" / "templates.json").read_text())
    items = payload.get("templates") or []
    seen: dict[str, str] = {}

    for i, item in enumerate(items):
        extra = set(item) - ALLOWED
        if extra:
            errors.append(f"templates[{i}] unexpected fields: {sorted(extra)}")
        missing = ALLOWED - set(item)
        if missing:
            errors.append(f"templates[{i}] missing fields: {sorted(missing)}")
        url = item.get("share_url", "")
        if not SHARE_RE.match(url):
            errors.append(f"templates[{i}] bad share_url: {url!r}")
            continue
        ident = bot_id(url)
        if ident in seen:
            errors.append(f"duplicate id {ident}: {seen[ident]!r} and {item.get('name')!r}")
        else:
            seen[ident] = item.get("name", "")
        twitter = item.get("twitter")
        if twitter is not None and (
            not isinstance(twitter, str) or twitter.startswith("@") or " " in twitter
        ):
            errors.append(f"templates[{i}] twitter must be a bare handle or null")
        blob = json.dumps(item, ensure_ascii=False)
        for host in FORBIDDEN:
            if host in blob:
                errors.append(f"templates[{i}] must not mention {host}")

    by_url = {item["share_url"]: item for item in items if "share_url" in item}

    for name in ["CONTRIBUTING.md", *README_FILES]:
        text = (ROOT / name).read_text()
        for host in FORBIDDEN:
            if host in text:
                errors.append(f"{name} mentions {host}")
        if "grokbot-templates.com" not in text:
            errors.append(f"{name} missing directory link grokbot-templates.com")
        if name == "CONTRIBUTING.md":
            if "grokbot-templates.com/submit" not in text:
                errors.append(f"{name} missing submit URL grokbot-templates.com/submit")
            continue
        listed = []
        for line in text.splitlines():
            if not line.startswith("- ["):
                continue
            if "](https://x.ai/bot/" not in line:
                continue
            m = LISTING_RE.match(line)
            if not m:
                errors.append(f"{name} bad listing line: {line}")
                continue
            title, url, desc, handle = m.groups()
            listed.append(url)
            item = by_url.get(url)
            if item is None:
                errors.append(f"{name} listing not in templates.json: {url}")
                continue
            if item["name"] != title:
                errors.append(f"{name} name mismatch for {url}: {title!r} vs {item['name']!r}")
            expected = item.get("twitter")
            if expected and handle != expected:
                errors.append(f"{name} twitter mismatch for {url}")
            if not expected and handle:
                errors.append(f"{name} unexpected twitter on {url}")
            # Localized READMEs may use translated one-liners; English must match templates.json.
            if name == "README.md" and item["description"] != desc:
                errors.append(f"{name} description mismatch for {url}")
        missing = set(by_url) - set(listed)
        extra = set(listed) - set(by_url)
        if missing:
            errors.append(f"{name} missing {len(missing)} share_url(s) from templates.json")
        if extra:
            errors.append(f"{name} has {len(extra)} listing(s) not in templates.json")

    if errors:
        print("validate failed:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"ok: {len(items)} templates, {len(README_FILES)} READMEs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
