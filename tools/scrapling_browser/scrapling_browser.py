#!/usr/bin/env python3
"""Small Scrapling-based web browsing helper.

Especially useful for browsing GitHub repos/pages to find code relevant to a task.

Examples:
  python3 tools/scrapling_browser/scrapling_browser.py fetch https://example.com
  python3 tools/scrapling_browser/scrapling_browser.py fetch https://example.com --css 'h1::text'
  python3 tools/scrapling_browser/scrapling_browser.py links https://example.com
  python3 tools/scrapling_browser/scrapling_browser.py text https://example.com --find 'pricing' --partial
  python3 tools/scrapling_browser/scrapling_browser.py github-search 'fastapi auth middleware'
  python3 tools/scrapling_browser/scrapling_browser.py github-readme https://github.com/tiangolo/fastapi
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any
from urllib.parse import quote_plus, urljoin, urlparse


MAX_TEXT = 4000
GITHUB_ROOT = "https://github.com"


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
            "Scrapling is not installed. Run: python3 -m pip install -r tools/scrapling_browser/requirements.txt"
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


def fetch_url(url: str, args):
    temp_args = argparse.Namespace(
        dynamic=args.dynamic,
        stealthy=args.stealthy,
        adaptive=args.adaptive,
        timeout=args.timeout,
        headless=args.headless,
        network_idle=args.network_idle,
        url=url,
    )
    return fetch_page(temp_args)


def normalize_github_url(url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return GITHUB_ROOT + url
    return urljoin(GITHUB_ROOT + "/", url)


def repo_slug_from_url(url: str) -> str | None:
    path = urlparse(normalize_github_url(url)).path.strip("/")
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return None


def page_meta(page, fallback_url: str) -> dict[str, Any]:
    return {
        "url": getattr(page, "url", fallback_url),
        "status": getattr(page, "status", None),
        "reason": getattr(page, "reason", None),
        "encoding": getattr(page, "encoding", None),
    }


def selector_items(values, limit: int) -> list[str]:
    items: list[str] = []
    for item in values[:limit]:
        if hasattr(item, "text"):
            items.append(trim(item.text or ""))
        else:
            items.append(trim(str(item)))
    return items


def visible_text(node: Any) -> str:
    return trim(getattr(node, "text", "") or "", 300)


def github_repo_candidates(page, limit: int) -> list[dict[str, str]]:
    seen: set[str] = set()
    results: list[dict[str, str]] = []
    for node in page.css("a[href]"):
        href = node.attrib.get("href", "")
        if not href.startswith("/"):
            continue
        path = href.split("?", 1)[0].strip("/")
        parts = [p for p in path.split("/") if p]
        if len(parts) != 2:
            continue
        if parts[0] in {
            "features",
            "topics",
            "collections",
            "orgs",
            "organizations",
            "marketplace",
            "settings",
            "search",
            "login",
            "signup",
            "explore",
            "sponsors",
            "apps",
            "users",
            "account",
            "pulls",
            "issues",
            "codespaces",
        }:
            continue
        slug = f"{parts[0]}/{parts[1]}"
        if slug in seen:
            continue
        text = visible_text(node)
        if not text:
            continue
        seen.add(slug)
        results.append(
            {
                "repo": slug,
                "text": text,
                "href": normalize_github_url(href),
            }
        )
        if len(results) >= limit:
            break
    return results


def github_code_candidates(page, limit: int) -> list[dict[str, str]]:
    seen: set[str] = set()
    results: list[dict[str, str]] = []
    for node in page.css("a[href]"):
        href = node.attrib.get("href", "")
        if "/blob/" not in href:
            continue
        full = normalize_github_url(href)
        if full in seen:
            continue
        seen.add(full)
        results.append(
            {
                "text": visible_text(node),
                "href": full,
            }
        )
        if len(results) >= limit:
            break
    return results


def repo_readme_text(page) -> str:
    selectors = [
        "article.markdown-body",
        "#readme article",
        "[data-testid='readme'] article",
        ".markdown-body",
    ]
    for sel in selectors:
        matches = page.css(sel)
        if matches:
            text = trim(matches[0].text or "")
            if text:
                return text
    return ""


def cmd_fetch(args):
    page = fetch_page(args)
    payload = page_meta(page, args.url)

    if args.css:
        values = page.css(args.css)
        payload["css"] = args.css
        payload["result"] = selector_items(values, args.limit) if args.all else (selector_items(values, 1)[0] if values else "")
    elif args.xpath:
        values = page.xpath(args.xpath)
        payload["xpath"] = args.xpath
        payload["result"] = selector_items(values, args.limit) if args.all else (selector_items(values, 1)[0] if values else "")
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


def cmd_github_search(args):
    query = quote_plus(args.query)
    url = f"{GITHUB_ROOT}/search?q={query}&type={args.search_type}"
    page = fetch_url(url, args)

    payload: dict[str, Any] = page_meta(page, url)
    payload["query"] = args.query
    payload["search_type"] = args.search_type

    if args.search_type == "repositories":
        payload["results"] = github_repo_candidates(page, args.limit)
    elif args.search_type == "code":
        payload["results"] = github_code_candidates(page, args.limit)
    else:
        payload["results"] = []

    if not payload["results"]:
        payload["hint"] = "No parsed results found. GitHub may have changed markup or blocked the fetch mode. Try --dynamic or inspect the raw search page with fetch."

    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_github_links(args):
    page = fetch_url(normalize_github_url(args.url), args)
    seen: set[str] = set()
    links: list[dict[str, str]] = []
    for node in page.css("a[href]"):
        href = node.attrib.get("href", "")
        full = normalize_github_url(href) if href.startswith("/") else href
        if not full.startswith(GITHUB_ROOT):
            continue
        if full in seen:
            continue
        seen.add(full)
        text = visible_text(node)
        if not text:
            continue
        links.append({"text": text, "href": full})
        if len(links) >= args.limit:
            break
    print(json.dumps({"url": getattr(page, "url", args.url), "links": links}, ensure_ascii=False, indent=2))


def cmd_github_readme(args):
    page = fetch_url(normalize_github_url(args.url), args)
    print(
        json.dumps(
            {
                **page_meta(page, args.url),
                "repo": repo_slug_from_url(args.url),
                "readme": repo_readme_text(page),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_code_find(args):
    page = fetch_url(normalize_github_url(args.url), args)
    page_text = getattr(page, "text", "") or ""
    lines = page_text.splitlines()
    matches: list[dict[str, Any]] = []
    pattern = re.compile(args.find if args.regex else re.escape(args.find), 0 if args.case_sensitive else re.IGNORECASE)

    for idx, line in enumerate(lines, start=1):
        if pattern.search(line):
            matches.append({"line": idx, "text": trim(line, 300)})
            if len(matches) >= args.limit:
                break

    print(
        json.dumps(
            {
                **page_meta(page, args.url),
                "query": args.find,
                "regex": args.regex,
                "matches": matches,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


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

    def add_fetcher_flags_only(p: argparse.ArgumentParser) -> None:
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

    gh_search = sub.add_parser("github-search", help="Search GitHub for repositories or code")
    gh_search.add_argument("query")
    gh_search.add_argument("--search-type", choices=["repositories", "code"], default="repositories")
    add_fetcher_flags_only(gh_search)
    gh_search.set_defaults(func=cmd_github_search)

    gh_links = sub.add_parser("github-links", help="List GitHub links from a repo or page")
    add_common(gh_links)
    gh_links.set_defaults(func=cmd_github_links)

    gh_readme = sub.add_parser("github-readme", help="Extract README text from a GitHub repository page")
    add_common(gh_readme)
    gh_readme.set_defaults(func=cmd_github_readme)

    code_find = sub.add_parser("code-find", help="Find text or regex snippets in fetched page text")
    add_common(code_find)
    code_find.add_argument("--find", required=True, help="Text or regex to search for")
    code_find.add_argument("--regex", action="store_true", help="Treat --find as regex")
    code_find.add_argument("--case-sensitive", action="store_true", help="Enable case-sensitive matching")
    code_find.set_defaults(func=cmd_code_find)

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
