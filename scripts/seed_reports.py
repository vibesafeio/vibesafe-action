#!/usr/bin/env python3
"""Seed web/seed_reports.json with scans of well-known repos.

Usage:
    python3 scripts/seed_reports.py

Scans each repo locally via cli_scanner.py and writes results to
web/seed_reports.json, which server.py loads on startup to populate
the sitemap.xml with permanent SEO URLs even after Render restarts.

Skip failed/timeout repos automatically; existing entries are preserved
so re-runs only add new repos.
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SEED_FILE = PROJECT_DIR / "web" / "seed_reports.json"
CLI_SCANNER = PROJECT_DIR / "tools" / "cli_scanner.py"

# Safe, medium-sized repos — vibe coding ecosystem + popular frameworks
# Intentionally excluded: OWASP/WebGoat, juice-shop (intentionally vulnerable)
# Excluded: next.js, react, django, supabase (too large → likely timeout)
REPOS = [
    "https://github.com/tiangolo/fastapi",
    "https://github.com/pallets/flask",
    "https://github.com/expressjs/express",
    "https://github.com/streamlit/streamlit",
    "https://github.com/gradio-app/gradio",
    "https://github.com/reflex-dev/reflex",
    "https://github.com/crewAIInc/crewAI",
    "https://github.com/continuedev/continue",
    "https://github.com/Codium-ai/pr-agent",
    "https://github.com/tiangolo/full-stack-fastapi-template",
    "https://github.com/shadcn-ui/ui",
    "https://github.com/trpc/trpc",
    "https://github.com/drizzle-team/drizzle-orm",
    "https://github.com/tailwindlabs/tailwindcss",
    "https://github.com/payloadcms/payload",
    "https://github.com/anthropics/anthropic-sdk-python",
    "https://github.com/openai/openai-python",
]

REPO_PATH_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def parse_owner_repo(url: str) -> tuple[str, str] | None:
    m = re.search(r"github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    if not (REPO_PATH_RE.match(owner) and REPO_PATH_RE.match(repo)):
        return None
    return owner, repo


def scan_repo(url: str) -> dict | None:
    parsed = parse_owner_repo(url)
    if not parsed:
        print(f"  [SKIP] Cannot parse URL: {url}")
        return None
    owner, repo = parsed
    print(f"  Scanning {owner}/{repo} ...", end=" ", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, str(CLI_SCANNER), url, "--json", "--light"],
            capture_output=True,
            text=True,
            timeout=120,
            env={"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
                 "HOME": str(Path.home()),
                 "SEMGREP_MAX_MEMORY": "256"},
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            score = data.get("score", {}).get("score", "?")
            grade = data.get("score", {}).get("grade", "?")
            print(f"score={score} grade={grade}")
            return {
                "owner": owner,
                "repo": repo,
                "url": url,
                "results": data,
                "scanned_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        else:
            err = (result.stdout or result.stderr or "")[:200]
            print(f"FAILED (exit {result.returncode}): {err}")
            return None
    except subprocess.TimeoutExpired:
        print("TIMEOUT (120s) — skipping")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def main() -> None:
    # Load existing seed file to preserve already-scanned entries
    if SEED_FILE.exists():
        existing: dict = json.loads(SEED_FILE.read_text())
        print(f"Loaded {len(existing)} existing seed entries")
    else:
        existing = {}

    total = len(REPOS)
    succeeded = 0
    skipped = 0

    for i, url in enumerate(REPOS, 1):
        parsed = parse_owner_repo(url)
        if not parsed:
            skipped += 1
            continue
        owner, repo = parsed
        key = f"{owner}/{repo}"

        if key in existing:
            print(f"[{i}/{total}] {key} — already seeded, skipping")
            skipped += 1
            continue

        print(f"[{i}/{total}] {key}")
        report = scan_repo(url)
        if report:
            existing[key] = report
            # Write after each success so partial runs are preserved
            SEED_FILE.write_text(json.dumps(existing, indent=2))
            succeeded += 1
        else:
            skipped += 1

    print(f"\nDone. {succeeded} new scans, {skipped} skipped/failed.")
    print(f"Seed file: {SEED_FILE} ({len(existing)} total entries)")
    print("\nNext steps:")
    print("  git add web/seed_reports.json && git commit -m 'seed: add SEO report seeds'")
    print("  git push  # Render redeploys, sitemap gains URLs immediately")


if __name__ == "__main__":
    main()
