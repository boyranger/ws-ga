#!/usr/bin/env python3
"""Small Scrapling-based web browsing helper.

Examples:
  python3 tools/scrapling_browser.py fetch https://example.com
  python3 tools/scrapling_browser.py fetch https://example.com --css 'h1::text'
  python3 tools/scrapling_browser.py links https://example.com
  python3 tools/scrapling_browser.py text https://example.com --find 'pricing' --partial
  python3 tools/scrapling_browser.py fetch https://example.com --dynamic --headless
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


MAX_TEXT = 4000


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def trim(value: str, limit: int = MAX_TEXT) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[:limit] + "\n...[truncated]"


def load_fetcher(dynamic: bool, stealthy: bool):
    try:
        from scrapling.fetchers import DynamicFetcher, Fetcher, StealthyFetcher
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Scrapling is not installed. Run: python3 -m pip install -r requirements-scrapling.txt"
        ) from exc

    if stealthy:
        return StealthyFetcher
    if dynamic:
        return DynamicFetcher
    return Fetcher


def fetch_page(args):
    FetcherClass = load_fetcher(args.dynamic, args.stealthy)
    selector_config = {"adaptive": args.adaptive} if args.adaptive else None

    kwargs: dict[str, Any] = {}
    if selector_config:
        kwargs["selector_config"] = selector_config
    if args.timeout:
        kwargs["timeout"] = args.timeout
    if args.dynamic or args.stealthy:
        kwargs["headless"] = args.headless
        kwargs["network_idle"] = args.network_idle

    page = FetcherClass.get(args.url, **kwargs)
    return page


def cmd_fetch(args):
    page = fetch_page(args)
    payload = {
        "url": getattr(page, "url", args.url),
        "status": getattr(page, "status", None),
        "reason": getattr(page, "reason", None),
        "encoding": getattr(page, "encoding", None),
    }

    if args.css:
        values = page.css(args.css)
        if args.all:
            payload["css"] = args.css
            payload["result"] = [trim(item.text if hasattr(item, "text") else str(item)) for item in values[: args.limit]]
        else:
            first = values[0] if values else None
            payload["css"] = args.css
            payload["result"] = trim(first.text if first is not None and hasattr(first, "text") else str(first or ""))
    elif args.xpath:
        values = page.xpath(args.xpath)
        if args.all:
            payload["xpath"] = args.xpath
            payload["result"] = [trim(item.text if hasattr(item, "text") else str(item)) for item in values[: args.limit]]
        else:
            first = values[0] if values else None
            payload["xpath"] = args.xpath
            payload["result"] = trim(first.text if first is not None and hasattr(first, "text") else str(first or ""))
    else:
        payload["text"] = trim(getattr(page, "text", ""))

    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_links(args):
    page = fetch_page(args)
    links = []
    for node in page.css("a[href]")[: args.limit]:
        href = node.attrib.get("href")
        text = trim(node.text or "", 200)
        if href:
            links.append({"text": text, "href": page.urljoin(href)})
    print(json.dumps({"url": getattr(page, "url", args.url), "links": links}, ensure_ascii=False, indent=2))


def cmd_text(args):
    page = fetch_page(args)
    results = page.find_by_text(
        args.find,
        partial=args.partial,
        first_match=not args.all,
        case_sensitive=args.case_sensitive,
    )
    if not args.all:
        results = [results] if results else []
    data = []
    for item in results[: args.limit]:
        if not item:
            continue
        data.append(
            {
                "text": trim(item.text or "", 300),
                "html": trim(str(item), 700),
            }
        )
    print(json.dumps({"url": getattr(page, "url", args.url), "matches": data}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Browse the web with Scrapling")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("url")
        p.add_argument("--dynamic", action="store_true", help="Use DynamicFetcher")
        p.add_argument("--stealthy", action="store_true", help="Use StealthyFetcher")
        p.add_argument("--headless", action="store_true", help="Run browser fetchers headless")
        p.add_argument("--network-idle", action="store_true", help="Wait for network idle in browser fetchers")
        p.add_argument("--adaptive", action="store_true", help="Enable Scrapling adaptive parser mode")
        p.add_argument("--timeout", type=float, default=None, help="Optional request timeout")
        p.add_argument("--limit", type=int, default=10, help="Max results to print")

    fetch = sub.add_parser("fetch", help="Fetch page text or selector output")
    add_common(fetch)
    fetch.add_argument("--css", help="CSS selector to extract")
    fetch.add_argument("--xpath", help="XPath selector to extract")
    fetch.add_argument("--all", action="store_true", help="Return multiple selector results")
    fetch.set_defaults(func=cmd_fetch)

    links = sub.add_parser("links", help="List links on a page")
    add_common(links)
    links.set_defaults(func=cmd_links)

    text = sub.add_parser("text", help="Find elements by visible text")
    add_common(text)
    text.add_argument("--find", required=True, help="Text to search for")
    text.add_argument("--partial", action="store_true", help="Use partial text matching")
    text.add_argument("--case-sensitive", action="store_true", help="Enable case-sensitive matching")
    text.add_argument("--all", action="store_true", help="Return all matches")
    text.set_defaults(func=cmd_text)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.dynamic and args.stealthy:
        eprint("Pick only one of --dynamic or --stealthy.")
        return 2
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
