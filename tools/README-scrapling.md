# Scrapling web browsing helper

This workspace includes a small helper for web browsing/surfing with [Scrapling](https://github.com/D4Vinci/Scrapling).

## Files

- `tools/scrapling_browser.py` — CLI wrapper around Scrapling fetchers
- `requirements-scrapling.txt` — Python dependency file

## Install

```bash
python3 -m pip install -r requirements-scrapling.txt
python3 -m playwright install chromium
```

Notes:
- Plain HTTP fetching works with Scrapling once the package is installed.
- `DynamicFetcher` / `StealthyFetcher` need browser dependencies.
- If Playwright browser install is not wanted yet, you can still use the basic `Fetcher` mode.

## Usage

Fetch visible page text:

```bash
python3 tools/scrapling_browser.py fetch https://example.com
```

Extract with CSS:

```bash
python3 tools/scrapling_browser.py fetch https://example.com --css 'h1::text'
```

Extract multiple links:

```bash
python3 tools/scrapling_browser.py links https://example.com
```

Find elements by text:

```bash
python3 tools/scrapling_browser.py text https://example.com --find 'pricing' --partial --all
```

Use browser rendering for dynamic pages:

```bash
python3 tools/scrapling_browser.py fetch https://example.com --dynamic --headless --network-idle
```

Use stealthier browser fetching:

```bash
python3 tools/scrapling_browser.py fetch https://example.com --stealthy --headless --network-idle
```

## Output format

All commands print JSON so they are easy to pipe into other scripts/tools.
